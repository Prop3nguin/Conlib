from flask import Blueprint, render_template

translator_bp = Blueprint("translator", __name__, url_prefix='/translator')

@translator_bp.route('/')
def translator_home():
    return render_template('translator.html')