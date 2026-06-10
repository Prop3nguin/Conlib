from flask import Blueprint

languages_bp = Blueprint("languages", __name__)

@languages_bp.route('/')
def languages_home():
    return '<h1>Languages Home</h1>'
