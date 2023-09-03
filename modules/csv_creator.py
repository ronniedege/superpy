"""This module generates dummy CSV files that can be used for testing the super.py app. 

Source dataset: https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset?resource=download

The original dataset has been modified and merged with several other datasets

The dataset can be downloaded from the source: https://raw.githubusercontent.com/ronniebax/static/main/data/groceries.csv
"""

import random
from random import shuffle
import csv
from datetime import timedelta
import os
from .functions import string_to_date, clear_console, read_system_date, get_today
from .const import GROCERY_NAMES, check_data_files, BOUGHT_HEADER, SOLD_HEADER, logo


DATA_DIR = 'modules/csv_data_test'
CSV_BOUGHT = 'modules/csv_data_test/bought.csv'
CSV_SOLD = 'modules/csv_data_test/sold.csv'


def check_data_dir():
    """Checks if data directory exists and creates this directory if not. 
    """
    if not os.path.exists(DATA_DIR):
        try: 
            os.makedirs(DATA_DIR)
            print(f'Created data directory.')
        except Exception as e:
            print(f'The following error has occurred: {e}.')


def generate_dates(date)-> list:
    """Function for generating dates. This function takes only one argument (date) and returns a list of dates based on the given argument. 
    The amount of generated dates is based on the difference in days between the given date and the current date (the time delta). 

    Parameters:
    -----------
    date: str, the date as YYYY-MM-DD
    """
    if type(date) == str:
        start_date = string_to_date(date)
    else:    
        start_date = date
    today = read_system_date()
    if start_date >= today:
        start_date = today - timedelta(15)
    interval = today - start_date
    dates = []
    new_date = start_date
    while len(dates) < interval.days:
        new_date += timedelta(1)
        dates.append(new_date)
    return dates

def random_date(date:list):
    """Returns a random date from a list that contains several dates
    """
    return random.choice(date)

def random_price()-> float:
    """Returns a random float between 0.5 and 15 with 2 decimal positions that acts in this context as product price
    """
    return round(random.uniform(0.5, 10), 2)

def random_exp_date(buy_date):
    """Takes a datetime object - buy_date - (yyyy-mm-dd) and adds a number of random days to it, in range 10-100

    returns
    -------
    Returns an expiration date as datetime object (yyyy-mm-dd)
    """
    new_date = buy_date + timedelta(random.uniform(10, 100))
    return new_date


def set_sell_price(buy_price:float):
    """Takes the buy price and calculates the sell price randomly. The margin varies between 1.5 and 2.5 to
    make sure the result of the profit calculation will be different. 
    """
    sell_price = buy_price * round(random.uniform(1.4, 2.5), 2)
    return round(sell_price, 2)

def grocery_names(items:int=None)-> list:
    """Returns the grocery items from the given csv file as list containing unique items

    Parameters
    ----------
    items: int, optional
        Provide the amount of unique items in the list. When a value is passed the list will be shuffled
    """
    check_data_files()
    with open(GROCERY_NAMES, 'r') as g_file:
        reader = csv.reader(g_file)
        data = set()
        for row in reader:
            data.add(row[0])
    grocery_list = list(data)        
    if items != None:
        shuffle(grocery_list)        
        if len(grocery_list) <= items:
            return grocery_list
        else:
            return grocery_list[:items]
    return grocery_list
  
def generate_csv(start_date, csv_rows:int=500, items:int=None):
    """Generates the bought.csv file.
    Pass the amount of desired rows as argument. After generating the bought.csv file the generate_csv_sold() function is called for generating the sold.csv file

    Parameters
    ----------
    start_date: str
        pass the start date as string (yyyy-mm-dd)
    csv_rows: int, defaults at 500
    items: int, optional
        the amount of unique values
    """ 
    clear_console()
    logo()
    check_data_dir()
    if items < 10:
        items = 10
    header = BOUGHT_HEADER.keys()
    ids = 1
    with open(CSV_BOUGHT, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(header)
        counter = 0
        groceries = grocery_names(items)
        buy_dates = generate_dates(start_date)
        for x in range(csv_rows):
            grocery = random.choice(groceries) # picks a random item from the groceries list with each iteration
            ids += 1
            counter += 1
            buy_date = random_date(buy_dates)
            exp_date = random_exp_date(buy_date)
            writer.writerow([ids, grocery, buy_date, random_price(), exp_date])
    clear_console()
    print(f'===> Generated bought file with {counter} rows at: {CSV_BOUGHT}')  
    generate_csv_sold(buy_dates, csv_rows) 


def generate_csv_sold(date, rows):
    """Reads the bought.csv file and iterates through it. 
    A new row is written to sold.csv when the sell date is greater than the buying date,
    and the expiration date is greater than the sell date. The bought.csv will be iterated until the
    amount of rows reaches 88% of the amount of rows in bought.csv. 
    """
    header = SOLD_HEADER.keys()
    ids = 1
    with open(CSV_SOLD, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(header)
        counter = 0
        x = 0
        output_amount = rows * 0.88 # 88% of the bought items are sold
        today = string_to_date(get_today())
        while x < 5: # while loop for iterating trough file multiple times. Capped at 5 times to prevent endless loops
            with open(CSV_BOUGHT) as bought_file:
                reader = csv.DictReader(bought_file)
                for row in reader:
                    sell_date = random_date(date) + timedelta(random.uniform(1,10)) # an extra layer of randomness 
                    buy_date = string_to_date(row['buy_date'])
                    bought_id = row['id']
                    expiration_date = string_to_date(row['expiration_date'])
                    if buy_date <= sell_date and expiration_date > sell_date and sell_date <= today:
                        ids += 1
                        counter += 1
                        writer.writerow([ids, bought_id, row['product_name'], sell_date, set_sell_price(float(row['price']))])
                        if counter >= output_amount:
                            break # break when desired amount of sold items is reached. 
            x += 1       
    print(f'===> Generated sold file with {counter} rows at: {CSV_SOLD}.') 