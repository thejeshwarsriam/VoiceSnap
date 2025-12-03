import requests
from typing import Optional, Dict
import time
from configurations import Config as config

class DailyAPI:
    """Daily.co API wrapper for VoiceSnap - Production Ready"""
    
    def __init__(self):
        self.api_key = config.DAILY_API_KEY
        self.base_url = config.DAILY_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_room(self, room_name: Optional[str] = None, max_participants: int = 100) -> Optional[Dict]:
        """Create audio-only Daily.co room"""
        
        if not self.api_key:
            print("❌ Error: DAILY_API_KEY not configured")
            return None
        
        payload = {
            "properties": {
                # Room capacity
                "max_participants": max_participants,
                
                # Audio-only configuration
                "start_video_off": True,              # Video off by default
                "start_audio_off": False,             # Audio on by default
                
                # Disable video features
                "enable_screenshare": False,
                "enable_video_processing_ui": False,
                
                # Enable audio features
                "enable_noise_cancellation_ui": True,
                "enable_network_ui": True,
                
                # Other settings
                "enable_chat": False,
                "enable_knocking": False,
                "enable_prejoin_ui": False,
                
                # Auto-expire after specified time (in seconds)
                "exp": int(time.time()) + (config.ROOM_EXPIRY_MINUTES * 60)
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
            
            if config.DEBUG:
                print(f"✅ Room created: {room_data.get('name', 'unknown')}")
            
            return room_data
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error creating room: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating room: {e}")
            return None
    
    def create_meeting_token(self, room_name: str, user_name: str, is_owner: bool = False) -> Optional[str]:
        """Create meeting token for user - Simplified for compatibility"""
        
        if not self.api_key:
            print("❌ Error: DAILY_API_KEY not configured")
            return None
        
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
            
            if config.DEBUG:
                print(f"✅ Token created for user: {user_name}")
            
            return token
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error creating token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating token: {e}")
            return None
    
    def get_room(self, room_name: str) -> Optional[Dict]:
        """Get room details"""
        
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if config.DEBUG:
                print(f"❌ Error getting room: {e}")
            return None
    
    def delete_room(self, room_name: str) -> bool:
        """Delete a room"""
        
        if not self.api_key:
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                if config.DEBUG:
                    print(f"✅ Room deleted: {room_name}")
                return True
            else:
                if config.DEBUG:
                    print(f"⚠️ Room deletion status: {response.status_code}")
                return False
                
        except Exception as e:
            if config.DEBUG:
                print(f"❌ Error deleting room: {e}")
            return False
    
    def get_domain_config(self) -> Optional[Dict]:
        """Get Daily.co domain configuration (for debugging)"""
        
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if config.DEBUG:
                print(f"❌ Error getting domain config: {e}")
            return None
    
    def test_api_key(self) -> tuple[bool, str]:
        """Test if Daily.co API key is valid"""
        
        if not self.api_key:
            return False, "API key not configured"
        
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return True, "✅ API key is valid"
            else:
                return False, f"❌ API key invalid: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"❌ API error: {str(e)}"

# Create global instance
daily = DailyAPI()