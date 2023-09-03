import pandas as pd
from tabulate import tabulate
from .functions import read_system_date, get_bought_ids, clear_console, validate_dates, date_to_string
from .const import BOUGHT_CSV, logo, SOLD_CSV, set_export_data
from datetime import timedelta
from .config import ui_sounds, statement_printer
import sys

def compare_dates(start_date, end_date):
    """Exits when an invalid date interval is given. 
    """
    if start_date > end_date:
        clear_console()
        sys.exit(f'Error: The end date ({date_to_string(end_date)}) must be greater than, or equal to the start date ({date_to_string(start_date)}).\n')


def get_inventory_report(option:str='today', date=None, export:bool=None, product:str=None, file_type:str=None):
    """Helper function for making the inventory report on the right date. 
    It calculates the right date based on the current system date and passes the on to the make_inventory_table() function
    """
    now = read_system_date()
    if date:
        return make_inventory_table(date, export=export, product=product, file_type=file_type)
    validate_dates()
    if option.lower() == 'yesterday':
        yesterday = now - timedelta(1)
        return make_inventory_table(yesterday, export=export, product=product, file_type=file_type)
    return make_inventory_table(now, export=export, product=product, file_type=file_type)


def make_inventory_table(date, export:bool=None, product:str=None, file_type:str=None):
    """Prints the inventory details from the given date as pivot table. When a product name is passed
    as argument a table with details about the given product will be printed. If the product wasn't in stock the table will be empty. 
    Optionally the data will be exported. By default as csv. The file type can be set by using the file_type argument.  
    """
    clear_console()
    logo()
    index_list = get_bought_ids(date) # get all ids sold before or on the given date
    df = pd.read_csv(BOUGHT_CSV) 

    # assigning datetime datatype to columns
    df['buy_date'] = pd.to_datetime(df['buy_date']).dt.date 
    df['expiration_date'] = pd.to_datetime(df['expiration_date']).dt.date 
    
    df = df[~df['id'].isin(index_list)] # leave out items from index_list (the sold items)
    df = df[(df['expiration_date']>= date)] # expiration date greater or equal to given date
    df = df[(df['buy_date']<= date)] # buy date smaller or equal to given date

    df = df.drop('id', axis=1) # remove id column from report

    if export:
        filename = set_export_data(name='inventory', date=date, format=file_type)
        if file_type == 'xlsx':
            df.to_excel(filename, index=False)
        else:    
            df.to_csv(filename, index=False)

    # new dataframe to display details per product
    if product:
        product_table = df[(df['product_name'] == product.lower())]
        product_table = product_table.rename(columns={
            'product_name': 'Product name',
            'buy_date': 'Buy date',
            'price': 'Buy price',
            'expiration_date': 'Expiration date'
        })
        product_table = product_table.sort_values(by=['Buy date'])
        print(f'\nInventory on {date} for product {product}:') 
        print(tabulate(product_table, headers='keys', tablefmt='psql', floatfmt='.2f', showindex=False),'\n')

    df = df.assign(new1='') # creating a new column before renaming it
    df = df.rename(columns={
        'product_name': 'Product name',
        'new1': 'Total items',
        'price': 'Total value',
    })

    # pivot table to summarize data
    summary = pd.pivot_table(
        df,
        values=['Total value','Total items'], 
        index=['Product name'],
        margins=True,
        margins_name='TOTALS',
        aggfunc={
            'Total value': 'sum',
            'Total items': 'count'
        }, 
        fill_value=0
        )

    ui_sounds('success')
    print(f'\nInventory summary on {date}:')
    print(tabulate(summary, headers='keys', tablefmt='psql', floatfmt='.2f'),'\n') # print the summary
    if export:
        statement_printer(f'===> Generated report at: {filename}', sleep=0.01)


