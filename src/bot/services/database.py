import mysql.connector
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                               (id INT AUTO_INCREMENT PRIMARY KEY,
                                sender VARCHAR(255),
                                sender_phone VARCHAR(255),
                                receiver VARCHAR(255),
                                receiver_phone VARCHAR(255),
                                message TEXT,
                                timestamp DATETIME)''')
        self.connection.commit()

    def insert_message(self, sender, sender_phone, receiver, receiver_phone, message, timestamp):
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO messages (sender, sender_phone, receiver, receiver_phone, message, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
                            (sender, sender_phone, receiver, receiver_phone, message, timestamp))
        self.connection.commit()
