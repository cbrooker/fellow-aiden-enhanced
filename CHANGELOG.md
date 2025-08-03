# Changelog

All notable changes to the Fellow Aiden Enhanced project will be documented in this file.

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