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
    vibe_preference: Optional[str] = "Psytrance"

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    referral_code: Optional[str] = None

class UserUpdate(BaseModel):
    vibe_preference: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: float

class FeedbackSubmit(BaseModel):
    vibe_rating: int
    technical_rating: int
    comment: Optional[str] = None

class TransitionVote(BaseModel):
    is_upvote: bool

class SongFeedback(BaseModel):
    track_id: str
    is_like: bool

class ClubCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ClubUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ClubMemberAdd(BaseModel):
    username: str
    role: str = "member"

class ClubMemberUpdate(BaseModel):
    role: str

class ClubMemberResponse(BaseModel):
    user_id: str
    username: str
    role: str
    joined_at: float

class ClubResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: float
    members: List[ClubMemberResponse] = []
