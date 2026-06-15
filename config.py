"""
config.py — application configuration

Reads from environment variables (loaded from .env via python-dotenv).
Swapping SQLite for Postgres later means changing DATABASE_URL in .env —
nothing in this file needs to change.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level up from this file's directory)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # --- Core Flask settings -----------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-this-in-production")

    # --- Database ------------------------------------------------------------
    # Default: SQLite file in an `instance/` folder (Flask convention — Flask
    # creates this folder automatically and it's git-ignored alongside *.db).
    # Override via DATABASE_URL in .env, e.g.:
    #   DATABASE_URL=postgresql://user:pass@localhost:5432/conlang
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'conlang.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Server --------------------------------------------------------------
    # host="0.0.0.0" makes the app reachable by anyone on the same LAN.
    # Change HOST to "127.0.0.1" in .env to restrict to this machine only.
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

    # --- Uploads / exports -----------------------------------------------
    # Where etymology export.py writes generated .html files.
    EXPORTS_DIR = BASE_DIR / "exports"

    # Where custom fonts / static assets for scripts live (referenced by
    # scripts.font_file_ref in the database).
    FONTS_DIR = BASE_DIR / "app" / "static" / "fonts"