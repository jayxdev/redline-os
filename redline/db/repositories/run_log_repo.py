from redline.db.repositories.base_repo import BaseRepository
from redline.models.run_log import RunLog

class RunLogRepository(BaseRepository[RunLog]):
    def __init__(self):
        super().__init__("job_runs", RunLog)

    def get_latest_runs(self, limit: int = 5):
        return self.list(limit=limit, sort=[("created_at", -1)])
