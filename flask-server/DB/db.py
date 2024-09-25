import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="aegis_auth",
        user="aegis",
        password="aegis_pwd",
        host="localhost",
        port="5432"
    )

# functions for creating users, and other db related functions from model.py