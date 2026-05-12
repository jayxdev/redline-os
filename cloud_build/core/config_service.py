import os
from ..db.repositories.config_repo import ConfigRepository

class ConfigService:
    def __init__(self):
        self.repo = ConfigRepository()

    def get(self, key: str, default: str = None) -> str:
        """
        Gets a config value from the database, falling back to environment variables.
        """
        # 1. Try Database
        db_val = self.repo.get_value(key)
        if db_val is not None:
            return str(db_val)
        
        # 2. Try Environment
        env_val = os.getenv(key)
        if env_val is not None:
            return env_val
            
        return default

    def set(self, key: str, value: str, description: str = None):
        self.repo.set_value(key, value, description)
