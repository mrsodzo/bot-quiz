import os
import json
import os
import sqlite3
from datetime import datetime
from typing import Optional


DB_PATH = "data/quiz.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            answers TEXT NOT NULL,
            tariff TEXT NOT NULL,
            price TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_result_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (quiz_result_id) REFERENCES quiz_results (id)
        )
        """
    )
    conn.commit()
    conn.close()


def save_quiz_result(user_id: int, username: Optional[str], answers: dict, tariff: str, price: str, description: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO quiz_results (user_id, username, answers, tariff, price, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            username,
            json.dumps(answers, ensure_ascii=False),
            tariff,
            price,
            description,
            datetime.utcnow().isoformat(),
        ),
    )
    result_id = c.lastrowid
    conn.commit()
    conn.close()
    return result_id


def save_contact(quiz_result_id: int, name: str, phone: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO contacts (quiz_result_id, name, phone, created_at) VALUES (?, ?, ?, ?)",
        (quiz_result_id, name, phone, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_quiz_result_with_contact(result_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM quiz_results WHERE id = ?", (result_id,))
    result = c.fetchone()
    result_dict = dict(result)
    c.execute("SELECT * FROM contacts WHERE quiz_result_id = ?", (result_id,))
    contact = c.fetchone()
    result_dict["contact"] = dict(contact) if contact else None
    conn.close()
    return result_dict
