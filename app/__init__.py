"""
app/__init__.py — application factory

db and migrate are defined ONCE here as module-level objects so they can be
imported by models.py and routes without circular imports. models.py should
import db from here (or, if db is defined in models.py instead, this file
should import it from there — pick ONE source of truth, never define
SQLAlchemy() in both places).
"""

from flask import Flask
from flask_migrate import Migrate

from app.models import db   # db = SQLAlchemy() lives in models.py — single source of truth

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    # --- Blueprints ----------------------------------------------------------
    from app.routes.languages import languages_bp
    from app.routes.lexicon import lexicon_bp
    from app.routes.translator import translator_bp
    from app.routes.export import export_bp

    app.register_blueprint(languages_bp)
    app.register_blueprint(lexicon_bp)
    app.register_blueprint(translator_bp)
    app.register_blueprint(export_bp)

    return app