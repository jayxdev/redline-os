import os
from redline.db.repositories.config_repo import ConfigRepository

class ConfigService:
    def __init__(self):
        self.repo = ConfigRepository()

    def get(self, key: str, default: str = None) -> str:
        """
        Gets a config value with the following priority:
        1. Streamlit Secrets (st.secrets)
        2. Database (system_config)
        3. Environment Variables (os.getenv)
        """
        import streamlit as st
        
        # 1. Try Streamlit Secrets
        try:
            if key in st.secrets:
                return str(st.secrets[key])
        except:
            pass

        # 2. Try Database
        db_val = self.repo.get_value(key)
        if db_val is not None:
            return str(db_val)
        
        # 3. Try Environment
        env_val = os.getenv(key)
        if env_val is not None:
            return env_val
            
        return default

    def set(self, key: str, value: str, description: str = None):
        self.repo.set_value(key, value, description)
