import sqlite3
from typing import Optional, List, Dict
from datetime import datetime

class Database:
    """SQLite3 database"""
    
    def __init__(self, db_path: str = "voicesnap.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            avatar_url TEXT,
            google_id TEXT UNIQUE,
            status TEXT DEFAULT 'offline',
            room_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status TEXT DEFAULT 'accepted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id),
            UNIQUE(user_id, friend_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(group_id, user_id)
        )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_friendships_user ON friendships(user_id)")
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, name: str, google_id: str = None, avatar_url: str = None) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                UPDATE users SET name = ?, avatar_url = COALESCE(?, avatar_url), 
                google_id = COALESCE(?, google_id), last_seen = CURRENT_TIMESTAMP 
                WHERE email = ?
                """, (name, avatar_url, google_id, email))
            else:
                cursor.execute("""
                INSERT INTO users (email, name, avatar_url, google_id, status) 
                VALUES (?, ?, ?, ?, 'available')
                """, (email, name, avatar_url, google_id))
            
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except:
            conn.close()
            return None
    
    def search_users(self, query: str, exclude_user_id: int = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query_pattern = f"%{query}%"
        
        if exclude_user_id:
            cursor.execute("""
            SELECT * FROM users 
            WHERE (name LIKE ? OR email LIKE ?) AND id != ?
            ORDER BY name LIMIT 20
            """, (query_pattern, query_pattern, exclude_user_id))
        else:
            cursor.execute("""
            SELECT * FROM users WHERE name LIKE ? OR email LIKE ? 
            ORDER BY name LIMIT 20
            """, (query_pattern, query_pattern))
        
        users = cursor.fetchall()
        conn.close()
        return [dict(u) for u in users]
    
    def is_friend(self, user_id: int, friend_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT COUNT(*) as count FROM friendships 
        WHERE user_id = ? AND friend_id = ? AND status = 'accepted'
        """, (user_id, friend_id))
        
        result = cursor.fetchone()
        conn.close()
        return result['count'] > 0
    
    def add_friend(self, user_id: int, friend_email: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM users WHERE email = ?", (friend_email,))
            friend = cursor.fetchone()
            
            if not friend:
                conn.close()
                return False
            
            friend_id = friend['id']
            
            cursor.execute("""
            INSERT OR IGNORE INTO friendships (user_id, friend_id, status) 
            VALUES (?, ?, 'accepted')
            """, (user_id, friend_id))
            
            cursor.execute("""
            INSERT OR IGNORE INTO friendships (user_id, friend_id, status) 
            VALUES (?, ?, 'accepted')
            """, (friend_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_user_friends(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT u.* FROM users u
        INNER JOIN friendships f ON u.id = f.friend_id
        WHERE f.user_id = ? AND f.status = 'accepted'
        ORDER BY u.name
        """, (user_id,))
        
        friends = cursor.fetchall()
        conn.close()
        return [{"friend": dict(f)} for f in friends]
    
    def get_user_groups(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT g.*, COUNT(gm.user_id) as member_count
        FROM groups g
        INNER JOIN group_members gm ON g.id = gm.group_id
        WHERE g.id IN (SELECT group_id FROM group_members WHERE user_id = ?)
        GROUP BY g.id
        """, (user_id,))
        
        groups = cursor.fetchall()
        conn.close()
        return [dict(g) for g in groups]
    
    def update_user_status(self, user_id: int, status: str, room_id: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE users SET status = ?, room_id = ?, last_seen = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (status, room_id, user_id))
        
        conn.commit()
        conn.close()

db = Database()