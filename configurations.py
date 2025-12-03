import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Config:
    """Production configuration for VoiceSnap"""
    
    # Daily.co API Configuration
    DAILY_API_KEY = os.getenv("DAILY_API_KEY", "")
    if not DAILY_API_KEY:
        try:
            DAILY_API_KEY = st.secrets["DAILY_API_KEY"]
        except:
            pass
    
    DAILY_API_URL = "https://api.daily.co/v1"
    
    # Google OAuth Configuration - AUTO-DETECT REDIRECT URI
    @staticmethod
    def get_google_redirect_uri():
        """Auto-detect correct redirect URI based on environment"""
        
        # Try from .env first
        env_uri = os.getenv("GOOGLE_REDIRECT_URI")
        if env_uri:
            return env_uri
        
        # Try from Streamlit secrets
        try:
            return st.secrets.get("GOOGLE_REDIRECT_URI")
        except:
            pass
        
        # Auto-detect based on Streamlit config
        try:
            # For local development
            if 'localhost' in st.get_option('client.serverAddress'):
                return "http://localhost:8501/"
            # For Streamlit Cloud
            elif hasattr(st, 'runtime') and hasattr(st.runtime, 'exists'):
                return os.getenv("APP_URL", "http://localhost:8501/")
        except:
            pass
        
        return "http://localhost:8501/"
    
    GOOGLE_REDIRECT_URI = get_google_redirect_uri()
    
    # App Configuration
    MAX_ROOM_SIZE = 100
    ROOM_EXPIRY_MINUTES = 60
    
    # Database Configuration
    DATABASE_PATH = "voicesnap.db"
    
    # Debug mode
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

config = Config()