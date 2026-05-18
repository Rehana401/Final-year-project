"""
DatabaseManager — SQLite database layer for Fraud Detection System.

Manages:
  • User accounts (bcrypt hashing)
  • Analysis history (transaction predictions)
  • Model metadata (training records)
"""

import os
import uuid
import sqlite3
from datetime import datetime
from contextlib import contextmanager

import bcrypt


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")

# ==============================================================
# ✏️  ADMIN CONFIGURATION — Edit this list to add/remove admins
#     Each entry needs: username, email, password
#     They will be auto-seeded into the DB on app startup.
# ==============================================================
SEED_ADMINS = [
    {"username": "Rehana",  "email": "rehanakousar108727@gmail.com", "password": "rehana@146"},
    {"username": "Ayesha",  "email": "ayeshaamin328@gmail.com", "password": "ayesha114"},
    # Add more admins below:
    # {"username": "admin2", "email": "admin2@example.com",      "password": "securepass2"},
]


class DatabaseManager:
    """SQLite database manager with WAL mode and parameterized queries."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()

    # ------------------------------------------------------------------
    # Connection helper
    # ------------------------------------------------------------------
    @contextmanager
    def _get_connection(self):
        """Context-managed SQLite connection with WAL mode."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Schema initialization
    # ------------------------------------------------------------------
    def _init_database(self):
        """Create tables and seed admin user if not exists."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS USERS (
                    userId       TEXT PRIMARY KEY,
                    username     TEXT UNIQUE NOT NULL,
                    email        TEXT UNIQUE NOT NULL,
                    password     TEXT NOT NULL,
                    is_admin     INTEGER DEFAULT 0,
                    createdAt    TEXT DEFAULT (datetime('now')),
                    lastLogin    TEXT
                );

                CREATE TABLE IF NOT EXISTS ANALYSIS_HISTORY (
                    historyId         TEXT PRIMARY KEY,
                    userId            TEXT NOT NULL,
                    transactionDetails TEXT,
                    resultLabel       TEXT,
                    riskScore         REAL,
                    confidenceScore   REAL,
                    featureImportance TEXT,
                    predictedAt       TEXT DEFAULT (datetime('now')),
                    exportedAs        TEXT DEFAULT 'none',
                    FOREIGN KEY (userId) REFERENCES USERS(userId)
                );

                CREATE TABLE IF NOT EXISTS MODEL_METADATA (
                    modelId         TEXT PRIMARY KEY,
                    algorithmType   TEXT NOT NULL,
                    version         TEXT DEFAULT '1.0',
                    accuracy        REAL,
                    precision_score REAL,
                    recall          REAL,
                    f1Score         REAL,
                    aucRoc          REAL,
                    isBestModel     INTEGER DEFAULT 0,
                    filePath        TEXT,
                    trainedAt       TEXT DEFAULT (datetime('now'))
                );
            """)

            # Seed all admins from SEED_ADMINS list if they don't exist yet
            for admin in SEED_ADMINS:
                existing = conn.execute(
                    "SELECT userId FROM USERS WHERE email = ?",
                    (admin["email"].lower(),)
                ).fetchone()

                if not existing:
                    admin_id = str(uuid.uuid4())
                    hashed = bcrypt.hashpw(admin["password"].encode("utf-8"), bcrypt.gensalt())
                    conn.execute(
                        "INSERT INTO USERS (userId, username, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (admin_id, admin["username"], admin["email"].lower(), hashed.decode("utf-8"), 1)
                    )
                    print(f"[DB] Admin seeded: {admin['email']}")

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------
    def create_user(self, username: str, email: str, password: str,
                    is_admin: bool = False) -> dict:
        """Create a new user account. Returns user dict or raises."""
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO USERS (userId, username, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, email.lower(), hashed.decode("utf-8"), int(is_admin))
            )

        return {"userId": user_id, "username": username, "email": email, "is_admin": is_admin}

    def authenticate(self, email: str, password: str) -> dict:
        """Authenticate user by email + password. Returns user dict or None."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT userId, username, email, password, is_admin FROM USERS WHERE email = ?",
                (email.lower(),)
            ).fetchone()

        if row is None:
            return None

        if bcrypt.checkpw(password.encode("utf-8"), row["password"].encode("utf-8")):
            # Update last login
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE USERS SET lastLogin = ? WHERE userId = ?",
                    (datetime.now().isoformat(), row["userId"])
                )
            return {
                "userId": row["userId"],
                "username": row["username"],
                "email": row["email"],
                "is_admin": bool(row["is_admin"]),
            }
        return None

    def user_exists(self, username: str = None, email: str = None) -> bool:
        """Check if a username or email already exists."""
        with self._get_connection() as conn:
            if username:
                row = conn.execute("SELECT 1 FROM USERS WHERE username = ?", (username,)).fetchone()
                if row:
                    return True
            if email:
                row = conn.execute("SELECT 1 FROM USERS WHERE email = ?", (email.lower(),)).fetchone()
                if row:
                    return True
        return False

    # ------------------------------------------------------------------
    # Analysis history
    # ------------------------------------------------------------------
    def save_search(self, user_id: str, transaction_details: str,
                    result_label: str, risk_score: float,
                    confidence_score: float,
                    feature_importance: dict = None,
                    model_id: str = None) -> str:
        """Save a prediction to analysis history. Returns historyId."""
        import json
        history_id = str(uuid.uuid4())
        fi_json = json.dumps(feature_importance) if feature_importance else None

        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO ANALYSIS_HISTORY
                   (historyId, userId, transactionDetails, resultLabel,
                    riskScore, confidenceScore, featureImportance)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (history_id, user_id, transaction_details, result_label,
                 risk_score, confidence_score, fi_json)
            )
        return history_id

    def get_history(self, user_id: str, start_date: str = None,
                    end_date: str = None) -> list:
        """Get analysis history for a user, optionally filtered by date."""
        query = "SELECT * FROM ANALYSIS_HISTORY WHERE userId = ?"
        params = [user_id]

        if start_date:
            query += " AND predictedAt >= ?"
            params.append(start_date)
        if end_date:
            query += " AND predictedAt <= ?"
            params.append(end_date)

        query += " ORDER BY predictedAt DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [dict(r) for r in rows]

    def delete_history(self, history_id: str, user_id: str) -> bool:
        """Delete a single history record (ownership check)."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM ANALYSIS_HISTORY WHERE historyId = ? AND userId = ?",
                (history_id, user_id)
            )
        return cursor.rowcount > 0

    def update_export_status(self, history_id: str, export_format: str):
        """Update the export status of a history record."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE ANALYSIS_HISTORY SET exportedAs = ? WHERE historyId = ?",
                (export_format, history_id)
            )

    # ------------------------------------------------------------------
    # Model metadata
    # ------------------------------------------------------------------
    def save_model_metadata(self, algorithm_type: str, accuracy: float,
                            precision_score: float, recall: float,
                            f1_score: float, auc_roc: float,
                            is_best: bool = False,
                            file_path: str = None) -> str:
        """Save training metadata for a model."""
        model_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            if is_best:
                conn.execute("UPDATE MODEL_METADATA SET isBestModel = 0")

            conn.execute(
                """INSERT INTO MODEL_METADATA
                   (modelId, algorithmType, accuracy, precision_score, recall,
                    f1Score, aucRoc, isBestModel, filePath)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (model_id, algorithm_type, accuracy, precision_score, recall,
                 f1_score, auc_roc, int(is_best), file_path)
            )
        return model_id

    def get_all_models(self) -> list:
        """Get all model metadata records."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM MODEL_METADATA ORDER BY trainedAt DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_best_model(self) -> dict:
        """Get metadata for the current best model."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM MODEL_METADATA WHERE isBestModel = 1"
            ).fetchone()
        return dict(row) if row else None

    def get_user_count(self) -> int:
        """Get total number of registered users."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM USERS").fetchone()
        return row["cnt"] if row else 0

    def get_total_analyses(self) -> int:
        """Get total number of analyses performed."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM ANALYSIS_HISTORY").fetchone()
        return row["cnt"] if row else 0

    def get_user_analyses_count(self, user_id: str) -> int:
        """Get total number of analyses performed by a specific user."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM ANALYSIS_HISTORY WHERE userId = ?", (user_id,)).fetchone()
        return row["cnt"] if row else 0
