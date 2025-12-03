import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Config:
    """Production configuration for VoiceSnap"""
    
    # Daily.co API Configuration
    DAILY_API_KEY = os.getenv("DAILY_API_KEY", "")
    if not DAILY_API_KEY:
        # Try Streamlit secrets
        try:
            DAILY_API_KEY = st.secrets["DAILY_API_KEY"]
        except:
            pass
    
    DAILY_API_URL = "https://api.daily.co/v1"
    
    # Google OAuth Configuration
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/")
    if not GOOGLE_REDIRECT_URI or GOOGLE_REDIRECT_URI == "http://localhost:8501/":
        # Try Streamlit secrets
        try:
            GOOGLE_REDIRECT_URI = st.secrets.get("GOOGLE_REDIRECT_URI", "http://localhost:8501/")
        except:
            pass
    
    # App Configuration
    MAX_ROOM_SIZE = 100
    ROOM_EXPIRY_MINUTES = 60
    
    # Database Configuration
    DATABASE_PATH = "voicesnap.db"
    
    # Debug mode (set to False in production)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

config = Config()