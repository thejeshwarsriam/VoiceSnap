import streamlit as st
import time
from authlib.integrations.requests_client import OAuth2Session
from database import db
from daily_api import daily
from configurations import Config as config
import os
import json
import requests

# Page config
st.set_page_config(
    page_title="VoiceSnap",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean CSS
st.markdown("""
<style>
    .block-container {padding-top: 2rem; max-width: 1200px;}
    .stApp {background: white;}
    h1, h2, h3, h4, h5, h6, p, div, span, label {color: #000000 !important;}
    .header-card {background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px;}
    .friend-card {background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin: 8px 0; display: flex; align-items: center; justify-content: space-between;}
    .friend-card:hover {box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
    .status-dot {width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px;}
    .status-available {background: #22c55e;}
    .status-busy {background: #ef4444;}
    .status-offline {background: #9ca3af;}
    .call-header {background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHLIB CONFIGURATION
# ============================================================================

def load_google_credentials():
    """Load Google OAuth credentials"""
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        
        if credentials_json:
            return json.loads(credentials_json)
        else:
            with open('google_credentials.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"❌ Failed to load Google OAuth credentials: {e}")
        return None

def get_authlib_oauth_session():
    """Create AuthLib OAuth2 session for Google"""
    credentials = load_google_credentials()
    if not credentials:
        return None
    
    try:
        client_id = credentials['web']['client_id']
        client_secret = credentials['web']['client_secret']
        
        session = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=config.GOOGLE_REDIRECT_URI,
            scope=[
                'openid',
                'profile',
                'email'
            ]
        )
        return session
    except Exception as e:
        st.error(f"❌ Failed to create OAuth session: {e}")
        return None

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'in_call' not in st.session_state:
    st.session_state.in_call = False
if 'current_room' not in st.session_state:
    st.session_state.current_room = None
if 'room_url' not in st.session_state:
    st.session_state.room_url = None
if 'auth_processed' not in st.session_state:
    st.session_state.auth_processed = False

# ============================================================================
# AUTHLIB OAUTH LOGIN
# ============================================================================

def get_google_auth_url():
    """Generate Google OAuth authorization URL using AuthLib"""
    session = get_authlib_oauth_session()
    if not session:
        return None
    
    try:
        auth_uri, state = session.create_authorization_url(
            'https://accounts.google.com/o/oauth2/v2/auth',
            prompt='consent'
        )
        st.session_state.oauth_state = state
        return auth_uri
    except Exception as e:
        st.error(f"❌ Failed to generate auth URL: {e}")
        return None

def exchange_code_for_token(code):
    """Exchange authorization code for access token using AuthLib"""
    try:
        session = get_authlib_oauth_session()
        if not session:
            return None
        
        # Fetch token from Google
        token = session.fetch_token(
            'https://oauth2.googleapis.com/token',
            code=code,
            timeout=10
        )
        
        if not token or 'access_token' not in token:
            st.error("❌ Failed to obtain access token")
            return None
        
        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {token["access_token"]}'},
            timeout=10
        )
        
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            return {
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
        else:
            st.error(f"❌ Failed to fetch user info: {user_info_response.status_code}")
            return None
    
    except Exception as e:
        st.error(f"❌ Token exchange failed: {str(e)}")
        return None

def render_google_login():
    """Google OAuth login screen using AuthLib"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 50px 20px;">
            <h1 style="font-size: 56px; margin: 0;">🎙️</h1>
            <h1 style="font-size: 36px; margin: 10px 0;">VoiceSnap</h1>
            <p style="font-size: 16px; color: #666; margin-bottom: 30px;">
                Real-time audio hangouts for friends
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: -20px;">
            <h3 style="margin: 0 0 5px 0; font-size: 20px;">🔐 Sign in with Google</h3>
            <p style="margin: 0; font-size: 14px; color: #666;">Secure authentication • No password needed</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for OAuth callback
        query_params = st.query_params
        
        # Process auth code only once
        if 'code' in query_params and not st.session_state.auth_processed:
            # Mark as processed immediately to prevent re-processing
            st.session_state.auth_processed = True
            auth_code = query_params['code']
            
            with st.spinner("🔄 Authenticating with Google..."):
                user_info = exchange_code_for_token(auth_code)
                
                if user_info:
                    try:
                        # Create/update user in database
                        user = db.create_user(
                            email=user_info['email'],
                            name=user_info['name'],
                            google_id=user_info['id'],
                            avatar_url=user_info['picture']
                        )
                        
                        if user:
                            st.session_state.user = user
                            
                            # Clear query params BEFORE rerun
                            st.query_params.clear()
                            st.session_state.auth_processed = False
                            
                            st.success(f"✅ Welcome, {user_info['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to create user in database")
                            st.session_state.auth_processed = False
                    except Exception as e:
                        st.error(f"❌ Database error: {e}")
                        st.session_state.auth_processed = False
                else:
                    st.error("❌ Failed to authenticate. Please try again.")
                    st.session_state.auth_processed = False
        else:
            # Show login button
            auth_url = get_google_auth_url()
            
            if auth_url:
                st.markdown(f"""
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285F4;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        cursor: pointer;
                        width: 100%;
                        font-weight: 600;
                        margin-top: 10px;
                    ">
                        <span style="margin-right: 8px;">🔵</span> Sign in with Google
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Google OAuth not configured properly")
                st.info("""
                **Setup Instructions:**
                1. Go to https://console.cloud.google.com/
                2. Create OAuth 2.0 credentials (OAuth 2.0 Client ID)
                3. Add Authorized redirect URIs: `""" + config.GOOGLE_REDIRECT_URI + """`
                4. Download JSON and save as `google_credentials.json`
                5. Update OAuth consent screen app name to: **VoiceSnap**
                """)
        
        st.markdown("""
        <p style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
            🔒 We only access your name, email, and profile photo<br>
            ✅ No data sharing • No spam • 100% secure
        </p>
        """, unsafe_allow_html=True)

# ============================================================================
# MAIN INTERFACE WITH GLOBAL SEARCH
# ============================================================================

def render_main_interface():
    """Main interface after login"""
    
    # Header
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="header-card">
            <h2 style="margin: 0;">👋 Hey, {st.session_state.user['name']}!</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Ready to hang out?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.in_call = False
            st.session_state.auth_processed = False
            st.rerun()
    
    # GLOBAL SEARCH BAR
    st.markdown("### 🔍 Search Users Worldwide")
    search_query = st.text_input(
        "Search by name or email",
        placeholder="Type name or email to find users...",
        label_visibility="collapsed"
    )
    
    # Search results
    if search_query and len(search_query) > 2:
        results = db.search_users(search_query, exclude_user_id=st.session_state.user['id'])
        
        if results:
            st.markdown(f"**Found {len(results)} users:**")
            for user in results:
                render_search_result(user)
        else:
            st.info("No users found. Be the first to invite your friends!")
    
    st.markdown("---")
    
    # Tabs for Friends and Groups
    tab1, tab2 = st.tabs(["👥 Friends", "🎯 Groups"])
    
    with tab1:
        render_friends_list()
    
    with tab2:
        render_groups_list()

def render_search_result(user):
    """Render search result with instant call button"""
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        st.image(user['avatar_url'], width=60)
    
    with col2:
        status_class = f"status-{user.get('status', 'offline')}"
        st.markdown(f"""
        <div>
            <div style="font-weight: 600; font-size: 16px;">{user['name']}</div>
            <div style="font-size: 14px; color: #666;">
                <span class="status-dot {status_class}"></span>{user['email']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        is_friend = db.is_friend(st.session_state.user['id'], user['id'])
        
        if is_friend:
            if user.get('status') == 'available':
                if st.button("📞 Call Now", key=f"call_{user['id']}", use_container_width=True, type="primary"):
                    start_call_with_user(user)
            elif user.get('status') == 'busy':
                if st.button("👥 Join Call", key=f"join_{user['id']}", use_container_width=True):
                    join_user_call(user)
            else:
                st.button("💤 Offline", key=f"off_{user['id']}", disabled=True, use_container_width=True)
        else:
            if st.button("➕ Add Friend", key=f"add_{user['id']}", use_container_width=True):
                if db.add_friend(st.session_state.user['id'], user['email']):
                    st.success(f"✅ Added {user['name']} as friend!")
                    time.sleep(1)
                    st.rerun()

def render_friends_list():
    """Friends list"""
    st.markdown("### Your Friends")
    
    friends = db.get_user_friends(st.session_state.user['id'])
    
    if not friends:
        st.info("👥 No friends yet. Use search above to find friends!")
        return
    
    for friend_data in friends:
        friend = friend_data['friend']
        
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.image(friend['avatar_url'], width=60)
        
        with col2:
            status = friend.get('status', 'offline')
            status_class = f"status-{status}"
            st.markdown(f"""
            <div>
                <div style="font-weight: 600; font-size: 16px;">{friend['name']}</div>
                <div style="font-size: 14px; color: #666;">
                    <span class="status-dot {status_class}"></span>{status.capitalize()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if status == 'available':
                if st.button("📞 Call", key=f"fcall_{friend['id']}", use_container_width=True, type="primary"):
                    start_call_with_user(friend)
            elif status == 'busy':
                if st.button("👥 Join", key=f"fjoin_{friend['id']}", use_container_width=True):
                    join_user_call(friend)
            else:
                st.button("💤 Offline", key=f"foff_{friend['id']}", disabled=True, use_container_width=True)

def render_groups_list():
    """Groups list"""
    st.markdown("### Your Groups")
    
    groups = db.get_user_groups(st.session_state.user['id'])
    
    if not groups:
        st.info("🎯 No groups yet")
        return
    
    for group in groups:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.markdown(f"""
            <div style="width: 60px; height: 60px; border-radius: 12px; background: linear-gradient(135deg, #f093fb, #f5576c); 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px;">
                {group['name'][0]}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div>
                <div style="font-weight: 600; font-size: 16px;">{group['name']}</div>
                <div style="font-size: 14px; color: #666;">{group.get('member_count', 0)} members</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("📞 Start Group Call", key=f"group_{group['id']}", use_container_width=True):
                start_group_call(group)

# ============================================================================
# CALL FUNCTIONS
# ============================================================================

def start_call_with_user(user):
    """Start 1:1 call with a user"""
    with st.spinner(f"Calling {user['name']}..."):
        room = daily.create_room(max_participants=2)
        
        if room:
            st.session_state.current_room = room['name']
            st.session_state.room_url = room['url']
            st.session_state.in_call = True
            db.update_user_status(st.session_state.user['id'], 'busy', room['name'])
            st.rerun()

def join_user_call(user):
    """Join user's active call"""
    if user.get('room_id'):
        st.session_state.current_room = user['room_id']
        st.session_state.room_url = f"https://{user['room_id']}.daily.co/{user['room_id']}"
        st.session_state.in_call = True
        db.update_user_status(st.session_state.user['id'], 'busy', user['room_id'])
        st.rerun()

def start_group_call(group):
    """Start group call"""
    with st.spinner(f"Starting {group['name']}..."):
        room = daily.create_room(max_participants=100)
        
        if room:
            st.session_state.current_room = room['name']
            st.session_state.room_url = room['url']
            st.session_state.in_call = True
            db.update_user_status(st.session_state.user['id'], 'busy', room['name'])
            st.rerun()

# ============================================================================
# CALL INTERFACE
# ============================================================================

def render_call_interface():
    """Active call interface"""
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="call-header">
            <h3 style="margin: 0;">🎙️ Active Call</h3>
            <p style="margin: 5px 0 0 0; color: #666;">Room: <code>{st.session_state.current_room}</code></p>
            <p style="margin: 5px 0 0 0; color: #22c55e; font-size: 14px;">🔊 Audio-only mode</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📞 End Call", use_container_width=True, type="primary"):
            end_call()
    
    if st.session_state.room_url:
        try:
            token = daily.create_meeting_token(
                st.session_state.current_room,
                st.session_state.user['name'],
                is_owner=True
            )
        except:
            token = None
        
        if token:
            url = f"{st.session_state.room_url}?t={token}&videoOff=true&showLocalVideo=false"
        else:
            url = f"{st.session_state.room_url}?videoOff=true&showLocalVideo=false"
        
        st.markdown(f"""
        <iframe
            src="{url}"
            allow="microphone; fullscreen"
            style="width: 100%; height: 600px; border: 1px solid #e0e0e0; border-radius: 12px;"
        ></iframe>
        """, unsafe_allow_html=True)
        
        st.success("✅ Audio-only mode • No video • Crystal clear quality")

def end_call():
    """End call and return home"""
    try:
        daily.delete_room(st.session_state.current_room)
    except:
        pass
    
    db.update_user_status(st.session_state.user['id'], 'available', None)
    
    st.session_state.in_call = False
    st.session_state.current_room = None
    st.session_state.room_url = None
    
    st.success("Call ended. Returning home...")
    time.sleep(1)
    st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    if not config.DAILY_API_KEY:
        st.error("⚠️ Daily.co API key not configured!")
        st.stop()
    
    if not st.session_state.user:
        render_google_login()
    elif st.session_state.in_call:
        render_call_interface()
    else:
        render_main_interface()

if __name__ == "__main__":
    main()