#!/usr/bin/env python

import gspread

google_service_account = gspread.service_account()

# Open by url sheet from a spreadsheet in one go
worksheet = google_service_account.open_by_url("https://docs.google.com/spreadsheets/d/197u2GPYJBZUViYF8vsXOEimHF2JL7Vi9owwBlroBYaA/edit?usp=sharing").sheet1

gspread.service_account(filename='path/to/the/downloaded/file.json')

#see if you can print out a value from a cell