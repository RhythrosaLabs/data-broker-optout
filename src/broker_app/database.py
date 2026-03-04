"""
Database layer — SQLite persistence for opt-out attempts and broker records.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

from .models import BrokerSite


class DatabaseManager:
    """Handles all SQLite database operations."""

    def __init__(self, db_path: str = "opt_out_log.db"):
        self.db_path = db_path
        self._init_database()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS opt_out_attempts (
                    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker_name          TEXT    NOT NULL,
                    attempt_date         DATETIME NOT NULL,
                    status               TEXT    NOT NULL,
                    error_message        TEXT,
                    verification_required BOOLEAN,
                    next_attempt_date    DATETIME,
                    notes                TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS broker_sites (
                    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                    name                 TEXT UNIQUE NOT NULL,
                    url                  TEXT NOT NULL,
                    opt_out_url          TEXT NOT NULL,
                    form_fields          TEXT NOT NULL,
                    instructions         TEXT,
                    difficulty           TEXT DEFAULT 'medium',
                    requires_verification BOOLEAN DEFAULT 0,
                    active               BOOLEAN DEFAULT 1
                )
            ''')
            conn.commit()

    # ------------------------------------------------------------------
    # Attempt logging
    # ------------------------------------------------------------------
    def log_attempt(self, broker_name: str, status: str,
                    error_message: str = None,
                    verification_required: bool = False,
                    notes: str = "") -> None:
        """Record a single opt-out attempt."""
        next_attempt = datetime.now() + timedelta(days=90)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO opt_out_attempts
                   (broker_name, attempt_date, status, error_message,
                    verification_required, next_attempt_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (broker_name, datetime.now().isoformat(), status,
                 error_message, verification_required,
                 next_attempt.isoformat(), notes),
            )
            conn.commit()

    def get_attempts_history(self) -> List[Dict]:
        """Return the 100 most recent opt-out attempts."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT broker_name, attempt_date, status,
                       error_message, verification_required, notes
                FROM opt_out_attempts
                ORDER BY attempt_date DESC
                LIMIT 100
            ''').fetchall()
        return [
            {
                'broker_name':          row[0],
                'attempt_date':         row[1],
                'status':               row[2],
                'error_message':        row[3],
                'verification_required': row[4],
                'notes':                row[5],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Broker site management
    # ------------------------------------------------------------------
    def add_broker_site(self, broker: BrokerSite) -> None:
        """Insert or update a broker site record."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO broker_sites
                   (name, url, opt_out_url, form_fields, instructions,
                    difficulty, requires_verification)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (broker.name, broker.url, broker.opt_out_url,
                 json.dumps(broker.form_fields), broker.instructions,
                 broker.difficulty, broker.requires_verification),
            )
            conn.commit()

    def get_broker_sites(self) -> List[BrokerSite]:
        """Return all active broker sites."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT name, url, opt_out_url, form_fields,
                       instructions, difficulty, requires_verification
                FROM broker_sites
                WHERE active = 1
                ORDER BY name
            ''').fetchall()
        return [
            BrokerSite(
                name=row[0],
                url=row[1],
                opt_out_url=row[2],
                form_fields=json.loads(row[3]),
                instructions=row[4],
                difficulty=row[5],
                requires_verification=bool(row[6]),
            )
            for row in rows
        ]
