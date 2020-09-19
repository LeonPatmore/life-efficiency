import gspread

gc = gspread.service_account(filename="credentials.json")
spreadsheet = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/12vPGwr5Ds3ZygiHf0-XXVXuOZFhH7VTLrWioUroeUbA/edit#gid=0")


