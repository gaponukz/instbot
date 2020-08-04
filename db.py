import sqlite3

"""
    CREATE TABLE Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR (255) NOT NULL,
        user_name VARCHAR (255) NOT NULL
    );
"""

class SQLite(object):
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database, check_same_thread = False)
        self.cursor = self.connection.cursor()

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `Users`").fetchall()

    def user_exists(self, user_id) -> bool:
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `Users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, user_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO `Users` (`user_id`, `user_name`) VALUES (?,?)", (user_id, user_name))