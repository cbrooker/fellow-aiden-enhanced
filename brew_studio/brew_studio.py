import streamlit as st
from fellow_aiden import FellowAiden
from fellow_aiden.profile import CoffeeProfile
from openai import OpenAI
from config_manager import ConfigManager
import json
import os
from datetime import datetime
from pathlib import Path

SYSTEM = """
Assume the role of a master coffee brewer. You focus exclusively on the pour over method and specialty coffee only. You often work with single origin coffees, but you also experiment with blends. Your recipes are executed by a robot, not a human, so maximum precision can be achieved. Temperatures are all maintained and stable in all steps. Always lead with the recipe, and only include explanations below that text, NOT inline. Below are the components of a recipe. 

Core brew settings: These settings are static and must match for single and batch brew.
Title: An interesting and creative name based on the coffee details. 
Ratio: How much coffee per water. Values MUST be between 14 and 20 with 0.5 step increments.
Bloom ratio: Water to use in bloom stage. Values MUST be between 1 and 3 with 0.5 step increments.
Bloom time: How long the bloom phase should last. Values MUST be between 1 and 120 seconds.
Bloom temperature: Temperature of the water. Values MUST be between 50 and 99 celsius.

Pulse settings: These are independent and can vary for single and batch brews. 
Number of pulses: Steps in which water is poured over coffee. Values MUST be between 1 and 10.
Time between pulses: Time in between each pulse. Values MUST be between 5 and 60 seconds. This MUST be included even if a single pulse is performed. 
Pulse temperate. Independent temperature to use for a given pulse.  Values MUST be between 50 and 99 celsius.

Below is an example of a previous recipe you put together for a speciality coffee called "Fruit cake" where you tasted cinnamon sugar, baked apples, and blackberry compote.

Roast: Light - Medium
Process | Cinnamon co-ferment | Strawberry co-ferment | Washed
33% Esteban Zamora - Cinnamon Anaerobic (San Marcos, Tarrazu, Costa Rica)
33% Sebastián Ramirez - Red Fruits (Quindio, Colombia)
33% Gamatui - Washed (Kapchorwa, Mt. Elgon, Uganda)

CORE
Ratio: 16
Bloom ratio: 3
Bloom time: 60s
Bloom temp: 87.5°C

SINGLE SERVE
Pulse 1 temp: 95°C
Pulse 2 temp: 92.5°C
Time between pulses: 25s
Number of pulses: 2 

BATCH
Pulse 1 temp: 95°C
Pulse 2 temp: 92.5°C
Time between pulses: 25s
Number of pulses: 2 

Here's another example. This coffee is a bold and intense cup composed of a smooth blend of Burundian and Latin American coffees with notes of mulled wine, baker's chocolate, blood orange, and a delicious blast of fudge.

Roast: Light - Medium
Process: Natural and Washed
Region: Burundi, Honduras and Peru
CORE
Ratio: 16
Bloom ratio: 2.5  
Bloom time: 30s
Bloom temp: 93.5°C 

SINGLE SERVE
Pulse 1 temp: 92°C
Pulse 2 temp: 92°C
Pulse 3 temp: 90.5°C 
Time between pulses: 20s
Number of pulses: 3 

BATCH
Pulse temp: 92°C 
Number of pulses: 1
"""    

REFORMAT_SYSTEM = """
Assume the role of a data engineer. You need to parse coffee recipes and their explanations so the data can be structured. Below are the important components of the recipe.

Core brew settings: These settings are static and must match for single and batch brew.
Title: An interesting and creative name based on the coffee details. 
Ratio: How much coffee per water. Values range from 1:14 to 1:20 with 0.5 steps.
Bloom ratio: Water to use in bloom stage. Values range from 1 to 3 with 0.5 steps.
Bloom time: How long the bloom phase should last. Values range from 1 to 120 seconds.
Bloom temperature: Temperature of the water. Values range from 50 celsius to 99 celsius.

Pulse settings: These are independent and can vary for single and batch brews. 
Number of pulses: Steps in which water is poured over coffee. Values range from 1 to 10.
Time between pulses: Time in between each pulse. Values range from 5 to 60 seconds. This must be included even if a single pulse is performed. 
Pulse temperate. Independent temperature to use for a given pulse.  Values range from 50 celsius to 99 celsius. 
"""


