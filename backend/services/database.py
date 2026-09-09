import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DatabasePSQL:

    def __init__(self):
        self.__user = os.getenv("DB_USER")
        self.__pass = os.getenv("DB_PASSWORD")
        self.__db = os.getenv("DB_NAME")

    def get_db_conn(self):
        conn = psycopg2.connect(
            host="db",
            database=self.__db,
            user=self.__user,
            password=self.__pass
        )
        return conn
