from flask import Blueprint

export_bp = Blueprint("export", __name__)

@export_bp.route('/')
def export_home():
    return '<h1>Export Home</h1>'