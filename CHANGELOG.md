# Changelog

All notable changes to the Fellow Aiden Enhanced project will be documented in this file.

## [Navigation Restructure] - 2025-08-03

### Added
- **Complete Navigation Restructure**: Transformed from sidebar-based to modern page-based navigation
  - Professional login page with centered design and auto-login capability
  - Top navigation menu with 7 organized sections: Dashboard, Profile Manager, AI Barista, Brew Links, Backups, Settings, Logout
  - Clean 2-column layouts optimized for wide screens and better workflow
- **Enhanced Profile Management**: Comprehensive profile management with visual indicators
  - Profile count display with color-coded status (🟢🟡🔴) showing 14-profile limit
  - Profile deletion with automatic backup and two-click confirmation
  - Profile backup system storing up to 50 deleted profiles with timestamps
  - Profile restoration from backup history with conflict-free naming
- **Dedicated Pages Structure**: Logical separation of functionality
  - **Dashboard**: Device info, profile overview, quick stats, recently used profiles
  - **Profile Manager**: 2-column layout with profile selection and full editor
  - **AI Barista**: 2-column layout with configuration and profile preview
  - **Brew Links**: 2-column layout with import tools and profile preview  
  - **Backups**: 2-column layout with backup history and restore functionality
  - **Settings**: Configuration info and deployment documentation
- **Auto-Login System**: Seamless authentication using saved credentials from environment variables or Streamlit secrets

### Fixed
- **Dashboard Sorting Error**: Fixed TypeError when sorting profiles by lastUsedTime
  - Handles None values, numeric timestamps, and string timestamps properly
  - Prevents crashes when profile usage data is inconsistent

### Enhanced
- **User Experience**: Modern, professional interface design
  - Collapsed sidebar by default to maximize content area
  - Intuitive navigation with clear visual hierarchy
  - Responsive layouts that utilize full screen width
  - Professional confirmation dialogs and status indicators
- **Profile Workflow**: Streamlined profile management experience
  - Dedicated spaces for each workflow (creation, editing, backup, restore)
  - Visual feedback for profile capacity and backup status
  - Quick actions available in both sidebar and dedicated pages
- **Session Management**: Improved authentication and state handling
  - Auto-login with environment variables for Docker deployments
  - Clean logout functionality with proper session cleanup
  - Persistent navigation state across page transitions

### Changed
- **Application Architecture**: Complete restructure from sidebar-centric to page-based navigation
  - Removed cluttered sidebar interface
  - Implemented modern single-page application with routing
  - Separated concerns into logical page components
- **Profile Editor**: Enhanced with better action buttons and layout
  - Save, Share, and Delete buttons in organized layout
  - Contextual delete buttons only shown for existing profiles
  - Improved confirmation dialogs for destructive actions

### Technical Details
- **New Navigation System**: 
  - Page routing with `st.session_state.current_page`
  - Auto-login detection and routing
  - Clean navigation menu with icon-based buttons
- **Enhanced Backup System**:
  - JSON-based profile backup storage (`profile_backups.json`)
  - Automatic cleanup keeping last 50 backups
  - Timestamp-based conflict resolution for restored profiles
- **Improved Error Handling**:
  - Robust sorting for mixed data types in profile timestamps
  - Graceful handling of None values in profile data
  - Better type checking and fallback mechanisms

## [Enhanced] - 2025-08-03

### Added
- **Configuration Management System**: Comprehensive configuration system supporting multiple sources for credentials and API keys
  - Environment variables (highest priority, recommended for Docker)
  - Streamlit secrets support for development
  - Local config file for non-sensitive data (email only)
  - Automatic email persistence after successful login
- **Docker Deployment Support**: Complete Docker setup with environment variable configuration
  - Updated Dockerfile to use local codebase instead of cloning from GitHub
  - Environment variable support for `FELLOW_EMAIL`, `FELLOW_PASSWORD`, and `OPENAI_API_KEY`
  - Docker deployment documentation with examples
- **Configuration Information Panel**: New "ℹ️ Config Info" button in sidebar
  - Shows current configuration sources for each credential
  - Displays Docker deployment instructions
  - Helps users understand configuration priority order
- **Streamlit Secrets Template**: Pre-configured `.streamlit/secrets.toml` template
  - Ready-to-edit structure for local development
  - Clear placeholder values and comments

### Fixed
- **Critical Library Initialization Bug**: Fixed `UnboundLocalError` in `connect_to_coffee_brewer` function
  - Moved session state assignment inside try block to prevent accessing undefined variable
  - Added proper exception re-raising for non-authentication errors
- **Profile Access Error**: Resolved `KeyError: 'profiles'` by installing local version of fellow-aiden library
  - Updated from packaged version 0.2.2 to local development version with lazy loading
  - Profiles and schedules now loaded on-demand via properties instead of during initialization

### Enhanced
- **User Experience**: Credentials are now automatically populated from saved configurations
  - Email field pre-filled from last successful login or environment variables
  - Password and API key fields auto-populated from environment variables or secrets
  - No more re-entering credentials on every app restart
- **Security Best Practices**: Implemented secure credential handling
  - Passwords and API keys never stored in plain text files
  - Only email addresses saved to local config file
  - Environment variables and secrets prioritized for sensitive data
- **Documentation**: Updated CLAUDE.md with comprehensive configuration instructions
  - Added environment variable examples
  - Docker deployment commands and examples
  - Configuration priority order explanation

### Changed
- **Dockerfile**: Completely rewritten for local development
  - Uses local codebase instead of GitHub clone
  - Installs fellow-aiden package in development mode
  - Proper Python 3.11 base image
  - Streamlit port configuration for container deployment

### Technical Details
- **New Files Added**:
  - `brew_studio/config_manager.py` - Configuration management class
  - `.streamlit/secrets.toml` - Streamlit secrets template
  - `CHANGELOG.md` - This changelog file
- **Modified Files**:
  - `brew_studio/brew_studio.py` - Integrated configuration manager
  - `CLAUDE.md` - Updated documentation with configuration instructions
  - `Dockerfile` - Rewritten for local deployment
- **Git Repository**: Updated to fork `cbrooker/fellow-aiden-enhanced`
  - Changed origin remote from `9b/fellow-aiden` to `cbrooker/fellow-aiden-enhanced`
  - Added upstream remote to track original repository

### Migration Notes
For existing users:
1. Set up environment variables or Streamlit secrets for automatic credential loading
2. Email addresses will be automatically saved after first successful login
3. For Docker deployment, use environment variables instead of manual entry
4. Existing functionality remains unchanged - all improvements are additive