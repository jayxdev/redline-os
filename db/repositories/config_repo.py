from .base_repo import BaseRepository
from ...models.system_config import SystemConfig
from typing import Any, Optional
from datetime import datetime

class ConfigRepository(BaseRepository[SystemConfig]):
    def __init__(self):
        super().__init__("system_config", SystemConfig)

    def get_value(self, key: str, default: Any = None) -> Any:
        data = self.collection.find_one({"key": key})
        if data:
            return data.get("value")
        return default

    def set_value(self, key: str, value: Any, description: str = None):
        self.collection.update_one(
            {"key": key},
            {
                "$set": {
                    "value": value,
                    "description": description,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
