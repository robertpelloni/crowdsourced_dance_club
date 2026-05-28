import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from src.db.database import DB_PATH

MODEL_PATH = "models/neural_conductor_v1.joblib"
ENCODER_PATH = "models/archetype_encoder.joblib"

def train_model():
    """
    Trains a regression model to predict transition success based on track features and archetypes.
    """
    if not os.path.exists("models"):
        os.makedirs("models")

    conn = sqlite3.connect(DB_PATH)

    # 1. Load transition feedback data
    query = '''
        SELECT tf.archetype, tf.is_upvote,
               t1.bpm as from_bpm, t1.energy as from_energy,
               t2.bpm as to_bpm, t2.energy as to_energy
        FROM transition_feedback tf
        JOIN tracks t1 ON tf.track_id_from = t1.id
        JOIN tracks t2 ON tf.track_id_to = t2.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    if len(df) < 10:
        return False, "Insufficient data for training (need at least 10 samples)"

    # 2. Preprocessing
    le = LabelEncoder()
    df['archetype_encoded'] = le.fit_transform(df['archetype'])

    # Calculate deltas as features
    df['bpm_delta'] = abs(df['from_bpm'] - df['to_bpm'])
    df['energy_delta'] = abs(df['from_energy'] - df['to_energy'])

    X = df[['archetype_encoded', 'from_bpm', 'from_energy', 'to_bpm', 'to_energy', 'bpm_delta', 'energy_delta']]
    y = df['is_upvote'].astype(float)

    # 3. Train Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 4. Save Artifacts
    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)

    return True, f"Model trained successfully on {len(df)} samples."

if __name__ == "__main__":
    success, msg = train_model()
    print(msg)
