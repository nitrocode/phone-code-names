#!/usr/bin/env python3
import os
import requests
from pprint import pprint
from app.db import create_connection, create_devices_table, create_stats_table, create_fono_table, get_device, insert_device_row
from app.data import load_lineageos_stats, load_lineageos_devices, load_data_file, load_fono
import re
import csv


def load_data(conn):
    # make data dir if it doesn't exist
    # try:
    #     os.mkdir('data')
    # except:
    #     pass
    csv_files = [
        os.path.join('data', 'missing_devices.csv'),
        os.path.join('data', 'google_devices.csv'),
    ]
    los_stats_file = os.path.join('data', 'lineageos_stats.csv')
    los_devices_file = os.path.join('data', 'lineageos_devices.csv')
    
    try:
        create_devices_table(conn)
        create_stats_table(conn)
        create_fono_table(conn)

        for csv_file in csv_files:
            to_db = load_data_file(conn, csv_file, append_file_name=True)
            insert_device_row(conn, to_db)
        load_lineageos_devices(conn, los_devices_file)
        load_lineageos_stats(conn, los_stats_file)
    except:
        print('Tables and data already loaded.')
        raise


def main():
    db_file = ':memory:'
    # db_file = 'my.db'
    conn = create_connection(db_file)
    # if it's from memory, reload data, otherwise assume it's there in db file
    load_data(conn)
    fono_file = os.path.join('data', 'fono_fields.csv')
    load_fono(conn, fono_file)


if __name__ == "__main__":
    print('start')
    main()
    print('fin')