# ------------------------------------------------------------------------------
# Mock / Placeholder functions
# ------------------------------------------------------------------------------
def connect_to_coffee_brewer(email, password):
    """Mock function returning a list of profile dicts."""
    email = email.strip()
    password = password.strip()

    if 'aiden' not in st.session_state:
        try:
            local = FellowAiden(email, password)
            st.session_state['aiden'] = local
        except Exception as e:
            if "incorrect" in str(e):
                return False
            # Re-raise other exceptions
            raise

    obj = {
        'device_settings': {
            'name': st.session_state['aiden'].get_display_name(),
        },
        # Make sure each profile has "description" if your mock doesn't already:
        'profiles': [
            {
                **p,
                **{"description": p.get("description", "")}
            }
            for p in st.session_state['aiden'].get_profiles()
        ]
    }
    return obj

def save_profile_to_coffee_machine(profile_name, updated_profile):
    st.success(f"Profile '{profile_name}' saved.")
    if 'description' in updated_profile:
        updated_profile.pop('description', None)
    updated_profile['profileType'] = 0
    
    try:
        # Check if a profile with this name already exists
        existing_profile = st.session_state['aiden'].get_profile_by_title(profile_name)
        
        if existing_profile:
            # If profile exists, update it
            profile_id = existing_profile['id']
            st.session_state['aiden'].update_profile(profile_id, updated_profile)
        else:
            # If profile doesn't exist, create a new one
            st.session_state['aiden'].create_profile(updated_profile)
    except Exception as e:
        st.warning(f"Failed to save profile: {e}")

def parse_brewlink(link):
    """Returns a dict with all profile fields parsed from the link."""
    parsed = st.session_state['aiden'].parse_brewlink_url(link)
    # Add a 'description' key if not present:
    if 'description' not in parsed:
        parsed['description'] = ""
    return parsed


def extract_recipe_from_description(model_explanation):
    """Extracts the recipe from the description."""
    try:
        completion = st.session_state['oai'].beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": REFORMAT_SYSTEM},
                {"role": "user", "content": model_explanation},
            ],
            response_format=CoffeeProfile,
        )
        model_recipe = completion.choices[0].message.parsed
    except Exception as e:
        print("Failed to extract recipe from description:", e)
        return False
    
    return model_recipe


def generate_ai_recipe_and_explanation(USER):
    guidance = "Suggest a recipe for the following coffee. Provide your explanations below the recipe.\n"
    USER = ' '.join([guidance, USER])
    completion = st.session_state['oai'].chat.completions.create(
        model="o1-preview",
        messages=[
            {"role": "user", "content": SYSTEM + USER},
        ]
    )
    model_explanation = completion.choices[0].message.content
    print(model_explanation)

    while True:
        model_recipe = extract_recipe_from_description(model_explanation)
        if model_recipe:
            break

    recipe = model_recipe.model_dump()
    recipe['description'] = model_explanation
    return recipe


def get_share_link(title):
    profile = st.session_state['aiden'].get_profile_by_title(title)
    return st.session_state['aiden'].generate_share_link(profile['id'])

# ------------------------------------------------------------------------------
# Profile Management Functions
# ------------------------------------------------------------------------------
def get_backup_file_path():
    """Get the path for the profile backup file."""
    return Path("profile_backups.json")

