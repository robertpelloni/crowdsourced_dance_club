import uuid
import time
from typing import List, Optional
from src.db.database import get_db_connection

def create_club(name: str, description: Optional[str], owner_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    club_id = "club_" + str(uuid.uuid4())
    now = time.time()

    cursor.execute(
        "INSERT INTO clubs (id, name, description, owner_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (club_id, name, description, owner_id, now)
    )

    # Owner is automatically an admin member
    cursor.execute(
        "INSERT INTO club_members (club_id, user_id, role, joined_at) VALUES (?, ?, ?, ?)",
        (club_id, owner_id, "owner", now)
    )

    conn.commit()
    conn.close()
    return club_id

def get_club(club_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clubs WHERE id = ?", (club_id,))
    club = cursor.fetchone()

    if not club:
        conn.close()
        return None

    cursor.execute(
        "SELECT m.*, u.username FROM club_members m JOIN users u ON m.user_id = u.id WHERE m.club_id = ?",
        (club_id,)
    )
    members = cursor.fetchall()
    conn.close()

    club_dict = dict(club)
    club_dict["members"] = [dict(m) for m in members]
    return club_dict

def list_user_clubs(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT c.* FROM clubs c JOIN club_members m ON c.id = m.club_id WHERE m.user_id = ?",
        (user_id,)
    )
    clubs = cursor.fetchall()
    conn.close()
    return [dict(c) for c in clubs]

def add_club_member(club_id: str, username: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find user by username
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False, "User not found"

    user_id = user["id"]

    # Check if already a member
    cursor.execute("SELECT 1 FROM club_members WHERE club_id = ? AND user_id = ?", (club_id, user_id))
    if cursor.fetchone():
        conn.close()
        return False, "User already a member of this club"

    cursor.execute(
        "INSERT INTO club_members (club_id, user_id, role, joined_at) VALUES (?, ?, ?, ?)",
        (club_id, user_id, role, time.time())
    )
    conn.commit()
    conn.close()
    return True, "Member added"

def update_club_member_role(club_id: str, user_id: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if member exists
    cursor.execute("SELECT role FROM club_members WHERE club_id = ? AND user_id = ?", (club_id, user_id))
    current_member = cursor.fetchone()
    if not current_member:
        conn.close()
        return False, "Member not found"

    if current_member["role"] == "owner":
        conn.close()
        return False, "Cannot change owner role"

    cursor.execute(
        "UPDATE club_members SET role = ? WHERE club_id = ? AND user_id = ?",
        (role, club_id, user_id)
    )
    conn.commit()
    conn.close()
    return True, "Role updated"

def remove_club_member(club_id: str, user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if member exists
    cursor.execute("SELECT role FROM club_members WHERE club_id = ? AND user_id = ?", (club_id, user_id))
    current_member = cursor.fetchone()
    if not current_member:
        conn.close()
        return False, "Member not found"

    if current_member["role"] == "owner":
        conn.close()
        return False, "Cannot remove owner"

    cursor.execute("DELETE FROM club_members WHERE club_id = ? AND user_id = ?", (club_id, user_id))
    conn.commit()
    conn.close()
    return True, "Member removed"

def is_club_admin(club_id: str, user_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM club_members WHERE club_id = ? AND user_id = ?",
        (club_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return row["role"] in ["owner", "admin"]
