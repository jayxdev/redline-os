from db.repositories.base_repo import BaseRepository
from models.video import Video

class VideoRepository(BaseRepository[Video]):
    def __init__(self):
        super().__init__("videos", Video)

    def get_by_video_id(self, video_id: str) -> Video:
        return self.get_by_id(video_id, "video_id")
