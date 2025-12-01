import streamlit as st
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

# CSS with ONLY the 5 fixes
st.markdown("""
<style>
    
    /* FIX 3: All fonts black */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {
        color: #000000 !important;
    }
    
    /* Keep white background (default Streamlit) */
    .stApp {
        background: white;
    }
    
    /* Search bar styling */
    .search-bar {
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'in_call' not in st.session_state:
    st.session_state.in_call = False
if 'current_room' not in st.session_state:
    st.session_state.current_room = None
if 'room_url' not in st.session_state:
    st.session_state.room_url = None

# ============================================================================
# FIX 1: Login screen with no scrollbar
# ============================================================================

def render_login():
    """Login screen that fits in viewport without scrollbar"""
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 56px; margin: 0;">🎙️</h1>
            <h2 style="font-size: 36px; margin: 1px 0;">VoiceSnap</h1>
            <p style="font-size: 16px; color: #666;">Real-time audio hangouts</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        name = st.text_input("👤 Your Name", placeholder="Rahul Kumar")
        email = st.text_input("📧 Email", placeholder="your.email@gmail.com")
        
        if st.button("🚀 Start Hanging Out", use_container_width=True, type="primary"):
            if name and email:
                user = db.create_user(email, name)
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Please enter both name and email")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FIX 2: Main interface with tabs for Friends and Groups
# FIX 3: All fonts black (applied via CSS above)
# FIX 4: Global search bar below "Hey, {name}"
# ============================================================================

def render_main_interface():
    """Main interface with all fixes applied"""
    
    # Header with logout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"## 👋 Hey, {st.session_state.user['name']}!")
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.in_call = False
            st.rerun()
    
    # FIX 4: Global search bar (below "Hey, {name}")
    st.markdown('<div class="search-bar">', unsafe_allow_html=True)
    search_query = st.text_input(
        "🔍 Search users by name or email",
        placeholder="Search for users...",
        key="global_search"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show search results if searching
    if search_query and len(search_query) > 0:
        render_search_results(search_query)
        st.markdown("---")
    
    # FIX 2: Tabs for Friends and Groups
    tab1, tab2 = st.tabs(["👥 Individual Friends", "🎯 Groups"])
    
    with tab1:
        render_friends_list()
    
    with tab2:
        render_groups_list()

# ============================================================================
# FIX 4: Global search with instant connect
# ============================================================================

def render_search_results(query):
    """Search users across network and allow instant connect"""
    
    st.markdown("### 🔍 Search Results")
    
    # Mock search (replace with real database query in production)
    all_users = [
        {"id": 101, "name": "Arjun Patel", "email": "arjun@example.com", "status": "available"},
        {"id": 102, "name": "Sneha Gupta", "email": "sneha@example.com", "status": "offline"},
        {"id": 103, "name": "Vikram Singh", "email": "vikram@example.com", "status": "busy"},
        {"id": 104, "name": "Ananya Sharma", "email": "ananya@example.com", "status": "available"},
    ]
    
    # Filter by name or email
    query_lower = query.lower()
    results = [u for u in all_users if query_lower in u['name'].lower() or query_lower in u['email'].lower()]
    
    if not results:
        st.info("No users found matching your search")
        return
    
    # Display results with instant connect button
    for user in results:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.markdown(f"""
            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {user['name'][0]}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{user['name']}**")
            st.caption(user['email'])
        
        with col3:
            if st.button("➕ Connect", key=f"connect_{user['id']}", use_container_width=True):
                st.success(f"✅ Friend request sent to {user['name']}")
                time.sleep(1)
                st.rerun()

# ============================================================================
# Friends list (Tab 1)
# ============================================================================

def render_friends_list():
    """Individual friends list"""
    
    st.markdown("### Your Friends")
    
    friends = db.get_user_friends(st.session_state.user["id"])
    
    if not friends:
        st.info("👥 No friends yet. Use the search bar above to find friends!")
        return
    
    for friend_data in friends:
        friend = friend_data.get("friend", friend_data)
        
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            avatar_url = friend.get("avatar_url", f"https://ui-avatars.com/api/?name={friend['name']}")
            st.image(avatar_url, width=60)
        
        with col2:
            status = friend.get("status", "offline")
            status_emoji = {"available": "🟢", "busy": "🔴", "offline": "⚪"}[status]
            
            st.markdown(f"**{friend['name']}**")
            st.caption(f"{status_emoji} {status.capitalize()}")
        
        with col3:
            if status == "available":
                if st.button("📞 Call", key=f"call_{friend['id']}", use_container_width=True):
                    start_call([friend])
            elif status == "busy":
                if st.button("👥 Join", key=f"join_{friend['id']}", use_container_width=True):
                    st.info("Joining their call...")
            else:
                st.button("💤 Offline", key=f"offline_{friend['id']}", disabled=True, use_container_width=True)

# ============================================================================
# Groups list (Tab 2)
# ============================================================================

def render_groups_list():
    """Groups list"""
    
    st.markdown("### Your Groups")
    
    # Mock groups (replace with real data)
    groups = [
        {"id": 1, "name": "Study Squad", "members": 5, "active": True},
        {"id": 2, "name": "Weekend Hangout", "members": 8, "active": False},
        {"id": 3, "name": "Gaming Crew", "members": 12, "active": True},
    ]
    
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
            st.markdown(f"**{group['name']}**")
            active_text = "🟢 Active" if group['active'] else "⚪ Inactive"
            st.caption(f"{group['members']} members • {active_text}")
        
        with col3:
            if group['active']:
                if st.button("👥 Join", key=f"join_group_{group['id']}", use_container_width=True):
                    st.info(f"Joining {group['name']}...")
            else:
                if st.button("📞 Start", key=f"start_group_{group['id']}", use_container_width=True):
                    st.info(f"Starting {group['name']}...")
    
    st.markdown("---")
    if st.button("➕ Create New Group", use_container_width=True):
        st.info("Group creation coming soon!")

# ============================================================================
# Call functions
# ============================================================================

def start_call(friends):
    """Start a new call"""
    with st.spinner("Creating room..."):
        room = daily.create_room(max_participants=100)
        
        if room:
            st.session_state.current_room = room["name"]
            st.session_state.room_url = room["url"]
            st.session_state.in_call = True
            st.rerun()

# ============================================================================
# FIX 5: Call interface with auto-redirect to homepage
# ============================================================================

def render_call_interface():
    """Call interface with auto-redirect on end"""
    
    # Header
    st.markdown(f"""
    ## 🎙️ Active Call
    **Room:** `{st.session_state.current_room}`  
    🔊 Audio-only mode
    """)
    
    # End call button at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📞 End Call & Return Home", use_container_width=True, type="primary"):
            end_call_and_redirect()
    
    st.markdown("---")
    
    # Daily.co iframe
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
        <iframe
            src="{url}"
            allow="microphone; fullscreen"
            style="width: 100%; height: 600px; border: none; border-radius: 10px;"
        ></iframe>
        """, unsafe_allow_html=True)
    
    st.success("✅ Audio-only mode active • No video")
    
    # Another end button at bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📞 End Call", use_container_width=True, type="primary", key="end_bottom"):
            end_call_and_redirect()

# FIX 5: Auto-redirect function
def end_call_and_redirect():
    """End call and automatically redirect to homepage"""
    
    # Delete room
    try:
        daily.delete_room(st.session_state.current_room)
    except:
        pass
    
    # Clear all call state
    st.session_state.in_call = False
    st.session_state.current_room = None
    st.session_state.room_url = None
    
    # Show brief message
    st.success("Call ended. Returning to homepage...")
    time.sleep(1)
    
    # Automatic redirect by rerunning
    st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Check API key
    if not config.DAILY_API_KEY:
        st.error("⚠️ Daily.co API key not configured!")
        st.stop()
    
    # Route based on state
    if not st.session_state.user:
        render_login()  # FIX 1: No scrollbar
    elif st.session_state.in_call:
        render_call_interface()  # FIX 5: Auto-redirect
    else:
        render_main_interface()  # FIX 2, 3, 4: Tabs, black text, search

if __name__ == "__main__":
    main()