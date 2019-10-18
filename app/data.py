import os
import json
import csv
import re
import requests
from bs4 import BeautifulSoup
from app.db import create_devices_table, create_stats_table, \
    create_fono_table, insert_device_row, insert_stat_row, \
    insert_fono_row, get_device, get_lineageos_stats, \
    FONO_FIELDS, STAT_FIELDS, DEVICE_FIELDS


def save_request(url, output_file):
    """
    Attempts to read from file. If there's no file, then it will
    save the contents of a url in json/html
    """
    # check for cached version
    try:
        with open(output_file) as fp:
            data = fp.read()
            try:
                data = json.loads(data)
            except:
                pass
    except:
        # otherwise redownload and parse
        page = requests.get(url)
        with open(output_file, 'w') as fp:
            try:
                data = page.json()
                fp.write(json.dumps(data))
            except:
                data = page.text
                fp.write(data)
    return data


def load_data_file(conn, input_file, append_file_name=False):
    """Load data from input file
    
    :param conn: db connection
    :input_file: csv file
    """
    with open(input_file) as fp:
        dr = csv.DictReader(fp)
        if append_file_name:
            to_db = [
                # ([value.lower() for value in i.values()])
                (list(i.values()) + [input_file])
                for i in dr
            ]
        else:
            to_db = [
                # ([value.lower() for value in i.values()])
                (list(i.values()))
                for i in dr
            ]
    
    return to_db


def parse_title(title):
    """Parse strings from lineageos json

    :param title: format should be `code - brand phone`
    """
    split_datum = title.split(' - ')
    split_name = split_datum[1].split(' ')

    device = split_datum[0]
    brand = split_name[0]
    name = ' '.join(split_name[1:])

    return [brand, name, device, device]


def parse_stat(stat):
    """Parses the stat html text to get rank, code, and count"""
    stat_clean = stat.replace('\n', ' ').replace('.', '').strip()
    stat_list = stat_clean.split(' ')

    rank = stat_list[0]
    code_orig = ' '.join(stat_list[1:-1])
    # remove xx and dd from the end of the code so we can get more matches
    code = code_orig.rstrip('xx').rstrip('dd')
    count = stat_list[-1]

    return [rank, code, code_orig, count]


def get_fono_data(brand, device):
    """Hits the fono api to get fields based on brand and device"""
    url = 'https://fonoapi.freshpixl.com/v1/getdevice'
    data = {
        'token': os.environ['FONO_API'],
        'brand': brand,
        'device': device
    }
    res = requests.post(url, data=data)
    return res.json()


def set_missing_fields_to_blank(data):
    """Set field to empty if defined in FONO_FIELDS and missing"""
    for field in list(set(FONO_FIELDS) - set(list(data))):
        data[field] = ''
    return data


def parse_fono(conn, datum):
    """This parses the fono data and combines it with lineageos data"""
    model = get_device(conn, datum['code'])
    if not model:
        print(f"Missing codename '{datum['code']}' from devices table. "
               "Add to missing_devices.csv")
        data = datum.copy()
        return set_missing_fields_to_blank(data)
    # remove paranthetical strings from name
    if '(' in model['name']:
        model['name'] = re.sub(r'\(.*\)', '', model['name'])
    fono_data = get_fono_data(model['brand'], model['name'])
    if 'status' in fono_data:
        print(f'Missing brand "{model["brand"]}" and device "{model["name"]}" '
              f'from fono api. Status: {fono_data["status"]}')
        data = dict(datum)
        data['brand'] = model["brand"]
        data['name'] = model["name"]
        return set_missing_fields_to_blank(data)
    # use only the first data point
    data = fono_data[0]
    for field in list(data):
        # Remove newlines from each field if they exist
        if '\r\n' in data[field]:
            data[field] = data[field].replace('\r\n', ' ')
        # only keep fields defined in FONO_FIELDS
        if not field in FONO_FIELDS:
            del data[field]
    # set field to none if defined in FONO_FIELDS and missing from
    # defined but not found in fono data
    data = set_missing_fields_to_blank(data)
    data.update(datum)
    return data


def load_lineageos_devices(conn, output_file):
    """Load data from lineageos search.json
    
    :param conn: db connection
    :input_file: csv file
    """
    to_db = []
    try:
        to_db = load_data_file(conn, output_file)
    except:
        url = 'https://wiki.lineageos.org/search.json'
        save_file = f'{os.path.splitext(output_file)[0]}.json'
        res_data = save_request(url, save_file)
        with open(output_file, 'w+') as fp:
            writer = csv.writer(
                fp,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )
            writer.writerow(DEVICE_FIELDS)
            for datum in res_data:
                if not ' - ' in datum['title']:
                    continue
                # parse and add source
                new_datum = parse_title(datum['title']) + [url]
                to_db.append(new_datum)
                writer.writerow(new_datum)
    insert_device_row(conn, to_db)


def load_lineageos_stats(conn, output_file):
    """Loads lineageos stats into the db"""
    to_db = []
    try:
        to_db = load_data_file(conn, output_file)
    except:
        save_file = f'{os.path.splitext(output_file)[0]}.html'
        url = 'https://stats.lineageos.org/'
        data = save_request(url, save_file)
        soup = BeautifulSoup(data, 'html.parser')
        rows = soup.select('div#top-devices .leaderboard-row')
        with open(output_file, 'w+') as fp:
            writer = csv.writer(
                fp,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )
            writer.writerow(STAT_FIELDS)
            for row in rows:
                # parse and add source
                new_datum = parse_stat(row.get_text()) + [url]
                to_db.append(new_datum)
                writer.writerow(new_datum)
    insert_stat_row(conn, to_db)


def load_fono(conn, output_file, limit):
    """Loads combined fono and los stats data into db"""
    to_db = []
    try:
        to_db = load_data_file(conn, output_file)
    except:
        data = get_lineageos_stats(conn, limit)
        with open(output_file, 'w+') as fp:
            writer = csv.writer(
                fp,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )
            writer.writerow(FONO_FIELDS)
            for datum in data:
                values = parse_fono(conn, datum)
                if values:
                    new_datum = [values[field] for field in FONO_FIELDS]
                    to_db.append(new_datum)
                    writer.writerow(new_datum)

    insert_fono_row(conn, to_db)


def load_data(conn, limit=10):
    """Loads all data"""
    csv_files = [
        os.path.join('data', 'missing_devices.csv'),
        os.path.join('data', 'google_devices.csv'),
    ]
    los_stats_file = os.path.join('data', 'lineageos_stats.csv')
    los_devices_file = os.path.join('data', 'lineageos_devices.csv')
    fono_file = os.path.join('data', 'fono_fields.csv')
    
    try:
        create_devices_table(conn)
        create_stats_table(conn)
        create_fono_table(conn)

        for csv_file in csv_files:
            to_db = load_data_file(conn, csv_file, append_file_name=True)
            insert_device_row(conn, to_db)
    except:
        print('Tables already loaded.')

    load_lineageos_devices(conn, los_devices_file)
    load_lineageos_stats(conn, los_stats_file)
    load_fono(conn, fono_file, limit=100)