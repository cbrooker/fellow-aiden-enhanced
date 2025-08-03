# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python library for interacting with the Fellow Aiden coffee brewer. It provides:
- A core `FellowAiden` class for API interactions with Fellow's cloud service
- Profile and schedule management for coffee brewing
- A Streamlit-based Brew Studio UI with AI-generated recipes
- Profile validation using Pydantic models

## Development Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
# or install in development mode:
pip install -e .[dev]
```

**Run tests:**
```bash
python -m pytest tests/
# or using unittest:
python -m unittest tests/test_fellow_aiden.py
```

**Code formatting:**
```bash
black fellow_aiden/
black tests/
```

**Run Brew Studio locally:**
```bash
streamlit run brew_studio/brew_studio.py
```

**Docker deployment:**
```bash
# Build the image
docker build -t brew-studio .

# Run with environment variables
docker run -p 8501:8501 \
  -e FELLOW_EMAIL=your@email.com \
  -e FELLOW_PASSWORD=yourpassword \
  -e OPENAI_API_KEY=sk-your-key \
  brew-studio
```

**Build package:**
```bash
python setup.py sdist bdist_wheel
# or using build:
python -m build
```

## Project Structure

**Core Library (`fellow_aiden/`):**
- `__init__.py` - Main `FellowAiden` class with API client functionality
- `profile.py` - `CoffeeProfile` Pydantic model with validation rules
- `schedule.py` - `CoffeeSchedule` Pydantic model for brew scheduling

**Applications:**
- `brew_studio/` - Streamlit web app for profile management and AI recipe generation
- `brew_assistant/` - Additional brewing assistant functionality

**Key Architecture Details:**
- Authentication uses JWT tokens with automatic retry on 401 responses
- All API calls include retry logic and reauthentication handling
- Profile validation enforces Fellow Aiden's specific constraints (temperature ranges, ratios, etc.)
- Lazy loading of profiles and schedules with caching
- Server-side fields are automatically stripped from user-provided profile data

## Configuration

The Brew Studio app supports multiple configuration methods for flexibility and security:

### Environment Variables (Recommended for Docker)
```bash
FELLOW_EMAIL=your@email.com
FELLOW_PASSWORD=yourpassword
OPENAI_API_KEY=sk-your-openai-key
```

### Streamlit Secrets (Development)
Create `.streamlit/secrets.toml`:
```toml
FELLOW_EMAIL = "your@email.com"
FELLOW_PASSWORD = "yourpassword"
OPENAI_API_KEY = "sk-your-openai-key"
```

### Config File (Non-sensitive data only)
The app automatically saves your Fellow email to `brew_studio_config.json` after successful login. Passwords and API keys are never stored in files for security.

**Priority Order:**
1. Environment Variables (highest)
2. Streamlit Secrets
3. Config File (lowest, email only)

## API Integration

The library interfaces with Fellow's AWS API at `https://l8qtmnc692.execute-api.us-west-2.amazonaws.com/v1`. Key endpoints:
- Device management and profile CRUD operations
- Schedule management
- Profile sharing via brew links
- Authenticated session management with automatic token refresh