from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from .. import models, schemas
from ..database import get_db
from ..models import Poll
from datetime import timezone


router = APIRouter(prefix="/poll", tags=["Poll"])


# =========================
# CREATE POLL
# =========================
@router.post("/create")
def create_poll(poll: schemas.PollCreate, db: Session = Depends(get_db)):

    if len(poll.options) < 2:
        raise HTTPException(status_code=400, detail="At least 2 options required")

    cleaned_options = list(
        set([opt.strip() for opt in poll.options if opt.strip()])
    )

    if len(cleaned_options) < 2:
        raise HTTPException(
            status_code=400,
            detail="Options must be unique and non-empty"
        )

    # ✅ Handle expiry
    expires_at = None
    if poll.duration_minutes and poll.duration_minutes > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=poll.duration_minutes)

    new_poll = models.Poll(
        question=poll.question,
        expires_at=expires_at
    )

    db.add(new_poll)
    db.commit()
    db.refresh(new_poll)

    for option_text in cleaned_options:
        option = models.Option(
            text=option_text,
            poll_id=new_poll.id
        )
        db.add(option)

    db.commit()

    return {
        "poll_id": new_poll.id,
        "share_url": f"http://localhost:5173/poll/{new_poll.id}",
        "expires_at": new_poll.expires_at
    }


# =========================
# GET POLL
# =========================
@router.get("/{poll_id}")
def get_poll(poll_id: str, db: Session = Depends(get_db)):

    poll = db.query(Poll).options(
        joinedload(Poll.options),
        joinedload(Poll.votes)
    ).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    # ✅ Check expiry
    is_expired = False
    if poll.expires_at and poll.expires_at < datetime.utcnow():
        is_expired = True

    results = []

    for option in poll.options:
        vote_count = len(
            [v for v in poll.votes if v.option_id == option.id]
        )
        results.append({
            "option_id": option.id,
            "text": option.text,
            "votes": vote_count
        })

    total_votes = len(poll.votes)

    return {
        "poll_id": poll.id,
        "question": poll.question,
        "total_votes": total_votes,
        "options": results,
        "expires_at": poll.expires_at.isoformat() if poll.expires_at else None,
        "is_expired": is_expired
    }
