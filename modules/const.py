import os, json, csv, sys, time, requests, urllib3
from datetime import date
from time import sleep
import platform
from os import system

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable warning when working with local certificate

DATA_DIR = os.path.join(os.getcwd(), 'data') # directory for storing data files
BOUGHT_CSV = os.path.join(DATA_DIR, 'bought.csv') # csv file for storing bought products
SOLD_CSV = os.path.join(DATA_DIR, 'sold.csv') # csv file for storing sold products
TODAY_TXT = os.path.join(DATA_DIR, 'today.txt') # txt file for storing the program's current date
SETTINGS = os.path.join(DATA_DIR, 'settings.json') # json file for storing the app settings
GROCERY_NAMES = os.path.join(DATA_DIR, 'groceries.csv')
LOGO = os.path.join(DATA_DIR, 'logo.txt')
GROCERY_URL = 'https://raw.githubusercontent.com/ronniebax/static/main/data/groceries.csv'
EXPORT_DIR = os.path.join(os.getcwd(), 'export')


 # The header for the bought.csv file as dict with align parameter (l/r) as values to be used to set the alignment for the prettytable function
BOUGHT_HEADER = {
    'id': 'l',
    'product_name': 'l',
    'buy_date': 'r',
    'price': 'r',
    'expiration_date': 'r'
    }


 # the header for the sold.csv file as dict with align parameter (l/r) as values
SOLD_HEADER = {
    'id': 'l',
    'bought_id': 'l',
    'product_name': 'l',
    'sell_date': 'r',
    'sell_price': 'r'
    } 


# initial configuration parameters for the json settings file
CONFIG_DATA = {
    "sound": True,
    "sound_theme": "material",
    "printer": True,
    "enable_advance_time": False,
    "enable_date_alert": True,
    "validate_names": True

}


def get_today():
    """Gets the current date and returns it as a string
    """
    return date.today().strftime('%Y-%m-%d')


def write_csv(csv_file, data):
    """Writes the provided data to the given csv file
    """
    try:
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(data)
    except Exception as e:
        print(f'The following error has occurred: {e}.') 
        sys.exit(1)


def write_date(txt_file, date):
    """Writes the given date to today.txt
    """
    try:
        with open(txt_file, 'w') as file:
            file.write(date)
    except Exception as e:
        print(f'The following error has occurred: {e}.')
        sys.exit(1)


def check_data_files():
    """Checks if data directory and data files exist and create them if not present
    """
    if not os.path.exists(DATA_DIR):
        try: 
            os.makedirs(DATA_DIR)
            print(f'Created data directory.')
        except Exception as e:
            print(f'The following error has occurred: {e}.')

    if not os.path.exists(BOUGHT_CSV):
        write_csv(BOUGHT_CSV, BOUGHT_HEADER.keys())
        print(f'Created {BOUGHT_CSV}.')

    if not os.path.exists(SOLD_CSV):
        write_csv(SOLD_CSV, SOLD_HEADER.keys())
        print(f'Created {SOLD_CSV}.')

    if not os.path.exists(TODAY_TXT):
        write_date(TODAY_TXT, get_today())

    # checks if json setting file is present and creates new file when not present
    if not os.path.exists(SETTINGS):
        try:
            with open(SETTINGS, 'w') as file:
                json.dump(CONFIG_DATA, file, indent=4)
                print(f'Created {SETTINGS}.')
        except Exception as e:
            print(f'The following error has occurred: {e}.')

    # checks if grocery datafile is present and downloads it when not present
    if not os.path.exists(GROCERY_NAMES):
        try:
            response = requests.get(GROCERY_URL, verify=False)
            with open(GROCERY_NAMES, 'wb') as file:
                file.write(response.content)
                print(f'Successfully downloaded and saved grocery datafile at {GROCERY_NAMES}')
        except Exception as e:
            print(f'The following error has occurred: {e}.')


def set_timestamp():
    """Creates string from epoch time and removes dots. The string can be used as unique value for naming report exports
    """
    return str(time.time()).replace('.', '')
 

def set_export_data(name, date, format):
    """- Checks if the export directory exists and creates one if not. Folder name: export
    - Generates a file name with time stamp (from epoch) to guarantee a unique name

    Parameters
    ----------
    name: str, start of the filename, example: inventory
    date: datetime object, generates a time stamp via set_timestamp()
    format: str, the file extension, example: 'csv'

    Returns
    -------
    a filename, formatted: {name}_{timestamp}_{extension}
    """
    if not os.path.exists(EXPORT_DIR):
        try: 
            os.makedirs(EXPORT_DIR)
            print(f'Created export directory: {EXPORT_DIR}')
        except Exception as e:
            print(f'The following error has occurred: {e}.')
    filename = f'{name}_{date}_{set_timestamp()}.{format}'
    return os.path.join(EXPORT_DIR, filename)

def logo(pause:bool=True):
    """Prints super.py logo from logo.txt as ascii art
    """
    with open('data/logo.txt','r') as file:
        logo = file.read()
        print(logo)
        if pause:
            sleep(1)

def clear_console():
    """Checks operating platform and clears console window. 
    """
    plt = platform.system()
    if plt == "Windows":
        system('cls')
    else: 
        system("printf '\\33c\\e[3J'")
    