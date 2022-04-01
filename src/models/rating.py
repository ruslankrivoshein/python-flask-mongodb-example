from pydantic import BaseModel, conint

from src.object_id import PydanticObjectId


class Rating(BaseModel):
    song_id: PydanticObjectId
    value: conint(ge=1, le=5)
