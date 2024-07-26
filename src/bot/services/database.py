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
                                sender TEXT,
                                sender_phone TEXT,
                                receiver TEXT,
                                receiver_phone TEXT,
                                message TEXT,
                                timestamp TEXT)''')
        self.connection.commit()

    def insert_message(self, sender, sender_phone, receiver, receiver_phone, message, timestamp):
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO messages (sender, sender_phone, receiver, receiver_phone, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                            (sender, sender_phone, receiver, receiver_phone, message, timestamp))
        self.connection.commit()

    def fetch_messages(self, sender_phone):
        self.cursor.execute("SELECT * FROM messages WHERE sender_phone=? ORDER BY timestamp", (sender_phone,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()
