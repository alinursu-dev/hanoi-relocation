from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    app.config['SECRET_KEY'] = 'dev-secret-key'
    CORS(app, supports_credentials=True)

    # Initialize SQLite database
    from app.database import init_db
    init_db()

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.today import today_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(today_bp)

    return app
