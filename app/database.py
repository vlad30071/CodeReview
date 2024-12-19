import sqlite3
from app.scraper import scrape_event


def get_db_connection():
    conn = sqlite3.connect("app/events.db")
    conn.row_factory = sqlite3.Row
    return conn
