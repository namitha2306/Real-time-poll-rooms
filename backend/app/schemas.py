from pydantic import BaseModel
from typing import List
from typing import Optional


class PollCreate(BaseModel):
    question: str
    options: List[str]
    duration_minutes: Optional[int] = None


class VoteCreate(BaseModel):
    option_id: str