def get_revenue_report(start_date, end_date, export:bool=None, profit:bool=None, file_type:str='csv'):
    """Prints the revenue details over the given time frame per product as a table. Optionally the data will be exported. By default as csv.
    The file type can be set by using the file_type argument.  
    At the bottom a table with the revenue per day will be printed.
    """
    compare_dates(start_date, end_date)
    if not profit:
        clear_console()
        logo()
    
    df = pd.read_csv(SOLD_CSV)
    df['sell_date'] = pd.to_datetime(df['sell_date']).dt.date 

    date_filter = (df['sell_date'] >= start_date) & (df['sell_date'] <= end_date) 
    df = df.loc[date_filter]

    # returns total revenue, amount of items and the dataframe to be used in the profit report
    if profit:
        df = df.drop(['id', 'product_name'], axis=1)
        df = df.rename(columns={
            'bought_id': 'id'
        })
        rows = df.shape[0]
        return df['sell_price'].sum(), rows, df


    df = df.drop(['bought_id', 'id'], axis=1) # remove columns from dataframe

    if export:
        date_string = date_to_string(start_date) + '-' + date_to_string(end_date)
        filename = set_export_data(name='revenue', date=date_string, format=file_type)
        if file_type == 'xlsx':
            df.to_excel(filename, index=False)
        else:    
            df.to_csv(filename, index=False)
    
    # new column and rename other columns for display purposes
    df = df.assign(new1='')
    df = df.rename(columns={
        'product_name': 'Product name',
        'new1': 'Total items',
        'sell_price': 'Revenue',
        'sell_date': 'Date'
    })

    overview = pd.pivot_table(
        df,
        values=['Revenue','Total items'], 
        index=['Product name'],
        margins=False,
        margins_name='TOTAL',
        aggfunc={
            'Revenue': 'sum',
            'Total items': 'count'
        }, 
        fill_value=0
        )
    
    # pivot table for printing revenue per day
    column_order = ['Total items', 'Revenue']
    overview = overview.reindex(column_order, axis=1)
    print(f'Revenue overview from {start_date} to {end_date}:')
    print(tabulate(overview, headers='keys', tablefmt='psql', floatfmt='.2f'))

    summary = pd.pivot_table(
        df,
        values=['Revenue'], 
        index=['Date'],
        margins=True,
        margins_name='TOTAL REVENUE',
        aggfunc={
            'Revenue': 'sum'
        }, 
        fill_value=0
        )
    ui_sounds('success')
    print(f'\n\nRevenue summary from {start_date} to {end_date}:')
    print(tabulate(summary, headers='keys', tablefmt='psql', floatfmt='.2f'),'\n')

    if export:
        statement_printer(f'===> Generated report at: {filename}', sleep=0.01)


def get_profit_report(start_date, end_date, export:bool=None, file_type:str='csv'):
    """Prints the profit details over the given time frame. The generated report gives an overview in two perspectives:
    - Profit based on total revenue minus the total costs over the given time frame
    - Profit based on the sold items only, per product

    Optionally the data will be exported. By default as csv. The file type can be set by using the file_type argument. At the bottom a table with the revenue per day will be printed.
    """
    compare_dates(start_date, end_date)
    clear_console()
    logo()
    
    df = pd.read_csv(BOUGHT_CSV)
    df_bought = df

    # assign date value to columns
    df['buy_date'] = pd.to_datetime(df['buy_date']).dt.date 

    # set date filter to given time frame
    date_filter = (df['buy_date'] >= start_date) & (df['buy_date'] <= end_date)  
    df = df.loc[date_filter]

    costs = df['price'].sum()
    revenue, items_sold, df_sold = get_revenue_report(start_date, end_date, export=False, profit=True)
    items_bought = df.shape[0]

    # data for dataframe
    data = {
        'Items bought': items_bought,
        'Items sold': [items_sold],
        'Costs': [costs],
        'Revenue': [revenue],
        'Profit': [revenue - costs],
        'Margin': [(revenue - costs)/revenue]
    }

    # setting column float format 
    fl_format = ['.0f', '.0f','.2f', '.2f', '.2f', '.2%']

    # table to display profit based on sales - costs within the given time frame
    totals = pd.DataFrame(data)
    ui_sounds('success')
    print(f'\nProfit report based on sold items vs bought items, from {start_date} to {end_date:}')
    print(tabulate(totals, headers='keys', tablefmt='psql', floatfmt=fl_format, showindex=False),'\n')
  
    # merge bought and sold data
    mrg = df_sold.merge(df_bought, on='id', how='left')

    # calculate profit and margin + round to two decimals
    mrg['profit'] = mrg['sell_price'] - mrg['price']
    mrg['profit'] = mrg['profit'].round(2)
    mrg['margin'] = mrg['profit'] / mrg['sell_price']
    mrg['margin'] = mrg['margin'].round(2)

    # export to file    
    if export:
        export_df = mrg
        export_df  = export_df.drop('id', axis=1)
        date_string = date_to_string(start_date) + '-' + date_to_string(end_date)
        filename = set_export_data(name='profit', date=date_string, format=file_type)
        if file_type == 'xlsx':
            export_df.to_excel(filename, index=False)
        else:    
            export_df.to_csv(filename, index=False)

    # create new column and rename the reporting fields
    mrg = mrg.assign(new='')
    mrg = mrg.rename(columns={
        'profit': 'Profit',
        'margin': 'Margin',
        'new': 'Items',
        'product_name': 'Product name',
        'price': 'Buy price',
        'sell_price': 'Sell price',

        })

    # create pivot table to summarize the profit based on sold items        
    overview = pd.pivot_table(
        mrg,
        values=['Items' ,'Sell price', 'Profit', 'Margin', 'Buy price'], 
        index=['Product name'],
        margins=True,
        margins_name='TOTAL',
        aggfunc={
            'Items': 'count',
            'Sell price': 'sum',
            'Profit': 'sum',
            'Margin': 'mean',
            'Buy price': 'sum'
        }, 
        fill_value=0
        )
    column_order = ['Items', 'Buy price', 'Sell price', 'Profit', 'Margin']
    overview = overview.reindex(column_order, axis=1)

    print(f'\nProfit report based on sold items only, from {start_date} to {end_date:}')
    print(tabulate(overview, headers='keys', tablefmt='psql', floatfmt=fl_format, showindex=True),'\n')

    if export:
        statement_printer(f'===> Generated report at: {filename}', sleep=0.01)