def load_profile_backups():
    """Load profile backups from JSON file."""
    backup_file = get_backup_file_path()
    if backup_file.exists():
        try:
            with open(backup_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Could not load profile backups: {e}")
            return []
    return []

def save_profile_backup(profile):
    """Save a profile to the backup file."""
    backups = load_profile_backups()
    
    # Add timestamp and backup info
    backup_entry = {
        "backed_up_at": datetime.now().isoformat(),
        "profile": profile.copy()
    }
    
    backups.append(backup_entry)
    
    # Keep only the last 50 backups to prevent file from growing too large
    if len(backups) > 50:
        backups = backups[-50:]
    
    backup_file = get_backup_file_path()
    try:
        with open(backup_file, 'w') as f:
            json.dump(backups, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Could not save profile backup: {e}")
        return False

def delete_profile_with_backup(profile_id, profile_title):
    """Delete a profile and create a backup."""
    try:
        # Get the profile data before deletion
        profile = st.session_state['aiden'].get_profile_by_title(profile_title)
        if profile:
            # Save backup before deletion
            if save_profile_backup(profile):
                st.success(f"Profile '{profile_title}' backed up successfully")
            
            # Delete the profile
            st.session_state['aiden'].delete_profile_by_id(profile_id)
            st.success(f"Profile '{profile_title}' deleted successfully")
            
            # Refresh the session state
            st.session_state.brewer_settings = connect_to_coffee_brewer(
                st.session_state.get('email', ''), 
                st.session_state.get('password', '')
            )
            st.rerun()
        else:
            st.error("Profile not found")
    except Exception as e:
        st.error(f"Failed to delete profile: {e}")

def restore_profile_from_backup(backup_entry):
    """Restore a profile from backup."""
    try:
        profile_data = backup_entry["profile"].copy()
        
        # Remove server-side fields before creating
        server_fields = ['id', 'createdAt', 'deletedAt', 'lastUsedTime', 'sharedFrom', 
                        'isDefaultProfile', 'instantBrew', 'folder', 'duration', 'lastGBQuantity']
        for field in server_fields:
            profile_data.pop(field, None)
        
        # Add a timestamp to the title to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_title = profile_data.get('title', 'Restored Profile')
        profile_data['title'] = f"{original_title}_restored_{timestamp}"
        
        # Create the profile
        result = st.session_state['aiden'].create_profile(profile_data)
        if result:
            st.success(f"Profile '{profile_data['title']}' restored successfully")
            
            # Refresh the session state
            st.session_state.brewer_settings = connect_to_coffee_brewer(
                st.session_state.get('email', ''), 
                st.session_state.get('password', '')
            )
            st.rerun()
        else:
            st.error("Failed to restore profile")
    except Exception as e:
        st.error(f"Failed to restore profile: {e}")

# ------------------------------------------------------------------------------
# Navigation Functions
# ------------------------------------------------------------------------------
def render_navigation():
    """Render the top navigation menu."""
    if st.session_state.logged_in:
        st.markdown("### ☕ Fellow Aiden Brew Studio")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            if st.button("🏠 Dashboard", key="nav_dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with col2:
            if st.button("📋 Profile Manager", key="nav_profiles"):
                st.session_state.current_page = "profiles"
                st.rerun()
        
        with col3:
            if st.button("🤖 AI Barista", key="nav_ai"):
                st.session_state.current_page = "ai_barista"
                st.rerun()
        
        with col4:
            if st.button("🔗 Brew Links", key="nav_links"):
                st.session_state.current_page = "brew_links"
                st.rerun()
        
        with col5:
            if st.button("📦 Backups", key="nav_backups"):
                st.session_state.current_page = "backups"
                st.rerun()
        
        with col6:
            if st.button("⚙️ Settings", key="nav_settings"):
                st.session_state.current_page = "settings"
                st.rerun()
        
        with col7:
            if st.button("🚪 Logout", key="nav_logout"):
                st.session_state.logged_in = False
                st.session_state.current_page = "login"
                st.session_state.pop('aiden', None)
                st.session_state.pop('brewer_settings', None)
                st.rerun()
        
        st.markdown("---")

def render_login_page():
    """Render the login page."""
    st.markdown("# ☕ Fellow Aiden Brew Studio")
    st.markdown("### Connect to your Fellow Aiden Coffee Brewer")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Fellow Account Credentials")
        
        saved_email = config_manager.get_fellow_email()
        email = st.text_input(
            "Email Address", 
            value=saved_email,
            placeholder="your@email.com"
        )
        
        saved_password = config_manager.get_fellow_password()
        password = st.text_input(
            "Password", 
            value=saved_password,
            type="password",
            placeholder="Your Fellow password"
        )
        
        st.markdown("")
        
        if st.button("🔌 Connect to Brewer", type="primary", use_container_width=True):
            if email and password:
                with st.spinner("Connecting to your Fellow Aiden brewer..."):
                    result = connect_to_coffee_brewer(email, password)
                    if result:
                        st.session_state.brewer_settings = result
                        st.session_state.logged_in = True
                        st.session_state.current_page = "dashboard"
                        # Save email for next time
                        if email != saved_email:
                            config_manager.save_fellow_email(email)
                        st.success("✅ Successfully connected!")
                        st.rerun()
                    else:
                        st.error("❌ Connection failed. Please check your credentials.")
            else:
                st.warning("⚠️ Please enter both email and password.")
        
        st.markdown("---")
        st.markdown("**Configuration Sources:**")
        config_info = config_manager.get_config_info()
        for info in config_info:
            st.write(f"• {info}")

# ------------------------------------------------------------------------------
# Page Rendering Functions  
# ------------------------------------------------------------------------------
def render_dashboard():
    """Render the main dashboard."""
    st.markdown("## 🏠 Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Brewer Information")
        device_info = st.session_state.brewer_settings["device_settings"]
        for k, v in device_info.items():
            st.write(f"**{k.replace('_', ' ').title()}**: {v}")
    
    with col2:
        st.markdown("### 📊 Profile Overview")
        profiles = st.session_state.brewer_settings["profiles"]
        profile_count = len(profiles)
        
        # Profile count with visual indicator
        if profile_count >= 14:
            st.markdown(f"🔴 **{profile_count}/14 Profiles** (Full)")
            st.error("⚠️ Profile storage is full. Consider deleting unused profiles.")
        elif profile_count >= 12:
            st.markdown(f"🟡 **{profile_count}/14 Profiles** (Nearly Full)")
            st.warning("Getting close to the 14 profile limit.")
        else:
            st.markdown(f"🟢 **{profile_count}/14 Profiles**")
            st.success(f"You have {14 - profile_count} profile slots available.")
        
        # Quick stats
        backups = load_profile_backups()
        st.write(f"📦 **{len(backups)} Profile Backups** available")
        
        if profiles:
            # Sort profiles by lastUsedTime, handling None values and different types
            def get_sort_key(profile):
                last_used = profile.get('lastUsedTime')
                if last_used is None:
                    return 0  # Default to 0 for None values
                if isinstance(last_used, (int, float)):
                    return last_used  # Return numeric timestamp as-is
                return last_used  # Return string timestamp as-is
            
            recent_profiles = sorted(profiles, key=get_sort_key, reverse=True)[:3]
            st.markdown("**Recently Used Profiles:**")
            for profile in recent_profiles:
                st.write(f"• {profile['title']}")

def render_profile_manager():
    """Render the profile management page."""
    st.markdown("## 📋 Profile Manager")
    
    profiles = st.session_state.brewer_settings["profiles"]
    profile_count = len(profiles)
    
    # Profile count header
    if profile_count >= 14:
        st.markdown(f"🔴 **{profile_count}/14 Profiles** (Full)")
    elif profile_count >= 12:
        st.markdown(f"🟡 **{profile_count}/14 Profiles** (Nearly Full)")
    else:
        st.markdown(f"🟢 **{profile_count}/14 Profiles**")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Select Profile")
        titles = [p["title"] for p in profiles]
        
        choice = st.selectbox(
            "Choose a profile to edit:",
            ["— Select Profile —"] + titles,
            key="profile_manager_choice"
        )
        
        if choice != "— Select Profile —":
            selected_profile = profiles[titles.index(choice)]
            
            st.markdown("### Quick Actions")
            if st.button("🗑️ Delete Profile", key="quick_delete"):
                if st.session_state.get('confirm_quick_delete', False):
                    delete_profile_with_backup(selected_profile['id'], selected_profile['title'])
                    st.session_state.confirm_quick_delete = False
                else:
                    st.session_state.confirm_quick_delete = True
                    st.rerun()
                    
            if st.session_state.get('confirm_quick_delete', False):
                st.warning(f"⚠️ Really delete '{selected_profile['title']}'?")
                if st.button("Cancel", key="cancel_quick_delete"):
                    st.session_state.confirm_quick_delete = False
                    st.rerun()
            
            if st.button("🔗 Share Profile"):
                link = get_share_link(selected_profile["title"])
                if link:
                    st.success("Share link generated!")
                    st.code(link)
    
    with col2:
        if choice != "— Select Profile —":
            selected_index = titles.index(choice)
            profile_data = profiles[selected_index]
            render_profile_editor(profile_data, profile_key=f"manager_{selected_index}")
        else:
            st.markdown("### Profile Editor")
            st.info("👈 Select a profile from the list to edit it here.")

def render_ai_barista():
    """Render the AI Barista page."""
    st.markdown("## 🤖 AI Barista")
    st.markdown("Generate custom coffee profiles using AI based on your coffee description.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Configuration")
        saved_api_key = config_manager.get_openai_api_key()
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=saved_api_key,
            type="password",
            placeholder="sk-your-openai-api-key"
        )
        
        st.markdown("### Coffee Description")
        user_coffee_request = st.text_area(
            "Describe your coffee:",
            placeholder="Light roasted blend of washed (Sidama, Ethiopia) and gesha (Santa Barbara, Honduras) coffees",
            height=150
        )
        
        if st.button("🎯 Generate AI Profile", type="primary", use_container_width=True):
            if openai_api_key.strip():
                st.session_state['oai'] = OpenAI(api_key=openai_api_key)
                if user_coffee_request.strip():
                    try:
                        with st.spinner("AI is crafting your perfect brew profile..."):
                            new_profile_data = generate_ai_recipe_and_explanation(user_coffee_request)
                        st.session_state.ai_generated_profile = new_profile_data
                        st.success("🎉 AI profile generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate AI recipe: {e}")
                else:
                    st.warning("Please enter a coffee description first.")
            else:
                st.warning("Please enter an OpenAI API key first.")
    
    with col2:
        if st.session_state.get('ai_generated_profile'):
            st.markdown("### Generated Profile")
            render_profile_editor(st.session_state.ai_generated_profile, profile_key="ai_generated")
        else:
            st.markdown("### AI Profile Preview")
            st.info("👈 Generate an AI profile to see it here for editing and saving.")

def render_brew_links():
    """Render the Brew Links import page."""
    st.markdown("## 🔗 Brew Links")
    st.markdown("Import coffee profiles from shared Fellow Aiden brew links.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Import Profile")
        brew_link = st.text_input(
            "Brew Link",
            placeholder="https://fellow.co/p/abc123 or paste link here...",
            help="Paste a Fellow Aiden brew link to import the profile"
        )
        
        if st.button("📥 Import Profile", type="primary", use_container_width=True):
            if brew_link.strip():
                try:
                    with st.spinner("Importing profile from brew link..."):
                        new_profile_data = parse_brewlink(brew_link)
                    st.session_state.imported_profile = new_profile_data
                    st.success("✅ Profile imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to import profile: {e}")
            else:
                st.warning("Please enter a brew link first.")
    
    with col2:
        if st.session_state.get('imported_profile'):
            st.markdown("### Imported Profile")
            render_profile_editor(st.session_state.imported_profile, profile_key="imported")
        else:
            st.markdown("### Profile Preview")
            st.info("👈 Import a brew link to see the profile here for editing and saving.")

def render_backups():
    """Render the backup management page."""
    st.markdown("## 📦 Profile Backups")
    st.markdown("Manage your profile backups and restore deleted profiles.")
    
    backups = load_profile_backups()
    
    if backups:
        st.success(f"📦 {len(backups)} profile backups available")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Backup History")
            st.write(f"Showing last {min(len(backups), 20)} backups:")
            
            selected_backup = None
            for i, backup in enumerate(reversed(backups[-20:])):
                backup_date = datetime.fromisoformat(backup['backed_up_at']).strftime("%Y-%m-%d %H:%M")
                profile_title = backup['profile'].get('title', 'Unknown')
                
                if st.button(f"📄 {profile_title}", key=f"backup_select_{i}"):
                    st.session_state.selected_backup = backup
                    st.rerun()
                
                st.caption(f"Backed up: {backup_date}")
                st.markdown("---")
        
        with col2:
            if st.session_state.get('selected_backup'):
                backup = st.session_state.selected_backup
                st.markdown("### Backup Preview")
                
                profile_data = backup['profile'].copy()
                backup_date = datetime.fromisoformat(backup['backed_up_at']).strftime("%Y-%m-%d %H:%M:%S")
                
                st.info(f"**Backed up:** {backup_date}")
                st.write(f"**Title:** {profile_data.get('title', 'Unknown')}")
                st.write(f"**Description:** {profile_data.get('description', 'No description')[:100]}...")
                
                if st.button("🔄 Restore This Profile", type="primary"):
                    restore_profile_from_backup(backup)
                
                with st.expander("View Full Profile Data"):
                    st.json(profile_data)
            else:
                st.markdown("### Backup Preview")
                st.info("👈 Select a backup from the history to preview and restore it.")
    else:
        st.info("📦 No profile backups available yet.")
        st.markdown("Backups are automatically created when you delete profiles.")

def render_settings():
    """Render the settings page."""
    st.markdown("## ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Configuration Information")
        config_info = config_manager.get_config_info()
        for info in config_info:
            st.write(f"• {info}")
        
        st.markdown("### Device Configuration")
        if st.button("🔍 Show Device Config"):
            st.json(st.session_state['aiden'].get_device_config())
    
    with col2:
        st.markdown("### Docker Deployment")
        st.markdown("For Docker deployment, set these environment variables:")
        st.code("""
FELLOW_EMAIL=your@email.com
FELLOW_PASSWORD=yourpassword
OPENAI_API_KEY=sk-your-openai-api-key
        """)
        
        st.markdown("### Streamlit Secrets")
        st.markdown("Or use `.streamlit/secrets.toml` for development:")
        st.code("""
FELLOW_EMAIL = "your@email.com"
FELLOW_PASSWORD = "yourpassword"
OPENAI_API_KEY = "sk-your-openai-api-key"
        """)

# ------------------------------------------------------------------------------
# Streamlit Setup
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Fellow Aiden Brew Studio",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize configuration manager
config_manager = ConfigManager()

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.markdown(
    """
    <style>
    hr { 
        margin: 0em;
        border-width: 2px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# Main Application Routing
# ------------------------------------------------------------------------------

# Auto-login if credentials are available from environment/secrets
if not st.session_state.logged_in and not st.session_state.get('login_attempted', False):
    saved_email = config_manager.get_fellow_email()
    saved_password = config_manager.get_fellow_password()
    
    if saved_email and saved_password:
        with st.spinner("Auto-connecting with saved credentials..."):
            result = connect_to_coffee_brewer(saved_email, saved_password)
            if result:
                st.session_state.brewer_settings = result
                st.session_state.logged_in = True
                st.session_state.current_page = "dashboard"
                st.rerun()
    
    st.session_state.login_attempted = True

# Render navigation if logged in
render_navigation()

# Route to appropriate page
if not st.session_state.logged_in:
    render_login_page()
else:
    page = st.session_state.current_page
    
    if page == "dashboard":
        render_dashboard()
    elif page == "profiles":
        render_profile_manager()
    elif page == "ai_barista":
        render_ai_barista()
    elif page == "brew_links":
        render_brew_links()
    elif page == "backups":
        render_backups()
    elif page == "settings":
        render_settings()
    else:
        # Default to dashboard
        st.session_state.current_page = "dashboard"
        render_dashboard()

# ------------------------------------------------------------------------------
# Legacy Support - render_profile_editor moved to navigation functions above
# ------------------------------------------------------------------------------
