import sqlite3
import os


class Database:
    def __init__(self):
        self.dirpath = os.path.join("temp")
        self.path = os.path.join(self.dirpath, "main.db")

        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)

        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.cursor = self.connection.cursor()

        # Init the DB tables
        # self.cursor.execute(
        #     """
        #     CREATE TABLE IF NOT EXISTS groups
        #     (id INTEGER PRIMARY KEY, messages_interval INTEGER NOT_NULL, text text NOT_NULL, ts text NOT_NULL);
        #     """
        # )

    def close_conn(self):
        return self.connection.close()
