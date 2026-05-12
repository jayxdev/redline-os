from .base_repo import BaseRepository
from models.idea import Idea

class IdeaRepository(BaseRepository[Idea]):
    def __init__(self):
        super().__init__("ideas", Idea)
