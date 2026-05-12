from pymongo import MongoClient
import os
from typing import Optional
from dotenv import load_dotenv

class MongoManager:
    _instance: Optional['MongoManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, uri: str, db_name: str):
        if not self._initialized:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self._initialized = True

    def get_db(self):
        if not self._initialized:
            import streamlit as st
            
            # 1. Try Streamlit Secrets
            try:
                uri = st.secrets.get("MONGODB_URI")
                db_name = st.secrets.get("MONGODB_DB_NAME", "redline_cult")
            except:
                uri = None
                db_name = None

            # 2. Fallback to .env and environment
            if not uri:
                dotenv_path = os.path.join(os.path.dirname(__file__), '../../..', '.env')
                load_dotenv(dotenv_path)
                uri = os.getenv("MONGODB_URI")
                db_name = os.getenv("MONGODB_DB_NAME", "redline_cult")
            
            if uri:
                self.initialize(uri, db_name)
            else:
                raise Exception("MongoManager not initialized and MONGODB_URI not found in environment.")
        
        return self.db

    def close(self):
        if self._initialized:
            self.client.close()
            self._initialized = False
        MongoManager._instance = None
