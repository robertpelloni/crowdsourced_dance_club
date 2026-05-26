import json
from typing import Dict, List
from src.db.database import get_db_connection

def generate_vibe_performance_report() -> Dict:
    """
    Aggregates performance logs and feedback to provide a summary of Conductor effectiveness.
    """
    conn = get_db_connection(); cursor = conn.cursor()

    # 1. Track Success Rates
    cursor.execute('''
        SELECT t.genre, AVG(l.vibe_score) as avg_score, AVG(l.success_metric) as avg_success
        FROM vibe_performance_logs l
        JOIN tracks t ON l.track_id = t.id
        GROUP BY t.genre
    ''')
    genre_performance = [dict(row) for row in cursor.fetchall()]

    # 2. Average User Ratings
    cursor.execute('SELECT AVG(vibe_rating), AVG(technical_rating) FROM feedback')
    avg_vibe, avg_tech = cursor.fetchone()

    conn.close()

    return {
        "genre_metrics": genre_performance,
        "average_user_ratings": {
            "vibe": round(avg_vibe or 0.0, 2),
            "technical": round(avg_tech or 0.0, 2)
        }
    }
