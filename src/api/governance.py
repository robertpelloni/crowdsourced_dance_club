import sqlite3
import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from src.db.database import get_db_connection

router = APIRouter(prefix="/api/governance", tags=["Governance"])

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
    return {"status": "success", "proposal_id": proposal_id}

@router.get("/proposals")
async def list_proposals():
    """List all active governance proposals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM governance_proposals WHERE status = 'active'")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

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
