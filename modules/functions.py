import csv
from os import system
from thefuzz import process
import platform
from datetime import datetime, timedelta
from prettytable import PrettyTable
from .config import statement_printer, write_config, read_config, ui_sounds, clean_header
from .const import BOUGHT_CSV, SOLD_CSV, TODAY_TXT, BOUGHT_HEADER, SOLD_HEADER, GROCERY_NAMES, write_csv, write_date, get_today, logo


def clear_console():
    """Checks operating platform and clears console window. 
    """
    plt = platform.system()
    if plt == "Windows":
        system('cls')
    else: 
        system("printf '\\33c\\e[3J'")


def string_to_date(date:str):
    """Converts string to datetime object. Input format: YYYY-MM-DD
    """
    try: 
        return datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError as err:
        print(f'The following error has occurred:', err)


def date_to_string(date:datetime):
    """Converts datetime object to string formatted as YYYY-MM-DD
    """
    try: 
        return date.strftime('%Y-%m-%d')
    except ValueError as err:
        print(f'The following error has occurred:', err)


def read_system_date():
     """Reads the current 'system' date from today.txt and returns data as datetime object in the following format: yyyy-mm-dd
     """
     with open(TODAY_TXT, 'r') as file:
          fetched_date = file.readline()
          return string_to_date(fetched_date)


def reset_date(silent:bool=True):
    """Resets system date and replaces it with the current date (today) in the today.txt file. The advance time key in the settings
    will be set to False.
    """
    today = get_today()
    write_date(TODAY_TXT, today)
    write_config(adv_time=False)
    if not silent:
        clear_console()
        logo()
        statement_printer(f'The date has been reset to {today}.', sound='success')


def validate_dates():
    """Function that compares the system date with the actual date. When different the user is asked for input, to either proceed with 
    the current settings, or reset the date. 
    """
    if read_config()['enable_date_alert']:
        today = string_to_date(get_today())
        system_date = read_system_date()
        if today != system_date:
            clear_console()
            statement_printer(f'\nWarning! The system date is unequal to the current date.\n===> System date: {system_date}.\n===> Current date: {today}.\n', sound='warning', sleep=0.009)
            # nested function to ask for keyboard input / confirmation
            def input_validator():
                check = str(input('Enter Y to continue or R to reset the date to the current date.\n'))
                try: 
                    if check[0].lower() == 'y':
                        return
                    elif check[0].lower() == 'r':
                        return reset_date()
                    statement_printer('Invalid input.', sound='error')
                    return input_validator()
                except Exception as err:
                    statement_printer(f'The following error has occurred: {err}', sound='error')
                    return input_validator()
            input_validator()


def advance_time(days:int):
    """Shifts the system date with the amount of days that are passed as argument and sets the 'advance_time' parameter 
    in the settings file to True 
    """
    current_date = read_system_date()
    adv_date = current_date + timedelta(days)
    new_date = date_to_string(adv_date)
    write_date(TODAY_TXT, new_date)
    write_config(adv_time=True)
    clear_console()
    logo()
    statement_printer(f'The date is now set to {read_system_date()}.\n', sound='success')


def check_advance_time():
    """Reads the current configuration and sets the date to today when advance_time is disabled, to make sure the system date is equal to the current date
    """
    if not read_config()['enable_advance_time']:
        reset_date()


def get_grocery_list()-> list:
    """Returns all known unique product names as a list. Reads both the bought.csv and groceries.csv files
    """
    groceries = set() # a set is used instead of a list since iterating over a set proved to be about 10x faster, also no concerns about dupes
    with open(BOUGHT_CSV, 'r') as file_1:
        with open(GROCERY_NAMES, 'r') as file_2:
            reader_1 = csv.DictReader(file_1, delimiter=',')
            reader_2 = csv.reader(file_2, delimiter=',')
            for row in reader_1:
                if row['product_name'] not in groceries:
                    groceries.add(row['product_name'])  
            for row in reader_2:
                if row[0] not in groceries:
                    groceries.add(row[0])               
    return list(groceries)


def check_product_names(word:str):
    """Validator function that checks the given string and compares it with existing strings in groceries.csv and bought.csv. The list of strings
    is collected via get_grocery_list(). The process module from thefuzz compares the given string with those in the list from get_grocery_list(). 
    When no exact match is found, user input is asked via product_name_validator()
    """
    original_word = word.lower()
    if read_config()['validate_names']:
        groceries = get_grocery_list()
        checked_word = str(process.extract(original_word, groceries, limit=1)[0][0]).lower()
        if original_word != checked_word:
            return product_name_validator(original_word, checked_word)
    return original_word
    

def product_name_validator(original_word:str, checked_word:str):
    """Ask for user input when no exactly matching product was found. The user can decide to go ahead with the entered product name or choose the suggested product name
    """
    ui_sounds('info')
    check = str(input(f'Did you mean {checked_word}? (Y/n)\n'))
    try: 
        if not check:
            return product_name_validator(original_word, checked_word)
        if check[0].lower() == 'y':
            return checked_word
        if check[0].lower() == 'n':
            return original_word
        return product_name_validator(original_word, checked_word)
    except Exception as e:
        print(f'The following has occurred: {e}')
        return product_name_validator(original_word, checked_word)


