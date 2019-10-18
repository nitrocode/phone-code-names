#!/usr/bin/env python3
from app.db import create_connection
from app.data import load_data
from app import sheet
import os


def main():
    db_file = ':memory:'
    # db_file = 'my.db'
    sheet_name = "LineageOS Phones Automated"
    data_file_to_push = os.path.join('data', 'fono_fields.csv')

    # db connection and load data
    if not os.path.exists(data_file_to_push):
        db_conn = create_connection(db_file)
        load_data(db_conn)

    gsheet_conn = sheet.connect()
    sheet.write_data(gsheet_conn, sheet_name, data_file_to_push)


if __name__ == "__main__":
    print('start')
    main()
    print('fin')