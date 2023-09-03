# module for storing the apps config related functions
import chime
import time
import json
from .const import SETTINGS
from prettytable import PrettyTable


def statement_printer(statement, space:int=0, sleep:float=0.02, h_space:bool=False, sound:str=None):
    """Creates a typewriter effect. This function can be disabled in the app settings

    Parameters:
    -----------
    statement: str, text to print
    space: int -> space between characters. Default = 0
    sleep: float -> time between each character, default = 0.02
    h_space: bool -> enable horizontal space, default = False
    sound: str -> theme from ui_sounds
    """
    spaces = (space * ' ')
    if sound != None:
        ui_sounds(sound)
    if read_config()['printer']:
        if h_space:
            print('')
        for letter in statement:
            print(letter, end=spaces, flush=True)
            time.sleep(sleep)
        print('\n')
    else: print(statement)


def ui_sounds(message_type:str):
    """When this option is enabled in the configuration a sound will be played to alert the user.
    
    Parameters
    ----------
    message_type: str
        one of the follwing strings have to be passed as arguments
        - info
        - warning
        - error
        - success
    """
    config = read_config()
    chime.theme(config['sound_theme'])
    if config['sound']:
        if message_type == 'info':
            chime.info()
        elif message_type == 'warning':
            chime.warning()
        elif message_type == 'error':
            chime.error()
        elif message_type == 'success':
            chime.success()


def read_config()-> dict:
    """Reads the settings.json file and returns the items as dictionary
    """
    with open(SETTINGS, 'r') as json_file:
        return json.load(json_file)
    

def write_config(sound:bool=None, printer:bool=None, sound_theme:str=None, adv_time:bool=None, date_alert:bool=None, validate_names:bool=None):
    def save_config():
        with open(SETTINGS, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    data = read_config()
    if printer != None:
        data['printer'] = printer
        save_config()
        statement_printer(f'The printer value is set to {printer}.')
    if sound != None:
        data['sound'] = sound
        save_config()
        statement_printer(f'The sound value is set to {sound}.')
        if sound:
            ui_sounds('success')
    if sound_theme != None:
        if sound_theme.lower() in chime.themes():
            data['sound_theme'] = sound_theme.lower()
            statement_printer(f'The sound theme is set to {sound_theme}.')
        else: 
            data['sound_theme'] = 'material'
            statement_printer(f'The option {sound_theme.lower()} is not available. The theme is now set to the default value: material.')
        save_config()
        if data['sound'] == True:
            ui_sounds('success')
        else:
            statement_printer('Sound is currently disabled. Use config sound --enable to turn on sound')
    if adv_time != None:
        data['enable_advance_time'] = adv_time
        save_config()
    if date_alert != None:
        data['enable_date_alert'] = date_alert
        save_config()
        statement_printer(f'The date alert value is set to {read_config()["enable_date_alert"]}.', sound='success')
    if validate_names != None:
        data['validate_names'] = validate_names
        save_config()
        statement_printer(f'The name validation function is set to {read_config()["validate_names"]}.', sound='success')


# takes the header dictonary, removes underscores and adds captions.
def clean_header(header:dict)-> dict:
    """Takes a dictionary and converts the keys:
    - replacing '_' by a space
    - Capitalizing the strings\n
    Usage: printing headers for the prettytable tables
    """
    data = tuple(header.items()) #convert to tuple for preserving order
    return dict((k.replace('_', ' ').capitalize(), v) for k, v in data)


def display_config():
    """Prints the keys and values from settings.json as a table. The advance time value is left out, since this option is a funtion by itself
    and no part of te config options. 
    """
    current_config = read_config()
    x = PrettyTable()
    x.field_names = clean_header(current_config)
    x.add_row(current_config.values())
    print('\nCurrent configuration:')
    print(x.get_string(fields=[c for c in x.field_names if 'advance' not in c.lower()]),'\n')