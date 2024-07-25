import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="data/messages.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                               (id INTEGER PRIMARY KEY,
                                user_id TEXT,
                                sender TEXT,
                                message TEXT,
                                timestamp TEXT)''')
        self.connection.commit()

    def insert_message(self, user_id, sender, message, timestamp):
        # Convert timestamp to ISO 8601 format if it's not already
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO messages (user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                            (user_id, sender, message, timestamp))
        self.connection.commit()

    def fetch_messages(self, user_id):
        self.cursor.execute("SELECT * FROM messages WHERE user_id=? ORDER BY timestamp", (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()
