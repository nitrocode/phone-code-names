#!/usr/bin/env python3
from app.db import create_connection
from app.data import load_data
from app import sheet
import os


def main():
    db_file = ':memory:'
    # db_file = 'my.db'
    sheet_name = "LineageOS Phones Automated"
    fono_file = os.path.join('data', 'fono_fields.csv')
    FONO_API = os.environ['FONO_API']
    try:
        debug = bool(os.environ['DEBUG'])
    except:
        debug = False

    # db connection and load data
    if not os.path.exists(fono_file):
        db_conn = create_connection(db_file)
        load_data(db_conn, fono_file)

    gsheet_conn = sheet.connect()
    sheet.write_data(gsheet_conn, sheet_name, fono_file, debug=debug)


if __name__ == "__main__":
    main()