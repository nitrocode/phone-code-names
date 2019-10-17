#!/usr/bin/env python3
import os
import requests
from pprint import pprint
from app.db import create_connection, create_device_table, get_device
from app.data import load_lineageos_stats, load_lineageos_devices, load_data_file


def get_fono_data(brand, device):
    url = 'https://fonoapi.freshpixl.com/v1/getdevice'
    data = {
        'token': os.environ['FONO_API'],
        'brand': brand,
        'device': device
    }
    res = requests.post(url, data=data)
    return res.json()


def main():
    db_file = ':memory:'
    try:
        os.mkdir('data')
    except:
        pass
    csv_files = [
        os.path.join('data', 'google_devices.csv'),
        os.path.join('data', 'missing_devices.csv'),
    ]
    los_stats_file = os.path.join('data', 'lineageos_stats.json')
    los_devices_file = os.path.join('data', 'lineageos_devices.csv')

    conn = create_connection(db_file)
    create_device_table(conn)

    for csv_file in csv_files:
        load_data_file(conn, csv_file)
    load_lineageos_devices(conn, los_devices_file)
    load_lineageos_stats(conn, los_stats_file)

    # for idx, code in enumerate(phone_code):
    #     if idx >= 10:
    #         break
    #     phone_code[code]
    #     get_fono_data()


if __name__ == "__main__":
    print('start')
    main()
    # pprint(get_fono_data('oneplus', 'one'))
    print('fin')