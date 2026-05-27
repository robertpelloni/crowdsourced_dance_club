import json
from typing import Dict, List
from src.db.database import get_db_connection

def generate_vibe_performance_report() -> Dict:
    """
    Aggregates performance logs and feedback to provide a summary of Conductor effectiveness.
    """
    conn = get_db_connection(); cursor = conn.cursor()

    # 1. Track Success Rates
    try:
        cursor.execute('''
            SELECT t.genre, AVG(l.vibe_score) as avg_score, AVG(l.success_metric) as avg_success
            FROM vibe_performance_logs l
            JOIN tracks t ON l.track_id = t.id
            GROUP BY t.genre
        ''')
        genre_performance = [dict(row) for row in cursor.fetchall()]
    except:
        genre_performance = []

    # 2. Average User Ratings
    try:
        cursor.execute('SELECT AVG(vibe_rating), AVG(technical_rating) FROM feedback')
        avg_vibe, avg_tech = cursor.fetchone()
    except:
        avg_vibe, avg_tech = 0, 0

    conn.close()

    return {
        "genre_metrics": genre_performance,
        "average_user_ratings": {
            "vibe": round(avg_vibe or 0.0, 2),
            "technical": round(avg_tech or 0.0, 2)
        }
    }

def get_feedback_insights() -> Dict:
    """
    Analyzes transition and song feedback to provide actionable insights.
    """
    conn = get_db_connection(); cursor = conn.cursor()

    # 1. Transition Success by Archetype
    cursor.execute('''
        SELECT archetype,
               COUNT(*) as total,
               SUM(CASE WHEN is_upvote THEN 1 ELSE 0 END) as upvotes
        FROM transition_feedback
        GROUP BY archetype
    ''')
    transition_insights = [
        {"archetype": r["archetype"], "success_rate": round(r["upvotes"]/r["total"], 2) if r["total"] > 0 else 0}
        for r in cursor.fetchall()
    ]

    # 2. Top and Bottom Rated Songs
    cursor.execute('''
        SELECT t.title, t.artist,
               SUM(CASE WHEN f.is_like THEN 1 ELSE -1 END) as score
        FROM song_feedback f
        JOIN tracks t ON f.track_id = t.id
        GROUP BY f.track_id
        ORDER BY score DESC
    ''')
    song_insights = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "transition_performance": transition_insights,
        "song_popularity_ranking": song_insights
    }

def get_engagement_metrics(dj_state) -> Dict:
    """Analyzes real-time engagement and voting velocity."""
    return {
        "vote_velocity_per_min": len(dj_state.vote_history),
        "active_users_with_points": len([u for u, s in dj_state.user_stats.items() if s['points'] > 0]),
        "total_clubs": 0,
        "is_peak_mode": dj_state.is_peak_mode
    }
