"""Configuration management for Brew Studio."""
import json
import os
import streamlit as st
from pathlib import Path


class ConfigManager:
    """Manages configuration from environment variables, secrets, and config files."""
    
    def __init__(self):
        self.config_file = Path("brew_studio_config.json")
        self._config_cache = None
    
    def get_fellow_email(self):
        """Get Fellow email from env vars, secrets, or config file."""
        # Priority: ENV -> Streamlit secrets -> config file
        email = os.getenv('FELLOW_EMAIL')
        if email:
            return email
            
        # Check Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'FELLOW_EMAIL' in st.secrets:
                return st.secrets['FELLOW_EMAIL']
        except Exception:
            pass
            
        # Check config file
        config = self._load_config()
        return config.get('fellow_email', '')
    
    def get_fellow_password(self):
        """Get Fellow password from env vars or secrets only (never config file)."""
        # Priority: ENV -> Streamlit secrets (never store in config file)
        password = os.getenv('FELLOW_PASSWORD')
        if password:
            return password
            
        # Check Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'FELLOW_PASSWORD' in st.secrets:
                return st.secrets['FELLOW_PASSWORD']
        except Exception:
            pass
            
        return ''
    
    def get_openai_api_key(self):
        """Get OpenAI API key from env vars or secrets only (never config file)."""
        # Priority: ENV -> Streamlit secrets (never store in config file)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key
            
        # Check Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                return st.secrets['OPENAI_API_KEY']
        except Exception:
            pass
            
        return ''
    
    def save_fellow_email(self, email):
        """Save Fellow email to config file (non-sensitive)."""
        config = self._load_config()
        config['fellow_email'] = email
        self._save_config(config)
    
    def _load_config(self):
        """Load configuration from JSON file."""
        if self._config_cache is not None:
            return self._config_cache
            
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config_cache = json.load(f)
            else:
                self._config_cache = {}
        except Exception as e:
            st.warning(f"Could not load config file: {e}")
            self._config_cache = {}
            
        return self._config_cache
    
    def _save_config(self, config):
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self._config_cache = config
        except Exception as e:
            st.warning(f"Could not save config file: {e}")
    
    def get_config_info(self):
        """Get information about current configuration sources."""
        info = []
        
        # Check Fellow email source
        if os.getenv('FELLOW_EMAIL'):
            info.append("Fellow Email: Environment Variable")
        elif hasattr(st, 'secrets') and 'FELLOW_EMAIL' in st.secrets:
            info.append("Fellow Email: Streamlit Secrets")
        elif self._load_config().get('fellow_email'):
            info.append("Fellow Email: Config File")
        else:
            info.append("Fellow Email: Not configured")
            
        # Check Fellow password source
        if os.getenv('FELLOW_PASSWORD'):
            info.append("Fellow Password: Environment Variable")
        elif hasattr(st, 'secrets') and 'FELLOW_PASSWORD' in st.secrets:
            info.append("Fellow Password: Streamlit Secrets")
        else:
            info.append("Fellow Password: Not configured")
            
        # Check OpenAI API key source
        if os.getenv('OPENAI_API_KEY'):
            info.append("OpenAI API Key: Environment Variable")
        elif hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            info.append("OpenAI API Key: Streamlit Secrets")
        else:
            info.append("OpenAI API Key: Not configured")
            
        return info