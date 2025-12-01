import requests
from typing import Optional, Dict
import time
from configurations import Config as config

class DailyAPI:
    """Daily.co API wrapper with audio-only configuration"""
    
    def __init__(self):
        self.api_key = config.DAILY_API_KEY
        self.base_url = "https://api.daily.co/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_room(self, room_name: Optional[str] = None, max_participants: int = 100) -> Dict:
        """Create audio-only Daily.co room"""
        
        payload = {
            "properties": {
                # Room capacity
                "max_participants": max_participants,
                
                # Audio-only configuration
                "start_video_off": True,              # Video off by default
                "start_audio_off": False,             # Audio on by default
                
                # Disable video features
                "enable_screenshare": False,
                #"enable_video_pro"cessing_ui": False,
                
                # Enable audio features
                "enable_noise_cancellation_ui": True,
                "enable_network_ui": True,
                
                # Other settings
                "enable_chat": False,
                "enable_knocking": False,
                "enable_prejoin_ui": False,
                
                # Auto-expire after 1 hour
                "exp": int(time.time()) + (60 * 60)
            }
        }
        
        if room_name:
            payload["name"] = room_name
        
        try:
            response = requests.post(
                f"{self.base_url}/rooms",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            room_data = response.json()
            print(f"✅ Room created: {room_data.get('name', 'unknown')}")
            return room_data
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating room: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def create_meeting_token(self, room_name: str, user_name: str, is_owner: bool = False) -> str:
        """Create meeting token - SIMPLIFIED VERSION"""
        
        # Simplified payload for better compatibility
        payload = {
            "properties": {
                "room_name": room_name,
                "user_name": user_name,
                "is_owner": is_owner
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/meeting-tokens",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            token = response.json().get("token")
            print(f"✅ Token created for user: {user_name}")
            return token
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_room(self, room_name: str) -> Optional[Dict]:
        """Get room details"""
        try:
            response = requests.get(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting room: {e}")
            return None
    
    def delete_room(self, room_name: str) -> bool:
        """Delete a room"""
        try:
            response = requests.delete(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Room deleted: {room_name}")
                return True
            else:
                print(f"⚠️ Room deletion status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error deleting room: {e}")
            return False

# Create global instance
daily = DailyAPI()