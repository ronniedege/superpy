import argparse
from .functions import get_today, read_system_date, string_to_date, date_to_string
from .config import ui_sounds
from datetime import  datetime
import re
from chime import themes

#  -> https://docs.python.org/3/library/argparse.html#type
def validate_date(date):
    """Argument date validator. Verifies that the date is specified as YYYY-MM-DD and is a valid date. 
    An error is raised when an invalid date was provided. 
    """
    try:
        return datetime.fromisoformat(date).date()
    except ValueError as err:
        if 'isoformat' in str(err).lower():
                err_message =  f'{err}. The date should be formatted as: YYYY-MM-DD'
        else: err_message = err
        ui_sounds('error')
        raise argparse.ArgumentTypeError(err_message)
    
def validate_expiration_date(date):
    """Expiration date validator. Compares the given date with the system date and raises an error when the given date is smaller
    or equal to the given date. 
    """
    validate_date(date)
    system_date = read_system_date()
    if string_to_date(date) <= system_date:
        ui_sounds('error')
        msg = f'The expiration date should be greater then the current system date ({date_to_string(system_date)})'
        raise argparse.ArgumentTypeError(msg)
    return date


# amount of days should be type int and greater then 0
def validate_adv_time(days):
    """Validator for the advance_time option. The data type must be int and the value must be greater than 0. 
    """
    try:
        if int(days) > 0:
            return int(days)
        ui_sounds('error')
        raise argparse.ArgumentTypeError('The amount of days should be greater than 0.')
    except ValueError:
        ui_sounds('error')
        raise argparse.ArgumentTypeError(f'Invalid data type -> "{days}". Type should be int.')
    

# regex validation to check if the sting contains alphanumeric characters. Spaces and dashes are also accepted
def validate_product_name(name:str):
    """Regex validation for the product name. Raises an error when an invalid character is used. 
    """
    if re.match('^[a-zA-Z0-9-&\s]*$', name):
        return name
    else:
        raise argparse.ArgumentTypeError(f'Product name {name} is invalid. The string must only contain alphanumeric characters. Spaces and dashes and ampersands are allowed')

