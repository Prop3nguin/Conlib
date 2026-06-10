from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    print(app.config.get("SQLALCHEMY_DATABASE_URI"))
    db.init_app(app)
    migrate.init_app(app, db)

    # Import blueprints here
    from app.routes.languages import languages_bp
    from app.routes.lexicon import lexicon_bp
    from app.routes.translator import translator_bp
    from app.routes.export import export_bp

    app.register_blueprint(languages_bp)
    app.register_blueprint(lexicon_bp, url_prefix='/lexicon')
    app.register_blueprint(translator_bp, url_prefix='/translator')
    app.register_blueprint(export_bp, url_prefix='/export')

    return app