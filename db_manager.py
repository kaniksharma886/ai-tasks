import sqlite3
import config
import utils
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


#Create the table for the first time.
def init_db(db_path=config.DB_PATH):
    """
    Initializes message history table.
    Requirement: 3.1 (b)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT, content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP )""")
        conn.commit()
        conn.close()
    except Exception as e0:
        utils.log_error("Error: Unable to create db table. ", e0)


def save_message(role, content, db_path=config.DB_PATH):
    """Saves a new message and removes anything more than 10 rows."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO message_history (role, content) VALUES (?, ?)", (role, content))
        
        cursor.execute(f"DELETE FROM message_history WHERE id NOT IN (SELECT id FROM message_history ORDER BY id DESC LIMIT {config.MESSAGE_HISTORY_LIMIT})")
        conn.commit()
        conn.close()
    except Exception as e1:
        utils.log_error("Error: Unable to add new message to database. ", e1)


def fetch_last_messages(db_path=config.DB_PATH, limit=config.MESSAGE_HISTORY_LIMIT):
    """Get last messages from the database."""
    try:
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM (
                SELECT id, role, content FROM message_history ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
    except Exception as e2:
        utils.log_error("Error: Unable to fetch messages from database. ", e2)
        return []
        
    messages = []
    for role, content in rows:
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    return messages
