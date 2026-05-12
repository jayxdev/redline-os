from .base_repo import BaseRepository
from cloud_build.models.rules_memory import RulesMemory

class RulesRepository(BaseRepository[RulesMemory]):
    def __init__(self):
        super().__init__("rules", RulesMemory)

    def get_latest_active(self) -> RulesMemory:
        results = self.list(filters={"status": "active"}, sort=[("version", -1)], limit=1)
        return results[0] if results else None
