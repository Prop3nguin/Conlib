from flask import Blueprint, render_template

export_bp = Blueprint("export", __name__)

@export_bp.route('/')
def export_home():
    return render_template('export.html')