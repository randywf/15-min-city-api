from typing import Dict, Optional, List, Literal
from pydantic import BaseModel

class OverpassTags(BaseModel):
    name: Optional[str] = None
    amenity: Optional[str] = None
    cuisine: Optional[str] = None
    # allow arbitrary other string keys:
    # Pydantic v2 way:
    model_config = {"extra": "allow"}

class OverpassElement(BaseModel):
    type: Literal["node", "way", "relation"]
    id: int
    lat: Optional[float] = None
    lon: Optional[float] = None
    center: Optional[Dict[str, float]] = None  # {"lat": ..., "lon": ...}
    tags: OverpassTags

class OverpassResponse(BaseModel):
    version: float | int
    generator: str
    elements: List[OverpassElement]