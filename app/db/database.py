import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "checkpoints.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invoice_checkpoints (
            checkpoint_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()
