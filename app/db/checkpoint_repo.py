import json
from typing import Dict, Any

from db.database import get_connection, init_db


def save_checkpoint(
    checkpoint_id: str,
    state: Dict[str, Any],
    status: str
):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO invoice_checkpoints
        (checkpoint_id, state_json, status)
        VALUES (?, ?, ?)
        """,
        (checkpoint_id, json.dumps(state), status)
    )

    conn.commit()
    conn.close()


def load_checkpoint(checkpoint_id: str) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT state_json
        FROM invoice_checkpoints
        WHERE checkpoint_id = ?
        """,
        (checkpoint_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError("Checkpoint not found")

    return json.loads(row[0])
