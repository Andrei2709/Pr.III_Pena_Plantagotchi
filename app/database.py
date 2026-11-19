import sqlite3
from pathlib import Path

DB_PATH = Path("plantagotchi.db")


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                xp INTEGER NOT NULL DEFAULT 0
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                watering_frequency_days INTEGER NOT NULL,
                light_requirement TEXT NOT NULL DEFAULT 'Medie',
                last_watered TEXT NOT NULL,
                is_alive INTEGER NOT NULL DEFAULT 1,
                death_reason TEXT,
                death_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS care_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                action_date TEXT NOT NULL,
                xp_change INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (plant_id) REFERENCES plants (id)
            );
            """
        )

        # Creăm un utilizator implicit dacă tabela este goală
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (id, username, xp)
            VALUES (1, 'gradinar', 0);
            """
        )

        conn.commit()