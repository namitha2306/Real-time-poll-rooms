import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Poll(Base):
    __tablename__ = "polls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)   # 👈 ADD THIS

    options = relationship("Option", back_populates="poll")
    votes = relationship("Vote", back_populates="poll")

class Option(Base):
    __tablename__ = "options"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String, nullable=False)
    poll_id = Column(String, ForeignKey("polls.id"))

    poll = relationship("Poll", back_populates="options")
    votes = relationship("Vote", back_populates="option")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    poll_id = Column(String, ForeignKey("polls.id"))
    option_id = Column(String, ForeignKey("options.id"))
    voter_hash = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    poll = relationship("Poll", back_populates="votes")
    option = relationship("Option", back_populates="votes")
