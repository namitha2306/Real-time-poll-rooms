from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Vote, Poll, Option
from ..schemas import VoteCreate
from ..utils import generate_voter_hash
from ..websocket import manager
from sqlalchemy.orm import joinedload
from ..core.limiter import limiter
from datetime import datetime


router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/{poll_id}")
@limiter.limit("5/minute")
async def cast_vote(
    poll_id: str,
    vote_data: VoteCreate,
    request: Request,
    db: Session = Depends(get_db)
):

    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    option = db.query(Option).filter(
        Option.id == vote_data.option_id,
        Option.poll_id == poll_id
    ).first()

    if not option:
        raise HTTPException(status_code=400, detail="Invalid option")

    ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    voter_hash = generate_voter_hash(ip, user_agent, poll_id)

    existing_vote = db.query(Vote).filter(
        Vote.poll_id == poll_id,
        Vote.voter_hash == voter_hash
    ).first()

    if existing_vote:
        raise HTTPException(status_code=403, detail="You have already voted")

    new_vote = Vote(
        poll_id=poll_id,
        option_id=vote_data.option_id,
        voter_hash=voter_hash,
        ip_address=ip
    )

    db.add(new_vote)
    db.commit()

    # 🔥 IMPORTANT: Re-fetch updated poll
    updated_poll = db.query(Poll).options(
        joinedload(Poll.options),
        joinedload(Poll.votes)
    ).filter(Poll.id == poll_id).first()

    results = []

    for opt in updated_poll.options:
        vote_count = len([v for v in updated_poll.votes if v.option_id == opt.id])
        results.append({
            "option_id": opt.id,
            "text": opt.text,
            "votes": vote_count
        })

    # 🔥 Broadcast update
    await manager.broadcast(poll_id, {
        "type": "vote_update",
        "total_votes": len(updated_poll.votes),
        "options": results
    })

    return {"message": "Vote cast successfully"}



   
