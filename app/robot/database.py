import sqlite3
import datetime
import os

class DatabaseManager:
    def __init__(self, db_name="mitsuha_memory.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
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

    def get_recent_interactions(self, limit=10):
        """පසුගිය චැට් මෙමරිය ඩේටාබේස් එකෙන් කියවීම"""
        self.cursor.execute("SELECT log FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
        results = self.cursor.fetchall()
        return [row[0] for row in reversed(results)]

    def save_preference(self, key, value):
        self.cursor.execute("REPLACE INTO user_data (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_preference(self, key):
        self.cursor.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None
