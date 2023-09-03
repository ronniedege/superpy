# SuperPy highlights

 - Product name validation via thefuzz
 - Pivoting data by using pandas
 - Customize app via settings

## Product name validation

For proper reporting, all products in the database should be unique. Because SuperPy uses the product name as the key value (instead of a product ID), I had to come up with a solution to avoid typos and situations where both *apple* and *apples* can exist next to each other.  That's where python package [*thefuzz*](https://pypi.org/project/thefuzz/) comes in. This package uses the Levenshtein distance algorithm with the option to find the similarity between two strings. 

To make this work, I first created a grocery database (groceries.csv) with a decent amount of unique grocery names. I then implemented *thefuzz*'s *process* module to compare the entered product name with the items in the grocery database and previously bought items, if the entered product name doesn't already exists in both files. In that case, *thefuzz* will return the most similar string and the user is asked for input to either use the suggested name or to proceed with the entered name. 

Example:
```bash
python3 super.py buy --product_name grape --price 3.99 --expiration_date 2023-12-30
```

```bash
Did you mean grapes? (Y/n)
```

To prevent case issues all names are converted to lower case everywhere.


## Pivoting data

Working on the app, I implemented the [*prettytable*](https://pypi.org/project/prettytable/) package for printing bought and sold data in a table. This package does a good job for display purposes, but later, when I worked on the reporting functions, it was difficult to group data properly

To group data and perform quick calculations, I often use pivot tables in Excel. Pivot tables are ideal for the reporting usecase in the SuperPy app. Not wanting to reinvent the wheel, I searched the internet for a way to use pivot tables in Python.  I soon found out that using dataframes, via the *pandas* package, is the best way to achieve this, so I implemented *pandas* in the app.

I found *pandas* not very intuitive and it took me a while to understand the syntax, but eventually I got everything working the way I wanted it to. As a bonus, *pandas* has powerful export options that I used to add functionality for exporting reporting data to csv and Excel files. The latter by adding the *openpyxl* package. 

Now I'm sure all calculations are performed correctly and the right values are in the reports.

## Customize app

I came up with the idea of making some app settings customisable to solve a problem with the `advance_time` function. The app's *system date* is stored in a txt file and the app uses this date as the current date for all date-related functions. Somehow, the app needs to know whether `advance_time` is enabled or not to ensure that the *system date* can be set to *today* when `advance_time` is disabled. Otherwise, the *system date* remains the same until it is manually set to *date* using the `reset` command. 

To achieve this, I created a settings file in json format to store the current `advance_time` setting (`true` or `false`). Each time operations in the app are performed, the settings file is read to ensure the correct action is performed. I chose a json file because it uses key-value pairs and can be read as a Python dictionary using the *json* module. 

Later, I implemented some other options, such as an audio feature to provide audio-visual feedback when operations are performed and alerts are given. I used the [*chime*](https://pypi.org/project/chime/) package to make this possible. 

## Worth mentioning

To test the app's functions and ensure the reports are accurate, data in both bought.csv and sold.csv is needed. The more data available, the better testing works. To avoid having to manually use the `buy` command dozens of times to generate buy data and the same for the `sell` command, I created a module (csv_creator) to generate a bought.csv and sold.csv file that can contain thousands of lines of accurate data. The function in this module takes three arguments:

- startdate
- rows
- items

With some help of the *random* module every time the function is called, different files are generated. 
