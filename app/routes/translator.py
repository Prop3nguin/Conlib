from flask import Blueprint

translator_bp = Blueprint("translator", __name__)

@translator_bp.route('/')
def translator_home():
    return '<h1>Translator Home</h1>'