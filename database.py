import sqlite3
import threading
import os
from datetime import datetime

class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_sessions.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        with self.conn:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT DEFAULT 'Yeni Sohbet',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP
            )''')
            
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT CHECK(role IN ('user', 'assistant')),
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )''')
    
    # Oturum İşlemleri
    def create_session(self, session_id, session_name=None):
        with self.conn:
            self.conn.execute('''
            INSERT INTO sessions (id, name, last_used)
            VALUES (?, ?, ?)''', 
            (session_id, session_name or f"Sohbet {datetime.now().strftime('%d/%m %H:%M')}", datetime.now()))
    
    def get_all_sessions(self):
        with self.conn:
            cursor = self.conn.execute('''
            SELECT id, name, strftime('%d/%m %H:%M', last_used) as last_used 
            FROM sessions 
            ORDER BY last_used DESC''')
            return cursor.fetchall()
    
    def delete_session(self, session_id):
        with self.conn:
            self.conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    
    # Mesaj İşlemleri
    def save_message(self, session_id, role, content):
        with self.conn:
            self.conn.execute('''
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)''', (session_id, role, content))
            self.conn.execute('UPDATE sessions SET last_used = ? WHERE id = ?', (datetime.now(), session_id))
    
    def get_messages(self, session_id):
        with self.conn:
            cursor = self.conn.execute('''
            SELECT role, content, strftime('%H:%M', timestamp) as time 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp''', (session_id,))
            return cursor.fetchall()