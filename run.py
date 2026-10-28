from app import create_app
from app.db import init_db
import os

app = create_app()

# Auto-create DB if it doesn't exist (needed for Docker)
with app.app_context():
    try:
        # Only init if DB file missing
        db_path = app.config.get('DATABASE', 'bookclub.db')
        if not os.path.exists(db_path):
            init_db()
            print(f"Database created at {db_path}")
    except Exception as e:
        print(f"DB init skipped: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
