import sqlite3
from sqlite3 import Error


DEVICE_FIELDS = ['brand', 'name', 'device', 'model']
DEVICE_TABLE = 'device'


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
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE {table} ({','.join(fields)});")
    cur.close()


def create_device_table(conn):
    """Create table for csv"""
    return create_table(conn, DEVICE_TABLE, DEVICE_FIELDS)


def insert_row(conn, table, fields, to_db):
    """Insert data to db for csv"""
    cur = conn.cursor()
    cur.executemany(
        f"INSERT INTO {table} ({','.join(fields)}) VALUES (?, ?, ?, ?);",
        to_db
    )
    conn.commit()
    cur.close()


def insert_device_row(conn, to_db):
    """Insert data to db for csv"""
    return insert_row(conn, DEVICE_TABLE, DEVICE_FIELDS, to_db)


def get_device(conn, search):
    """Query all rows in the tasks table

    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    
    # selects all fields from table where the device / model contains - exact
    cur.execute(f'select * from {DEVICE_TABLE} where device = ? or model = ?',
                (search, search))
    # to keep it simple, just get the first record found
    data = cur.fetchone()

    if not data:
        # selects all fields from table where the device / model contains
        # the search
        # the COLLATE NOCASE makes the search case insensitive
        cur.execute(f'select * from {DEVICE_TABLE} where device like ? or model like ? '
                    'COLLATE NOCASE;',
                    ('%' + search + '%', '%' + search + '%'))
        # to keep it simple, just get the first record found
        data = cur.fetchone()

    cur.close()
    if data:
        return {f:data[i] for i, f in enumerate(DEVICE_FIELDS)}
