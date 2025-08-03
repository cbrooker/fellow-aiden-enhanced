# Fellow Aiden Enhanced

[![PyPI version](https://badge.fury.io/py/fellow-aiden.svg)](https://badge.fury.io/py/fellow-aiden)

This enhanced library provides a comprehensive interface to the Fellow Aiden coffee brewer with an advanced Brew Studio UI featuring AI-generated recipes, profile management, and backup/restore capabilities. 

## ✨ Enhanced Features

### 🎯 **Professional Brew Studio Interface**
- **Modern Navigation**: Clean page-based navigation with 7 dedicated sections
- **Auto-Login**: Seamless authentication using environment variables or Streamlit secrets
- **2-Column Layouts**: Optimized for wide screens and professional workflows
- **Responsive Design**: Collapsed sidebar with maximized content area

### 📋 **Advanced Profile Management**
- **Visual Profile Counter**: Color-coded indicators (🟢🟡🔴) showing 14-profile limit status
- **Automatic Backups**: Every profile deletion creates automatic timestamped backups
- **Backup & Restore System**: Complete backup history with one-click profile restoration
- **Profile Import/Export**: Share profiles via brew links with preview functionality

### 🤖 **AI-Powered Recipe Generation**
- **Smart Coffee Profiles**: Generate custom brewing profiles using OpenAI's AI based on coffee descriptions
- **Recipe Explanations**: Detailed AI-generated explanations for each brewing parameter
- **Real-time Preview**: See generated profiles before saving to your brewer

### 🔧 **Enhanced Configuration Management**
- **Multiple Config Sources**: Environment variables → Streamlit secrets → config files
- **Docker-Ready**: Full containerization support with environment variable configuration
- **Persistent Settings**: Automatic email persistence and credential management
- **Security-First**: Passwords and API keys never stored in plain text files

![Fellow Brew Studio](https://github.com/9b/fellow-aiden/blob/master/brew_studio/fellow-brew-studio.png?raw=true)

## 🚀 Quick Start

### **Installation**

```bash
# Install from source (recommended for latest features)
git clone https://github.com/cbrooker/fellow-aiden-enhanced.git
cd fellow-aiden-enhanced
pip install -e .

# Or install from PyPI
pip install fellow-aiden
```

### **Run Brew Studio Locally**

```bash
# Set up configuration (choose one method)

# Method 1: Environment Variables (recommended for Docker)
export FELLOW_EMAIL='your@email.com'
export FELLOW_PASSWORD='your-password'
export OPENAI_API_KEY='sk-your-openai-key'  # Optional for AI features

# Method 2: Streamlit Secrets (for development)
# Create .streamlit/secrets.toml with your credentials

# Launch the Brew Studio
streamlit run brew_studio/brew_studio.py
```

### **Docker Deployment**

```bash
# Build and run with environment variables
docker build -t fellow-brew-studio .
docker run -p 8501:8501 \
  -e FELLOW_EMAIL=your@email.com \
  -e FELLOW_PASSWORD=your-password \
  -e OPENAI_API_KEY=sk-your-key \
  fellow-brew-studio
```

## Sample Code

This sample code shows some of the range of functionality within the library:

```python
import os
from fellow_aiden import FellowAiden

# EMAIL = "YOUR-EMAIL-HERE"
# PASSWORD = "YOUR-PASSWORD-HERE"

EMAIL = os.environ['FELLOW_EMAIL']
PASSWORD = os.environ['FELLOW_PASSWORD']

# Create an instance
aiden = FellowAiden(EMAIL, PASSWORD)

# Get display name of brewer
name = aiden.get_display_name()

# Get profiles
profiles = aiden.get_profiles()

# Add a profile
profile = {
    "profileType": 0,
    "title": "Debug-FellowAiden",
    "ratio": 16,
    "bloomEnabled": True,
    "bloomRatio": 2,
    "bloomDuration": 30,
    "bloomTemperature": 96,
    "ssPulsesEnabled": True,
    "ssPulsesNumber": 3,
    "ssPulsesInterval": 23,
    "ssPulseTemperatures": [96,97,98],
    "batchPulsesEnabled": True,
    "batchPulsesNumber": 2,
    "batchPulsesInterval": 30,
    "batchPulseTemperatures": [96,97]
}
aiden.create_profile(profile)

# Find profile
pid = None
option = aiden.get_profile_by_title('FellowAiden', fuzzy=True)
if option:
    pid = option['id'] # p0

# Share a profile
share_link = aiden.generate_share_link(pid)

# Delete a profile
aiden.delete_profile_by_id(pid)

# Add profile from shared brew link
aiden.create_profile_from_link('https://brew.link/p/ws98')

# Add a schedule
schedule = {
    "days": [True, True, False, True, False, True, False], // sunday - saturday
    "secondFromStartOfTheDay": 28800, // time since 12 am
    "enabled": True,
    "amountOfWater": 950, // 150 - 1500
    "profileId": "p7", // must be valid profile
}
aiden.create_schedule(schedule)

# Delete a schedule
aiden.delete_schedule_by_id('s0')

```

## 🛠️ Brew Studio Navigation

### 🏠 **Dashboard**
- Device information and connection status
- Profile overview with capacity indicators
- Recently used profiles and backup statistics
- Quick access to key metrics

### 📋 **Profile Manager**
- Browse and edit all your coffee profiles
- Visual profile count with 14-profile limit tracking
- Quick actions: delete, share, duplicate profiles
- Advanced profile editor with real-time preview

### 🤖 **AI Barista**
- Generate custom profiles using AI based on coffee descriptions
- Detailed brewing parameter explanations
- Real-time profile preview and editing
- Integration with OpenAI for intelligent recipe creation

### 🔗 **Brew Links**
- Import profiles from shared Fellow Aiden brew links
- Preview imported profiles before saving
- Seamless integration with Fellow's sharing ecosystem

### 📦 **Backup & Restore**
- Automatic backup of deleted profiles
- Browse backup history with timestamps
- One-click profile restoration
- Conflict-free naming for restored profiles

### ⚙️ **Settings**
- Configuration management and troubleshooting
- Docker deployment instructions
- Environment variable and secrets management

## 🔧 Core Library Features

* **Complete Aiden Integration**: Access all settings and details from your brewer
* **Profile Management**: Create, edit, delete, and organize custom brewing profiles
* **Backup System**: Automatic profile backups with restore capabilities
* **Brew Link Support**: Import and share profiles via URLs
* **Fuzzy Search**: Find profiles using title matching (exact and fuzzy)
* **Schedule Management**: Create and manage custom brewing schedules
* **Configuration Flexibility**: Multiple config sources with secure credential handling

## 🆚 What's Enhanced?

This enhanced version builds upon the original [Fellow Aiden library](https://github.com/9b/fellow-aiden) with significant improvements:

### **🎨 User Experience**
- **Modern Navigation**: Transformed from cluttered sidebar to clean page-based navigation
- **Professional Interface**: 2-column layouts optimized for productivity
- **Auto-Login**: No more re-entering credentials on every restart
- **Visual Feedback**: Color-coded indicators and professional confirmation dialogs

### **🛡️ Safety & Reliability**
- **Profile Backup System**: Never lose a profile again with automatic backups
- **Confirmation Dialogs**: Two-click confirmations prevent accidental deletions
- **Error Handling**: Robust error handling for edge cases and data inconsistencies
- **Type Safety**: Improved data validation and error recovery

### **⚙️ Configuration & Deployment**
- **Multiple Config Sources**: Environment variables, Streamlit secrets, and config files
- **Docker-Ready**: Complete containerization with environment variable support
- **Security-First**: Credentials never stored in plain text files
- **Development-Friendly**: Easy local setup with Streamlit secrets

### **🚀 Performance & Scalability**
- **Lazy Loading**: Improved performance with on-demand data loading
- **Efficient Caching**: Smart caching strategies for better responsiveness
- **Memory Management**: Optimized session state handling
- **Backup Cleanup**: Automatic cleanup of old backups to prevent storage bloat

## 📄 License & Contributing

This enhanced version maintains compatibility with the original Fellow Aiden library while adding professional-grade features for power users and production deployments.
