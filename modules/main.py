# Imports
from .functions import advance_time, reset_date, buy_product, check_advance_time, sell_product, string_to_date, read_system_date
from .parser import init_parser
from .const import check_data_files, get_today
from .reporting import get_inventory_report, get_revenue_report, get_profit_report
from .config import write_config, display_config
from .csv_creator import generate_csv

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.

def main():
    """
    Main function that calls the right functions after an argparge command is given. 
    """

    # initialize parser
    cli = init_parser()

    # first check if data files are present and create them when not present
    check_data_files()

    # check if the advance time option has been enabled and set system date to today if not.
    check_advance_time()

    # advance time functions
    if cli.command == 'advance_time':
        advance_time(cli.days, cli.date)
    elif cli.command == 'reset':   
        if cli.date:
            today = string_to_date(get_today())
            system_date = read_system_date()
            if today != system_date:
                reset_date(silent=False)
            else:
                print(f'The system date is already set to {today}. No changes were made.')

    # app configuration / settings
    elif cli.command == 'config':
        if cli.show:
            display_config()
        elif cli.config == 'sound':
            if type(cli.sound) == bool:
                write_config(sound=cli.sound)
            else:
                write_config(sound_theme=cli.sound)    
        elif cli.config == 'printer':
            write_config(printer=cli.printer)
        elif cli.config == 'alert':
            write_config(date_alert=cli.date_alert)
        elif cli.config == 'validate':
            write_config(validate_names=cli.validate)

    # generate testdata
    elif cli.command == 'testdata':
        generate_csv(start_date=cli.startdate, csv_rows=cli.rows, items=cli.items)

    # buying
    elif cli.command == 'buy':
        buy_product(cli.product_name, cli.price, cli.expiration_date, cli.amount)

    # selling
    elif cli.command == 'sell':
        sell_product(cli.product_name, cli.price, cli.amount)

    # reporting
    elif cli.command == 'report':

        # inventory report
        if cli.report == 'inventory':
            if cli.now:
                get_inventory_report(option='today', export=cli.export, product=cli.product, file_type=cli.type)
            elif cli.yesterday:
                get_inventory_report(option='yesterday', export=cli.export, product=cli.product, file_type=cli.type)
            else:
                get_inventory_report(date=cli.date, export=cli.export, product=cli.product, file_type=cli.type)

        # revenue report 
        elif cli.report == 'revenue':
            get_revenue_report(start_date=cli.start, end_date=cli.end, export=cli.export, file_type=cli.type)

        # profit report 
        elif cli.report == 'profit':
            get_profit_report(start_date=cli.start, end_date=cli.end, export=cli.export, file_type=cli.type)    

if __name__ == "__main__":
    main()