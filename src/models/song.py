from pydantic import BaseModel, Field

from src.object_id import PydanticObjectId


class BaseSong(BaseModel):
    artist: str
    title: str
    difficulty: float
    level: int
    released: str


class Song(BaseSong):
    id: PydanticObjectId | None = Field(None, alias="_id")

    def to_json(self):
        return {
            '_id': str(self.id),
            'artist': self.artist,
            'title': self.title,
            'difficulty': self.difficulty,
            'level': self.level,
            'released': self.released,
        }

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)

        if data["_id"] is None:
            str(data.pop("_id"))

        return data