def init_parser():
    """Creates all parsers, subparsers and arguments. Extensive help is included. 
    """
    # create parser instance
    parser = argparse.ArgumentParser(
        prog='python3 super.py', 
        description='A command-line tool for tracking supermarket inventory', 
        prefix_chars='--'
        )
    
    subparser = parser.add_subparsers(dest='command')

    #advance time
    advance_time = subparser.add_parser('advance_time', help='Function to advance time in a number of days.')
    advance_time.add_argument(
        '--days',
        type=validate_adv_time, 
        required=True, 
        help='Enter the number of days to advance as integer.'
        )

    # reset advance time
    reset = subparser.add_parser('reset', help=f'Resets the date. Use the --date argument.')
    reset.add_argument(
        '--date',
        default=False,
        action='store_true',
        help=f'Resets the date to {get_today()}.'
        )
    
    # configuration
    config = subparser.add_parser('config', help='Change the application configuration. Enter config --show to display the current configuration')
    config.add_argument(
        '--show',
        action='store_true',
        dest='show',
        help='Shows the current app configuration'
    )
    config = config.add_subparsers(dest='config', title='Change the application configuration. The following options are available')

    #sound options
    sound = config.add_parser(
        'sound',
        help=f"""Sets the sound options. When enabled the application will give audiovisual feedback when actions are performed or exceptions are encountered.
        Use --enable or --disable to turn it on or off. The --theme flag is used to set the sound theme. Available themes:{themes()}""",
        argument_default=None)
    sound = sound.add_mutually_exclusive_group(required=True)
    sound.add_argument(
        '--enable',
        action='store_true',
        dest='sound',
        help='Enables sound',)
    sound.add_argument(
        '--disable',
        action='store_false',
        dest='sound',
        help='Disables sound')
    sound.add_argument(
        '--theme',
        default='material',
        nargs=None,
        choices=themes(),
        dest='sound',
        help='Pick one of the available themes to set the sound theme'
    )
    
    # statement printer options
    printer = config.add_parser(
        'printer', 
        help='Sets the printer option. When enabled statements in the terminal will be printed character by character. Use --enable or --disable to turn it on or off',)
    printer = printer.add_mutually_exclusive_group(required=True)
    printer.add_argument(
        '--enable',
        action='store_true',
        dest='printer',
        help='Enables the printing of statements character by character',)
    printer.add_argument(
        '--disable',
        action='store_false',
        dest='printer',
        help='Disables the printing of statements character by character')
    

    # date alert options
    alert = config.add_parser(
        'alert', 
        help='If enabled this option shows a message when the system date is unequal to the current date and asks for user input to either confirm to proceed or reset the date to the current date',)
    alert = alert.add_mutually_exclusive_group(required=True)
    alert.add_argument(
        '--enable',
        action='store_true',
        dest='date_alert',
        help='Enables the alert message',)
    alert.add_argument(
        '--disable',
        action='store_false',
        dest='date_alert',
        help='Disables the alert message')
    

    # product names validation options
    validate = config.add_parser(
        'validate', 
        help="""If enabled this option will validate the product names that are passed via the buy or sell commands. This validation helps to prevent typos or double entries.
        If the given product name doesn't exactly match with a value from the names database a suggested product name is printed. The user will be asked for input to
        either use the alternative name or to proceed with the name entered. """
        ,)
    validate = validate.add_mutually_exclusive_group(required=True)
    validate.add_argument(
        '--enable',
        action='store_true',
        dest='validate',
        help='Enables the product name validation',)
    validate.add_argument(
        '--disable',
        action='store_false',
        dest='validate',
        help='Disables the product name validation')
    

    # test data generator
    testdata = subparser.add_parser('testdata', help='Generates a bought.csv and sold.csv file that can be used for test purposes. Each run the previously generated test files will be overwritten')
    testdata.add_argument(
        '--startdate', 
        required=True, 
        type=validate_date,
        metavar='YYYY-MM-DD',
        help='Enter the preferred start date of the buying of items')
    testdata.add_argument(
        '--rows', 
        type=int, 
        required=True, 
        help='Enter the amount of rows the bought.csv file should have')
    testdata.add_argument(
        '--items', 
        type=int, 
        required=True, 
        help='Enter the amount of unique items (products) the files should contain')
    

    # buy products
    buy = subparser.add_parser('buy', help='Function to register bought products.')
    buy.add_argument(
        '--product_name',
        type=validate_product_name, 
        required=True, 
        help='Enter the name of the product. Use double quotes between strings containing spaces')
    buy.add_argument(
        '--price', 
        type=float, 
        required=True, 
        help='Enter the price of the product as float.')
    buy.add_argument(
        '--expiration_date', 
        type=validate_expiration_date,
        required=True,
        metavar='YYYY-MM-DD', 
        help='Enter the expiration date in the following format: YYYY-MM-DD.')

    # sell products
    sell = subparser.add_parser('sell', help='Function to register sold products.')
    sell.add_argument(
        '--product_name', 
        type =validate_product_name, 
        required=True, 
        help='Enter the name of the product.')
    sell.add_argument(
        '--price', 
        type=float, 
        required=True, 
        help='Enter the selling price of the product as float.')

    # reporting
    report = subparser.add_parser('report', help='Generate reports')
    report = report.add_subparsers(dest='report', title='report types')

    # inventory report
    inventory = report.add_parser(
        'inventory', 
        help='Generates an inventory report for the date on the given argument. Use one of the mandatory arguments (--now | --yesterday | --date DATE)',)
    inventory.add_argument(
        '--export',
        required=False,
        action='store_true',
        help='Exports the report data to a csv file. No calculating or aggregating will be done. The report contains all items within the given date')
    inventory.add_argument(
        '--product',
        required=False,
        type = validate_product_name,
        help='Optional product filter. Enter a product name to get details about the product. Without this parameter an aggregated overview will be created')
    inventory.add_argument(
        '--type',
        required=False,
        nargs='?',
        default='csv',
        choices=['csv', 'xlsx'],
        help='Sets the output file type of the export file. Default is CSV')
    inventory = inventory.add_mutually_exclusive_group(required=True)
    inventory.add_argument(
        '--now', 
        action='store_true', 
        help=f'Generates an inventory report for today where today is the current system date ({read_system_date()})')
    inventory.add_argument(
        '--yesterday', 
        action='store_true', 
        help=f'Generates an inventory report for yesterday, relative to the current system date ({read_system_date()})')
    inventory.add_argument(
        '--date',  
        type=validate_date,
        metavar='YYYY-MM-DD', 
        help='Enter a date in the following format: YYYY-MM-DD to get the inventory on that day. The current system date will be ignored')
    
    # reventue reporting
    revenue = report.add_parser(
        'revenue',
        help='Get a detailed report of the revenue over a given period of time'
    )
    revenue.add_argument(
        '--start',
        type=validate_date,
        required=True,
        metavar='YYYY-MM-DD', 
        help='Enter the start date of the report as: YYYY-MM-DD.')
    revenue.add_argument(
        '--end',
        type=validate_date,
        required=True,
        metavar='YYYY-MM-DD', 
        help='Enter the end date of the report as: YYYY-MM-DD.')
    revenue.add_argument(
        '--export',
        required=False,
        action='store_true',
        help='Exports the report data to a csv file. No calculating or aggregating will be done. The report contains all items within the given time frame')
    revenue.add_argument(
        '--type',
        required=False,
        nargs='?',
        default='csv',
        choices=['csv', 'xlsx'],
        help='Sets the output file type of the export file. Default is CSV')


    # profit reporting
    profit = report.add_parser(
        'profit',
        help='Get the profit details over a given time frame in two perspectives: 1) based on total spend vs revenue, 2) based on items sold'
    )
    profit.add_argument(
        '--start',
        type=validate_date,
        required=True,
        metavar='YYYY-MM-DD', 
        help='Enter the start date of the report as: YYYY-MM-DD.')
    profit.add_argument(
        '--end',
        type=validate_date,
        required=True,
        metavar='YYYY-MM-DD', 
        help='Enter the end date of the report as: YYYY-MM-DD.')
    profit.add_argument(
        '--export',
        required=False,
        action='store_true',
        help='Exports the profit report data to a csv file without grouping first. ')
    profit.add_argument(
        '--type',
        required=False,
        nargs='?',
        default='csv',
        choices=['csv', 'xlsx'],
        help='Sets the output file type of the export file. Default is CSV')


    return parser.parse_args()
