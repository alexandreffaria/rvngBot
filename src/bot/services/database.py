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
        self.create_users_table()
        self.create_messages_table()
        self.create_state_table()

    def create_users_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                               (id INT AUTO_INCREMENT PRIMARY KEY,
                                phone VARCHAR(255) UNIQUE,
                                name VARCHAR(255),
                                email VARCHAR(255),
                                role VARCHAR(255))''')
        self.connection.commit()

    def create_messages_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                            (id INT AUTO_INCREMENT PRIMARY KEY,
                                user_id INT,
                                sender VARCHAR(255),
                                sender_phone VARCHAR(255),
                                receiver VARCHAR(255),
                                receiver_phone VARCHAR(255),
                                message TEXT,
                                timestamp DATETIME,
                                FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.connection.commit()

    def create_state_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS state
                               (user_id INT PRIMARY KEY,
                                state_key VARCHAR(255),
                                state_value TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.connection.commit()

    def insert_user(self, phone, name=None, email=None, role=None):
        self.cursor.execute('SELECT id, name, email, role FROM users WHERE phone=%s', (phone,))
        user = self.cursor.fetchone()
        
        if user:
            user_id, current_name, current_email, current_role = user
            updates = []
            params = []
            
            if name and name != current_name:
                updates.append("name=%s")
                params.append(name)
            if email and email != current_email:
                updates.append("email=%s")
                params.append(email)
            if role and role != current_role:
                updates.append("role=%s")
                params.append(role)
            
            if updates:
                update_query = "UPDATE users SET " + ", ".join(updates) + " WHERE phone=%s"
                params.append(phone)
                self.cursor.execute(update_query, tuple(params))
                self.connection.commit()
        else:
            self.cursor.execute('''INSERT INTO users (phone, name, email, role) 
                                VALUES (%s, %s, %s, %s)''',
                                (phone, name, email, role))
            self.connection.commit()
            user_id = self.cursor.lastrowid
        
        return user_id


    def insert_message(self, user_id, sender, sender_phone, receiver, receiver_phone, message, timestamp):
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO messages (user_id, sender, sender_phone, receiver, receiver_phone, message, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (user_id, sender, sender_phone, receiver, receiver_phone, message, timestamp))
        self.connection.commit()

    def update_user(self, user_id, name=None, email=None, role=None):
        query = "UPDATE users SET "
        params = []
        if name:
            query += "name=%s, "
            params.append(name)
        if email:
            query += "email=%s, "
            params.append(email)
        if role:
            query += "role=%s, "
            params.append(role)
        query = query.rstrip(', ') + " WHERE id=%s"
        params.append(user_id)
        
        self.cursor.execute(query, tuple(params))
        self.connection.commit()

    def set_state(self, user_id, key, value):
        self.cursor.execute('''INSERT INTO state (user_id, state_key, state_value) 
                            VALUES (%s, %s, %s) 
                            ON DUPLICATE KEY UPDATE state_value=VALUES(state_value)''',
                            (user_id, key, value))
        self.connection.commit()

    def get_state(self, user_id, key, default=None):
        self.cursor.execute('SELECT state_value FROM state WHERE user_id=%s AND state_key=%s', (user_id, key))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def delete_state(self, user_id, key):
        self.cursor.execute('DELETE FROM state WHERE user_id=%s AND state_key=%s', (user_id, key))
        self.connection.commit()
