import sqlite3
import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from src.db.database import get_db_connection

router = APIRouter(prefix="/api/governance", tags=["Governance"])

# In-memory TTL cache to mitigate SQLite read contention during high-load voting peaks
_proposals_cache: Optional[List[Dict]] = None
_proposals_cache_expiry: float = 0.0
CACHE_TTL_SECONDS = 15.0

def invalidate_governance_cache():
    """Invalidates the in-memory proposals cache immediately."""
    global _proposals_cache, _proposals_cache_expiry
    _proposals_cache = None
    _proposals_cache_expiry = 0.0

# Dependency mock for current user (assume imported correctly in main)
def mock_get_current_user():
    pass

class ProposalCreate(BaseModel):
    title: str
    description: str
    rule_type: str # e.g., 'bpm_cap', 'genre_lock'
    rule_value: str

@router.post("/proposals")
async def create_proposal(proposal: ProposalCreate):
    """Submit a new DAO macro-rule proposal for the venue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    proposal_id = "prop_" + str(uuid.uuid4())

    try:
        cursor.execute('''
            INSERT INTO governance_proposals (id, title, description, rule_type, rule_value, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (proposal_id, proposal.title, proposal.description, proposal.rule_type, proposal.rule_value, 'active', time.time()))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    conn.close()
    # Invalidate cache so fresh proposal appears immediately
    invalidate_governance_cache()
    return {"status": "success", "proposal_id": proposal_id}

@router.get("/proposals")
async def list_proposals():
    """List all active governance proposals, served via in-memory TTL cache to reduce DB load."""
    global _proposals_cache, _proposals_cache_expiry
    now = time.time()

    if _proposals_cache is not None and now < _proposals_cache_expiry:
        return _proposals_cache

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM governance_proposals WHERE status = 'active'")
    rows = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    _proposals_cache = result
    _proposals_cache_expiry = now + CACHE_TTL_SECONDS
    return result

class ProposalVote(BaseModel):
    proposal_id: str
    vote: int # 1 for yes, -1 for no

@router.post("/vote")
async def vote_on_proposal(vote: ProposalVote):
    """Vote on an active macro-rule proposal."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if active
    cursor.execute("SELECT status FROM governance_proposals WHERE id = ?", (vote.proposal_id,))
    row = cursor.fetchone()
    if not row or row["status"] != 'active':
        conn.close()
        raise HTTPException(status_code=400, detail="Proposal not active or does not exist.")

    try:
        cursor.execute('''
            INSERT INTO governance_votes (proposal_id, user_id, vote_value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (vote.proposal_id, "mock_user", vote.vote, time.time()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="User already voted on this proposal.")

    conn.close()
    return {"status": "success", "message": "Vote recorded."}
