from supabase import create_client, Client
from typing import Optional, List, Dict
import streamlit as st
from configurations import Config as config

class Database:
    def __init__(self):
        if config.SUPABASE_URL and config.SUPABASE_KEY:
            self.client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        else:
            self.client = None
            st.warning("⚠️ Supabase not configured. Using local storage only.")
    
    def create_user(self, email: str, name: str, avatar_url: str = None) -> Dict:
        """Create or update user"""
        if not self.client:
            return {"id": hash(email) % 10000, "email": email, "name": name}
        
        try:
            # Check if user exists
            result = self.client.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                # Update existing user
                user = self.client.table("users").update({
                    "name": name,
                    "avatar_url": avatar_url,
                    "last_seen": "now()"
                }).eq("email", email).execute()
                return user.data[0]
            else:
                # Create new user
                user = self.client.table("users").insert({
                    "email": email,
                    "name": name,
                    "avatar_url": avatar_url or f"https://ui-avatars.com/api/?name={name}&background=random"
                }).execute()
                return user.data[0]
        except Exception as e:
            st.error(f"Database error: {e}")
            return {"id": hash(email) % 10000, "email": email, "name": name}
    
    def get_user_friends(self, user_id: int) -> List[Dict]:
        """Get user's friends"""
        if not self.client:
            return self._get_mock_friends()
        
        try:
            result = self.client.table("friendships").select(
                "friend:users!friendships_friend_id_fkey(id, name, email, avatar_url, status)"
            ).eq("user_id", user_id).execute()
            return result.data
        except:
            return self._get_mock_friends()
    
    def add_friend(self, user_id: int, friend_email: str) -> bool:
        """Send friend request"""
        if not self.client:
            return True
        
        try:
            # Find friend by email
            friend = self.client.table("users").select("id").eq("email", friend_email).execute()
            if not friend.data:
                return False
            
            friend_id = friend.data[0]["id"]
            
            # Create bidirectional friendship
            self.client.table("friendships").insert([
                {"user_id": user_id, "friend_id": friend_id},
                {"user_id": friend_id, "friend_id": user_id}
            ]).execute()
            return True
        except:
            return False
    
    def update_presence(self, user_id: int, status: str, room_id: str = None):
        """Update user presence"""
        if not self.client:
            return
        
        try:
            self.client.table("users").update({
                "status": status,
                "room_id": room_id,
                "last_seen": "now()"
            }).eq("id", user_id).execute()
        except:
            pass
    
    def _get_mock_friends(self) -> List[Dict]:
        """Mock friends for demo"""
        return [
            {
                "friend": {
                    "id": 1,
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com",
                    "avatar_url": "https://ui-avatars.com/api/?name=Rahul+Kumar&background=4ade80",
                    "status": "available"
                }
            },
            {
                "friend": {
                    "id": 2,
                    "name": "Priya Sharma",
                    "email": "priya@example.com",
                    "avatar_url": "https://ui-avatars.com/api/?name=Priya+Sharma&background=f59e0b",
                    "status": "busy"
                }
            },
            {
                "friend": {
                    "id": 3,
                    "name": "Arjun Patel",
                    "email": "arjun@example.com",
                    "avatar_url": "https://ui-avatars.com/api/?name=Arjun+Patel&background=ef4444",
                    "status": "offline"
                }
            },
            {
                "friend": {
                    "id": 4,
                    "name": "Sneha Gupta",
                    "email": "sneha@example.com",
                    "avatar_url": "https://ui-avatars.com/api/?name=Sneha+Gupta&background=8b5cf6",
                    "status": "available"
                }
            }
        ]

db = Database()