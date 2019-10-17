import sqlite3
from sqlite3 import Error


DEVICE_TABLE = 'devices'
DEVICE_FIELDS = ['brand', 'name', 'device', 'model', 'source']
STAT_TABLE = 'stats'
STAT_FIELDS = ['rank', 'code', 'code_orig', 'count', 'source']
FONO_TABLE = 'fono'
FONO_FIELDS = [
    'code', 'count',
    'Brand', 'DeviceName', '_2g_bands', '_3_5mm_jack_', '_3g_bands',
    '_4g_bands', 'alert_types', 'announced', 'audio_quality', 'battery_c',
    'bluetooth', 'body_c', 'browser', 'build', 'camera', 'card_slot',
    'chipset', 'colors', 'cpu', 'dimensions', 'display', 'display_c', 'edge',
    'features', 'features_c', 'gprs', 'gps', 'gpu', 'infrared_port',
    'internal', 'java', 'loudspeaker', 'loudspeaker_', 'messaging',
    'multitouch', 'music_play', 'network_c', 'nfc', 'os', 'performance',
    'price', 'primary_', 'protection', 'radio', 'resolution', 'sar', 'sar_eu',
    'sar_us', 'secondary', 'sensors', 'sim', 'single', 'size', 'sound_c',
    'speed', 'stand_by', 'status', 'talk_time', 'technology', 'type', 'usb',
    'video', 'weight', 'wlan'
]


def create_connection(db_file):
    """Create a database connection to the SQLite database
    specified by the db_file

    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn


def create_table(conn, table, fields):
    """Create table for csv"""
    # try:
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE {table} ({','.join(fields)});")
    cur.close()
    # except:
    #     print(f'Table {table} already exists.')


def create_devices_table(conn):
    """Create table for csv"""
    return create_table(conn, DEVICE_TABLE, DEVICE_FIELDS)


def create_stats_table(conn):
    """Create table for csv"""
    return create_table(conn, STAT_TABLE, STAT_FIELDS)


def create_fono_table(conn):
    """Create table for csv"""
    return create_table(conn, FONO_TABLE, FONO_FIELDS)


def insert_row(conn, table, fields, to_db):
    """Insert data to db for csv"""
    cur = conn.cursor()
    values = ', '.join(["?"]*len(to_db[0]))
    cur.executemany(
        f"INSERT INTO {table} ({','.join(fields)}) VALUES ({values});",
        to_db
    )
    conn.commit()
    cur.close()


def insert_row_dict(conn, table, fields, to_db):
    """Insert data to db for csv"""
    cur = conn.cursor()
    values = ', '.join(["?"]*len(to_db[0]))
    cur.executemany(
        f"INSERT INTO {table} ({','.join(fields)}) VALUES ({values});",
        to_db
    )
    conn.commit()
    cur.close()


def insert_device_row(conn, to_db):
    """Insert data to db for csv"""
    return insert_row(conn, DEVICE_TABLE, DEVICE_FIELDS, to_db)


def insert_stat_row(conn, to_db):
    """Insert data to db for csv"""
    return insert_row(conn, STAT_TABLE, STAT_FIELDS, to_db)


def insert_fono_row(conn, to_db):
    """Insert data to db for csv"""
    return insert_row(conn, FONO_TABLE, FONO_FIELDS, to_db)


def get_device(conn, search):
    """Query all rows in the tasks table

    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    
    # selects all fields from table where the device / model contains - exact
    fields = ','.join(DEVICE_FIELDS)
    cur.execute(f"select {fields} from {DEVICE_TABLE} where device = ? or model = ?",
                (search, search))
    # to keep it simple, just get the first record found
    data = cur.fetchone()

    if not data:
        # selects all fields from table where the device / model contains
        # the search
        # the COLLATE NOCASE makes the search case insensitive
        cur.execute(f"select {fields} from {DEVICE_TABLE} where device like ? or model like ? "
                    'COLLATE NOCASE;',
                    ('%' + search + '%', '%' + search + '%'))
        # to keep it simple, just get the first record found
        data = cur.fetchone()

    cur.close()
    if data:
        return {f:data[i] for i, f in enumerate(DEVICE_FIELDS)}


def get_lineageos_stats(conn, limit=100):
    # conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # selects all fields from table where the device / model contains - exact
    cur.execute(f'select rank, code, count from stats limit {limit};')
    # to keep it simple, just get the first record found
    data = cur.fetchall()
    cur.close()
    # conn.row_factory = None
    return data