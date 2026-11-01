from app import create_app
from app.db import init_db
import os

app = create_app()

with app.app_context():
    database_url = os.environ.get('TURSO_DATABASE_URL')
    auth_token = os.environ.get('TURSO_AUTH_TOKEN')

    if database_url and auth_token:
        try:
            init_db()
            print("Turso database tables initialized successfully!")
        except Exception as e:
            raise RuntimeError(
                "Failed to initialize the Turso database."
            ) from e
    else:
        try:
            db_path = app.config.get('DATABASE', 'bookclub.db')
            if not os.path.exists(db_path):
                init_db()
                print(f"Database created at {db_path}")
        except Exception as e:
            print(f"DB init skipped: {e}")

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('FLASK_DEBUG') == '1',
        host='0.0.0.0',
        port=5000
    )