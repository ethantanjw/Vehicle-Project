import psycopg2
import csv
import os
import sys
from dotenv import load_dotenv
from .load_mock_data import load_csv_to_database
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database(db_name, user, password, host, port):
    """
    Initialize the vehicles database.
    """
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        cursor.execute(f"CREATE DATABASE {db_name};")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database '{db_name}': {e}")


def create_vehicle_table(conn, file_path):
    """
    Runs SQL queries to create the Vehicle table in the vehicles database.
    """
    try:
        cursor = conn.cursor()

        with open(file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        queries = sql_script.split(';')
        for query in queries:
            query = query.strip()
            if query:
                cursor.execute(query)

        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error executing queries from file '{file_path}': {e}")


def vin_trigger_function(conn):
    """
    Trigger function to enforce lowercase VIN values.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE OR REPLACE FUNCTION vin_case_insensitive()
            RETURNS trigger AS $$
            BEGIN
                NEW.vin = LOWER(NEW.vin);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating trigger function 'vin_case_insensitive': {e}")


def connect_db():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_NAME", "vehicles"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            cursor_factory=RealDictCursor,
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def init_db():
    """
    Wrapper function to create the database and execute queries.
    """
    db_name = os.getenv("DB_NAME", "vehicles")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    base_dir = os.path.abspath(os.path.dirname(__file__))
    sql_file = os.path.join(base_dir, "create.sql")
    csv_file = os.path.join(base_dir, "sample_vehicles.csv")

    create_database(db_name, user, password, host, port)

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )

        vin_trigger_function(conn)
        create_vehicle_table(conn, sql_file)
        load_csv_to_database(conn, csv_file)
        conn.close()

    except Exception as e:
        print(f"Error connecting to the database '{db_name}': {e}")


if __name__ == "__main__":
    init()