def buy_product(product_name:str, price:float, expiration_date):
    """Adds a product (in lowercase) to the bought.csv file by:
    - validating the product name
    - generating a buy id
    - putting all values in a list
    After writing to the csv file a table with details from the last added row will be printed
    """
    validate_dates()
    validated_name = check_product_names(product_name)
    buy_id = generate_id(BOUGHT_CSV)
    data = [buy_id, validated_name.lower(), read_system_date(), price, expiration_date]
    write_csv(BOUGHT_CSV, data)
    table, table_csv = table_printer(BOUGHT_HEADER, get_last_line(BOUGHT_CSV))
    clear_console()
    logo()
    statement_printer('===> The following item has successfully been added to the database:', sleep=0.009, sound='success')
    print(table,'\n')


def generate_id(datafile):
    """Gets the last row number from the given file and adds 1, so the value can be used as ID and makes sure the ID is equal to the row number
    """
    with open (datafile, 'r') as file:
        count = sum(1 for _ in file)
        return count +1


def get_last_line(inputfile)-> list:
    """Fetching the last line from the provided CSV file and returns the values as list of lists. This data is used for printing
    a table after adding a line to the given file
    """ 
    with open(inputfile, 'r') as file:
        last_line = file.readlines()[-1].strip()
        return [last_line.split(',')]


def table_printer(header:dict, rows:list):
    """Prints a table with a header and the last row from the csv file to be shown as confirmation after buying or selling a product
    """
    clear_console()
    c_header = clean_header(header)
    x = PrettyTable()
    x.field_names = c_header.keys()
    for k, v in c_header.items():
        x.align[k] = v
    for r in rows:
        x.add_row(r)
    table = x.get_string(fields=[x for x in c_header.keys() if not x.lower().endswith('id')]) # don't print 'id' columns
    table_csv = x.get_csv_string # return format that can be saved as csv file, currently unused since pandas takes care of the export
    return table, table_csv


def read_csv_dict(csv_file)-> dict:
    """Reads a csv file and returns an iterable dictionary. The value is casted into a list to prevent I/O errors
    """
    with open(csv_file) as file:
        reader = csv.DictReader(file)
        return list(reader)


def check_bought_items(product:str, id:list)-> dict:
    """Checks the bought.csv file and returns a row when
    - the given product exits in bought.csv
    - the row id is not already in the sold.csv (bought id)
    - the buy dat is smaller or equal to the system date
    _ the expiration date is greater then, or equal to the system date
    When a product is unavailable a message will be printed
    """
    system_date = read_system_date()
    csv_data = read_csv_dict(BOUGHT_CSV)
    for row in csv_data:
        if product.lower() == row['product_name'].lower() and row['id'] not in id and string_to_date(row['buy_date']) <= system_date and string_to_date(row['expiration_date']) >= system_date:
            return row
    if product.lower() == 'soup':
        statement_printer('No soup for you! NEXT!!', space=1, h_space=True, sound='warning') # couldn't resist a Seinfeld reference
        return 
    statement_printer(f'Product {product} is not available at this moment', sound='error')
    return 


def sell_product(name:str, price:float):
    """Function for checking if a product name is valid and the product is available for sale. Calls the store function when the item is available
    """
    validated_name = check_product_names(name)
    available_item = check_bought_items(validated_name, get_bought_ids())
    if available_item:
        store_sold_item(available_item['id'], validated_name, price)


# return all bought ids from the sold.csv file as list, with optional date argument to filter by date
def get_bought_ids(date:datetime=None)-> list:
    """Reads the sold.csv file and returns all bougt id's as a list. When a date is passed only bought id's smaller or equal to the given 
    date will be added to the list. This is important for generating inventory reports. 
    """
    csv_data = read_csv_dict(SOLD_CSV)
    bought_id_list = []
    if not date: 
        for row in csv_data:
            bought_id_list.append(row['bought_id'])
        return bought_id_list
    for row in csv_data:
        if string_to_date(row['sell_date']) <= date: 
            bought_id_list.append(int(row['bought_id']))
    return bought_id_list


def store_sold_item(bought_id:int, product_name:str, sell_price:float):
    """Writes the sold item to the sold.csv file after:
    - checking and validating the system date
    - generating an id
    - putting all row items in a list
    After updating the csv file a table containing data from the last row from that file will be printed. 
    """
    validate_dates()
    sell_id = generate_id(SOLD_CSV)
    data = [sell_id, bought_id, product_name.lower(), read_system_date(), sell_price]
    write_csv(SOLD_CSV, data)
    table, table_csv = table_printer(SOLD_HEADER, get_last_line(SOLD_CSV))
    clear_console()
    logo()
    statement_printer('===> The following item has successfully been registered as a sale:', sleep=0.009, sound='success')
    print(table,'\n')
