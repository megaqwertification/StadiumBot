import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE')

def connect():
    db_conn = psycopg2.connect(DATABASE_URL)
    return db_conn