from flask import Blueprint

lexicon_bp = Blueprint("lexicon", __name__)

@lexicon_bp.route('/')
def lexicon_home():
    return '<h1>Lexicon Home</h1>'