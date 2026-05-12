from typing import Generic, TypeVar, List, Optional, Any, Dict
from pydantic import BaseModel
from redline.providers.mongo.client import MongoManager

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model_class: type):
        self.collection_name = collection_name
        self.model_class = model_class
        self.db = MongoManager().get_db()
        self.collection = self.db[collection_name]

    def create(self, item: T) -> str:
        data = item.model_dump()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get_by_id(self, id_val: str, id_field: str = "id") -> Optional[T]:
        data = self.collection.find_one({id_field: id_val})
        if data:
            return self.model_class(**data)
        return None

    def list(self, filters: Dict[str, Any] = None, sort: List[tuple] = None, limit: int = 100) -> List[T]:
        if filters is None:
            filters = {}
        
        cursor = self.collection.find(filters)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return [self.model_class(**doc) for doc in cursor]

    def update(self, id_val: str, updates: Any, id_field: str = "id") -> bool:
        if isinstance(updates, BaseModel):
            data = updates.model_dump()
        else:
            data = updates
            
        result = self.collection.update_one({id_field: id_val}, {"$set": data})
        return result.modified_count > 0

    def delete(self, id_val: str, id_field: str = "id") -> bool:
        result = self.collection.delete_one({id_field: id_val})
        return result.deleted_count > 0
