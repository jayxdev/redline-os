from redline.db.repositories.base_repo import BaseRepository
from redline.models.idea import Idea

class IdeaRepository(BaseRepository[Idea]):
    def __init__(self):
        super().__init__("ideas", Idea)
