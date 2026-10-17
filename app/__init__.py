import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['DATABASE'] = os.path.join(app.root_path, '..', 'bookclub.db')

    from app.routes_auth import auth_bp
    from app.routes_admin import admin_bp
    from app.routes_club import club_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(club_bp)

    from app.db import close_db
    app.teardown_appcontext(close_db)

    return app
