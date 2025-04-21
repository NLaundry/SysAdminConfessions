from datetime import datetime
from sqlmodel import SQLModel, Field

class Confession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    score: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

