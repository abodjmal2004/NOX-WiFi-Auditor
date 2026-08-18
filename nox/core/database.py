import sqlite3
import os
from .config import Config

class Database:
    def __init__(self):
        self.db_path = os.path.join(Config.OUTPUT_DIR, "nox_data.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        # Table for discovered targets
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bssid TEXT UNIQUE,
                essid TEXT,
                encryption TEXT,
                channel TEXT,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for captured handshakes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS handshakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bssid TEXT,
                essid TEXT,
                file_path TEXT,
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bssid) REFERENCES targets(bssid)
            )
        ''')
        
        # Table for cracked passwords
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bssid TEXT,
                essid TEXT,
                password TEXT,
                cracked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bssid) REFERENCES targets(bssid)
            )
        ''')
        self.conn.commit()

    def save_target(self, target):
        self.cursor.execute('''
            INSERT OR REPLACE INTO targets (bssid, essid, encryption, channel, last_seen)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (target.bssid, target.essid, target.encryption, target.channel))
        self.conn.commit()

    def save_handshake(self, bssid, essid, file_path):
        self.cursor.execute('''
            INSERT INTO handshakes (bssid, essid, file_path)
            VALUES (?, ?, ?)
        ''', (bssid, essid, file_path))
        self.conn.commit()

    def save_password(self, bssid, essid, password):
        self.cursor.execute('''
            INSERT INTO passwords (bssid, essid, password)
            VALUES (?, ?, ?)
        ''', (bssid, essid, password))
        self.conn.commit()

    def get_all_passwords(self):
        self.cursor.execute('SELECT essid, bssid, password, cracked_at FROM passwords')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
