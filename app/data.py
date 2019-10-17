import os
import json
import csv
import requests
from bs4 import BeautifulSoup
from app.db import insert_device_row


def load_data_file(conn, input_file):
    """Load data from input file
    
    :param conn: db connection
    :input_file: csv file
    """
    with open(input_file) as fp:
        dr = csv.DictReader(fp)
        to_db = [
            # ([value.lower() for value in i.values()])
            (list(i.values()))
            for i in dr
        ]
        for to in to_db:
            if len(to) != 4:
                print(to)
    
    return insert_device_row(conn, to_db)


def parse_title(title):
    split_datum = title.split(' - ')
    device = split_datum[0]
    split_name = split_datum[1].split(' ')
    brand = split_name[0]
    name = ' '.join(split_name[1:])
    return [brand, name, device, device]


def load_lineageos_devices(conn, output_file):
    """Load data from lineageos search.json
    
    :param conn: db connection
    :input_file: csv file
    """
    try:
        load_data_file(conn, output_file)
    except:
        res = requests.get('https://wiki.lineageos.org/search.json')
        res_data = res.json()
        with open(f'{output_file}.json', 'w') as fp:
            fp.write(json.dumps(res_data))
        to_db = []
        with open(output_file, 'w+') as fp:
            writer = csv.writer(
                fp,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )
            writer.writerow([
                'Retail Branding','Marketing Name','Device','Model'
            ])
            for datum in res_data:
                if not ' - ' in datum['title']:
                    continue
                new_datum = parse_title(datum['title'])
                to_db.append(new_datum)
                writer.writerow(new_datum)
        insert_device_row(conn, to_db)


def load_lineageos_stats(conn, output_file):
    try:
        with open(output_file) as fp:
            return json.loads(fp.read())
    except:
        page = requests.get('https://stats.lineageos.org/')
        soup = BeautifulSoup(page.content, 'html.parser')
        rows = soup.select('div#top-devices .leaderboard-row')
        data = {}
        for row in rows:
            data_str = row.get_text().replace('\n', ' ').replace('.', '')
            data_list = data_str.strip().split(' ')
            data_to_join = data_list[1:-1]
            code = ' '.join(data_list[1:-1])
            code_key = code.rstrip('xx').rstrip('dd')
            if code_key in data:
                print(f'dupe: {code_key}')
            data[code_key] = {
                'rank': data_list[0],
                'count': data_list[-1],
                'code': code
            }
        with open(output_file, 'w') as fp:
            fp.write(json.dumps(data))