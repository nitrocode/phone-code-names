import os
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def connect():
    """Use creds to create a client to interact with the Google Drive API"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'client_secret.json', scope)
    client = gspread.authorize(creds)
    return client


def write_data(client, sheet_name, data_file, debug=False):
    sheet = client.open(sheet_name).sheet1

    cells = []
    with open(data_file) as fp:
        dr = csv.reader(fp)
        for row_num, row in enumerate(dr):
            for col_num, cell in enumerate(row):
                cells.append(
                    gspread.Cell(
                        row_num + 1, col_num + 1,
                        row[col_num]
                    )
                )

    if not debug:
        sheet.update_cells(cells)
