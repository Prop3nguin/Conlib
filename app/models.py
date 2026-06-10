from flask import Blueprint

models = Blueprint("models", __name__, template_folder="templates", static_folder="static")

@models.route('/')
def home():
    return '<h1>Test</h1>'