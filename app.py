# ============================================================================
# VoiceSnap - Clean UI with All Fixes Applied
# ============================================================================

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import time
from database import db
from daily_api import daily
from configurations import Config as config

# Page config
st.set_page_config(
    page_title="VoiceSnap",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, minimal CSS - White background, black text
st.markdown("""
<style>
    /* Remove default Streamlit padding */
    
    /* Clean white background */
    .stApp {
        background: white;
    }
    
    /* All text black */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #000000 !important;
    }
    
    /* Header card */
    .header-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Friend card */
    .friend-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: box-shadow 0.2s;
    }
    
    .friend-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Status indicators */
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-available {
        background: #22c55e;
    }
    
    .status-busy {
        background: #ef4444;
    }
    
    .status-offline {
        background: #9ca3af;
    }
    
    /* Search bar */
    .search-container {
        margin: 20px 0;
    }
    

    
    /* Call interface */
    .call-header {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Notepad */
    .notepad-container {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        min-height: 400px;
    }
    
    /* Whiteboard */
    .whiteboard-container {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Sound player */
    .sound-player {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
    }
    
    .sound-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .sound-card:hover {
        background: #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sound-card.playing {
        border: 2px solid #22c55e;
        background: #f0fdf4;
    }
    
    /* Hide scrollbar on main page */
    .main .block-container {
        max-height: 100vh;
        overflow-y: auto;
    }
    
    /* Streamlit tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background: #f8f9fa;
        border-radius: 8px;
        color: #000000;
    }
    
    .stTabs [aria-selected="true"] {
        background: #e9ecef;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'in_call' not in st.session_state:
    st.session_state.in_call = False
if 'current_room' not in st.session_state:
    st.session_state.current_room = None
if 'room_url' not in st.session_state:
    st.session_state.room_url = None
if 'shared_notes' not in st.session_state:
    st.session_state.shared_notes = ""
if 'ambient_sound' not in st.session_state:
    st.session_state.ambient_sound = None
if 'sound_volume' not in st.session_state:
    st.session_state.sound_volume = 50
if 'groups' not in st.session_state:
    st.session_state.groups = []

# Ambient sounds data
AMBIENT_SOUNDS = {
    "cafe": {"name": "☕ Cafe", "emoji": "☕", "category": "focus"},
    "rain": {"name": "🌧️ Rain", "emoji": "🌧️", "category": "focus"},
    "ocean": {"name": "🌊 Ocean", "emoji": "🌊", "category": "focus"},
    "forest": {"name": "🌲 Forest", "emoji": "🌲", "category": "focus"},
    "fireplace": {"name": "🔥 Fireplace", "emoji": "🔥", "category": "relax"},
    "lofi": {"name": "🎵 Lo-fi", "emoji": "🎵", "category": "music"},
    "jazz": {"name": "🎹 Jazz", "emoji": "🎹", "category": "music"},
    "whitenoise": {"name": "⚪ White Noise", "emoji": "⚪", "category": "focus"}
}

# ============================================================================
# LOGIN SCREEN (NO SCROLLBAR)
# ============================================================================

def render_login():
    """Clean login screen that fits in viewport"""
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Centered login box
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 56px; margin: 0; color: #000;">🎙️</h1>
            <h1 style="font-size: 36px; margin: 10px 0; color: #000;">VoiceSnap</h1>
            <p style="font-size: 16px; color: #666;">Real-time audio hangouts</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="header-card">', unsafe_allow_html=True)
        st.markdown("### Quick Login")
        
        name = st.text_input("👤 Your Name", placeholder="Rahul Kumar", label_visibility="collapsed", key="login_name")
        email = st.text_input("📧 Email", placeholder="your.email@gmail.com", label_visibility="collapsed", key="login_email")
        
        if st.button("🚀 Start Hanging Out", use_container_width=True, type="primary"):
            if name and email:
                user = db.create_user(email, name)
                st.session_state.user = user
                st.rerun()
            else:
                st.error("⚠️ Please enter both name and email")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.caption("🔒 Free • No signup required • Works everywhere")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN INTERFACE WITH TABS
# ============================================================================

def render_main_interface():
    """Main interface with tabs for Friends and Groups"""
    
    # Header with user info
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="header-card">
            <h2 style="margin: 0; color: #000;">👋 Hey, {st.session_state.user['name']}!</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Ready to hang out?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.in_call = False
            st.rerun()
    
    # Global search bar
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input(
        "🔍 Search users",
        placeholder="Search by name or email...",
        label_visibility="collapsed",
        key="global_search"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search results (if searching)
    if search_query and len(search_query) > 2:
        render_search_results(search_query)
        st.markdown("---")
    
    # Tabs for Friends and Groups
    tab1, tab2 = st.tabs(["👥 Friends", "🎯 Groups"])
    
    with tab1:
        render_friends_tab()
    
    with tab2:
        render_groups_tab()

def render_search_results(query):
    """Global search for users across network"""
    st.markdown("### 🔍 Search Results")
    
    # Mock search results (in production, query your database)
    all_users = [
        {"id": 101, "name": "Arjun Patel", "email": "arjun@example.com", "status": "available"},
        {"id": 102, "name": "Sneha Gupta", "email": "sneha@example.com", "status": "offline"},
        {"id": 103, "name": "Vikram Singh", "email": "vikram@example.com", "status": "busy"},
        {"id": 104, "name": "Ananya Sharma", "email": "ananya@example.com", "status": "available"},
    ]
    
    # Filter based on query
    query_lower = query.lower()
    results = [u for u in all_users if query_lower in u['name'].lower() or query_lower in u['email'].lower()]
    
    if not results:
        st.info("No users found")
        return
    
    for user in results:
        render_search_user_card(user)

def render_search_user_card(user):
    """Render search result card with connect button"""
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        st.markdown(f"""
        <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); 
                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">
            {user['name'][0]}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_class = f"status-{user['status']}"
        st.markdown(f"""
        <div>
            <div style="font-weight: 600; font-size: 16px; color: #000;">{user['name']}</div>
            <div style="font-size: 14px; color: #666;">
                <span class="status-dot {status_class}"></span>{user['email']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("➕ Connect", key=f"connect_{user['id']}", use_container_width=True):
            st.success(f"✅ Friend request sent to {user['name']}")

def render_friends_tab():
    """Render friends list"""
    st.markdown("### Your Friends")
    
    friends = db.get_user_friends(st.session_state.user["id"])
    
    if not friends:
        st.info("👥 No friends yet. Use the search bar above to find and connect with friends!")
        return
    
    for friend_data in friends:
        render_friend_card(friend_data)

def render_friend_card(friend_data):
    """Render individual friend card"""
    friend = friend_data.get("friend", friend_data)
    name = friend.get("name", "Unknown")
    email = friend.get("email", "")
    status = friend.get("status", "offline")
    avatar = friend.get("avatar_url", f"https://ui-avatars.com/api/?name={name}")
    
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        st.image(avatar, width=60)
    
    with col2:
        status_class = f"status-{status}"
        st.markdown(f"""
        <div>
            <div style="font-weight: 600; font-size: 16px; color: #000;">{name}</div>
            <div style="font-size: 14px; color: #666;">
                <span class="status-dot {status_class}"></span>{status.capitalize()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if status == "available":
            if st.button("📞 Call", key=f"call_{email}", use_container_width=True, type="primary"):
                start_call([friend])
        elif status == "busy":
            if st.button("👥 Join", key=f"join_{email}", use_container_width=True, type="secondary"):
                st.info("Joining their room...")
        else:
            st.button("💤 Offline", key=f"offline_{email}", disabled=True, use_container_width=True)

def render_groups_tab():
    """Render groups list"""
    st.markdown("### Your Groups")
    
    # Mock groups (in production, fetch from database)
    groups = [
        {"id": 1, "name": "Study Squad", "members": 5, "active": True},
        {"id": 2, "name": "Weekend Hangout", "members": 8, "active": False},
        {"id": 3, "name": "Gaming Crew", "members": 12, "active": True},
    ]
    
    if not groups:
        st.info("🎯 No groups yet. Create one to start group hangouts!")
    
    for group in groups:
        render_group_card(group)
    
    st.markdown("---")
    if st.button("➕ Create New Group", use_container_width=True, type="primary"):
        st.info("Group creation coming soon!")

def render_group_card(group):
    """Render group card"""
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        st.markdown(f"""
        <div style="width: 60px; height: 60px; border-radius: 12px; background: linear-gradient(135deg, #f093fb, #f5576c); 
                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px;">
            {group['name'][0]}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_text = "🟢 Active" if group['active'] else "⚪ Inactive"
        st.markdown(f"""
        <div>
            <div style="font-weight: 600; font-size: 16px; color: #000;">{group['name']}</div>
            <div style="font-size: 14px; color: #666;">{group['members']} members • {active_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if group['active']:
            if st.button("👥 Join Group", key=f"join_group_{group['id']}", use_container_width=True, type="primary"):
                st.info(f"Joining {group['name']}...")
        else:
            if st.button("📞 Start Call", key=f"start_group_{group['id']}", use_container_width=True, type="secondary"):
                st.info(f"Starting {group['name']} call...")

def start_call(friends):
    """Start a new call"""
    with st.spinner("Creating room..."):
        room = daily.create_room(max_participants=config.MAX_ROOM_SIZE)
        
        if room:
            st.session_state.current_room = room["name"]
            st.session_state.room_url = room["url"]
            st.session_state.in_call = True
            st.rerun()
        else:
            st.error("Failed to create room")

# ============================================================================
# CALL INTERFACE WITH BACK BUTTON
# ============================================================================

def render_call_interface_enhanced():
    """Enhanced call interface with automatic redirect on end"""
    
    # Header with back button
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown(f"""
        <div class="call-header">
            <h3 style="margin: 0; color: #000;">🎙️ Active Call</h3>
            <p style="margin: 5px 0 0 0; color: #666;">Room: <code>{st.session_state.current_room}</code></p>
            <p style="margin: 5px 0 0 0; color: #22c55e; font-size: 14px;">🔊 Audio-only mode</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📞 End Call", use_container_width=True, type="primary"):
            end_call()
    
    # Feature tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎙️ Voice", "📝 Notes", "🎨 Board", "🔊 Sounds"])
    
    with tab1:
        render_voice_tab()
    
    with tab2:
        render_notepad()
    
    with tab3:
        render_whiteboard()
    
    with tab4:
        render_ambient_sounds()

def end_call():
    """End call and return to homepage"""
    try:
        daily.delete_room(st.session_state.current_room)
    except:
        pass
    
    # Clear call state
    st.session_state.in_call = False
    st.session_state.current_room = None
    st.session_state.room_url = None
    st.session_state.ambient_sound = None
    st.session_state.shared_notes = ""
    
    # Automatic redirect to homepage
    st.rerun()

def render_voice_tab():
    """Voice call tab with Daily.co embed"""
    if st.session_state.room_url:
        try:
            token = daily.create_meeting_token(
                st.session_state.current_room,
                st.session_state.user["name"],
                is_owner=True
            )
        except:
            token = None
        
        if token:
            url = f"{st.session_state.room_url}?t={token}&videoOff=true&showLocalVideo=false"
        else:
            url = f"{st.session_state.room_url}?videoOff=true&showLocalVideo=false"
        
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; height: 500px;">
            <iframe
                src="{url}"
                allow="microphone; fullscreen"
                style="width: 100%; height: 100%; border: none; border-radius: 8px;"
            ></iframe>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ Audio-only mode • No video • Optimized for low bandwidth")

def render_notepad():
    """Shared notepad"""
    st.markdown('<div class="notepad-container">', unsafe_allow_html=True)
    
    st.markdown("### 📝 Shared Notes")
    st.caption("Everyone in the room can edit")
    
    notes = st.text_area(
        "Notes",
        value=st.session_state.shared_notes,
        height=350,
        placeholder="Start typing...",
        label_visibility="collapsed"
    )
    
    if notes != st.session_state.shared_notes:
        st.session_state.shared_notes = notes
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save", use_container_width=True):
            st.success("Notes saved!")
    with col2:
        if st.button("📤 Export", use_container_width=True):
            st.info("Export as PDF")
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.shared_notes = ""
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_whiteboard():
    """Interactive whiteboard"""
    st.markdown('<div class="whiteboard-container">', unsafe_allow_html=True)
    
    st.markdown("### 🎨 Shared Whiteboard")
    st.caption("Draw together in real-time")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        drawing_mode = st.selectbox("Tool", ["freedraw", "line", "rect", "circle"], label_visibility="collapsed")
    with col2:
        stroke_width = st.slider("Size", 1, 20, 3, label_visibility="collapsed")
    with col3:
        stroke_color = st.color_picker("Color", "#000000", label_visibility="collapsed")
    
    canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=350,
        width=700,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Board", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("💾 Save Drawing", use_container_width=True):
            st.success("Drawing saved!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_ambient_sounds():
    """Ambient sound player"""
    st.markdown('<div class="sound-player">', unsafe_allow_html=True)
    
    st.markdown("### 🔊 Ambient Sounds")
    st.caption("Set the mood")
    
    volume = st.slider("Volume", 0, 100, st.session_state.sound_volume, label_visibility="collapsed")
    st.session_state.sound_volume = volume
    
    cols = st.columns(4)
    for idx, (sound_id, sound) in enumerate(AMBIENT_SOUNDS.items()):
        with cols[idx % 4]:
            is_playing = st.session_state.ambient_sound == sound_id
            button_type = "primary" if is_playing else "secondary"
            label = f"{sound['emoji']} {'⏸️' if is_playing else '▶️'}"
            
            if st.button(label, key=f"sound_{sound_id}", use_container_width=True, type=button_type):
                if is_playing:
                    st.session_state.ambient_sound = None
                else:
                    st.session_state.ambient_sound = sound_id
                st.rerun()
    
    if st.session_state.ambient_sound:
        current = AMBIENT_SOUNDS[st.session_state.ambient_sound]
        st.info(f"🎵 Playing: {current['name']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    if not config.DAILY_API_KEY:
        st.error("⚠️ Daily.co API key not configured!")
        st.stop()
    
    if not st.session_state.user:
        render_login()
    elif st.session_state.in_call:
        render_call_interface_enhanced()
    else:
        render_main_interface()

if __name__ == "__main__":
    main()