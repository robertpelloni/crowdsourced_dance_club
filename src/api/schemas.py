from pydantic import BaseModel
from typing import List, Optional

class Track(BaseModel):
    id: str
    title: str
    artist: str
    bpm: float
    key: str
    energy: float

class User(BaseModel):
    username: str
    points: int = 0
    badges: List[str] = []
    role: str = "user"
    referral_code: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    referral_code: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: float

class FeedbackSubmit(BaseModel):
    vibe_rating: int
    technical_rating: int
    comment: Optional[str] = None
