import psycopg2
from . import db_config


def get_conn():
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASWD
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        pass
    return False


def check_conn():
    conn = get_conn()
    if conn:
        conn.close()
        print("working database connection")
    else:
        print("Database connection settings invalid or server not reacheable")
