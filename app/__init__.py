from flask import Flask
from flask_login import LoginManager
from .db import db

login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = 'dev-secret-change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookclub.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
