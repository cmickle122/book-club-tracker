import sqlite3
from flask import g, current_app
from app.models import SCHEMA_SQL

def get_db():
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'bookclub.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()
    print("Database tables initialized successfully in bookclub.db!")

# ==============================================================================
# REUSABLE CUSTOM DATABASE HELPER FUNCTIONS
# ==============================================================================
# Write your code here:

# Example:
# def get_user_by_id(user_id):
#     db = get_db()
#     return db.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()

# To here.