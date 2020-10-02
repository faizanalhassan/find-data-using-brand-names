import sqlite3
from sqlite3 import IntegrityError, OperationalError
debug = False


def escape_single_quote(value):
    return value.replace("'", "''")


def print_if_debug(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


def create_connection(db_path):
    database = db_path
    print_if_debug(f"db = {database}")
    conn = sqlite3.connect(database)
    return conn


def run_query(query, db_path):
    conn = create_connection(db_path)
    c = conn.cursor()
    print_if_debug(f"query = {query}")
    try:
        c.execute(query)
        conn.commit()
        query = query.lower()
        rows = c.fetchall()
        rowcount = c.rowcount
        lastrowid = c.lastrowid
        if query.startswith("create"):
            table = query.replace("create table if not exists ", "").split(" ")[0]
            c.execute(f"PRAGMA table_info({table});")
            print_if_debug(f"Columns:{','.join([row[1] for row in c.fetchall()])}")
        conn.close()
        return lastrowid, rowcount, rows
    except Exception as e:
        print(f'Exception in query: {query}')
        conn.close()
        raise

