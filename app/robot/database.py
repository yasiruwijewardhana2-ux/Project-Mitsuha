import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name="mitsuha_memory.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Interactions සහ Preferences සඳහා tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS interactions 
                             (id INTEGER PRIMARY KEY, timestamp TEXT, log TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_data 
                             (key TEXT PRIMARY KEY, value TEXT)''')
        self.conn.commit()

    def log_interaction(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO interactions (timestamp, log) VALUES (?, ?)", (timestamp, message))
        self.conn.commit()

    def save_preference(self, key, value):
        self.cursor.execute("REPLACE INTO user_data (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_preference(self, key):
        self.cursor.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None
