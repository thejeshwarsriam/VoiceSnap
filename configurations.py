import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Daily.co Configuration
    DAILY_API_KEY = os.getenv("DAILY_API_KEY")
    DAILY_API_URL = "https://api.daily.co/v1"
    
    # Supabase Configuration (for user data)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    
    # App Configuration
    MAX_ROOM_SIZE = 100
    ROOM_EXPIRY_MINUTES = 60

config = Config()