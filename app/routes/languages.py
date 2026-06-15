from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Language, Dialect, Script, Glyph

languages_bp = Blueprint("languages", __name__)

@languages_bp.route('/')
def languages_home():
    """
    this route should contain the following sections & features: (Does not include elements initialized in base.html)
        priority ---
    - language list: table of all languages in the database, with links to their detail pages
        - a sub-list of dialects for each language, also linking to their detail pages and adding context for their relationships.

        later additions (QOL features) ---
    - search bar: allows users to search for languages by name, family, region, etc
    - filters: dropdowns or checkboxes to filter the language list by various criteria (e.g. language family, number of speakers, etc)
    - stats: summary of how many languages, dialects, scripts, and glyphs currently shown with filters and search applied.
    """
    context = {
        "languages": Language.query.all(),
    }

    return render_template('languages.html', **context)

@languages_bp.route('/<int:language_id>', methods=['GET', 'POST'])
def language_detail(language_id):
    # Implementation for handling language detail view
    pass

@languages_bp.route('/dialects', methods=['GET', 'POST'])
def dialects():
    # Implementation for handling dialects view
    pass

@languages_bp.route('/scripts', methods=['GET', 'POST'])
def scripts():
    # Implementation for handling scripts view
    pass

@languages_bp.route('/glyphs:<int:script_id>', methods=['GET', 'POST'])
def glyphs(script_id):
    # Implementation for handling glyphs view
    pass

@languages_bp.route('/DBStructure', methods=['GET', 'POST'])
def db_structure():
    
    context = {
        "languages": Language.query.all(),
        "dialects": Dialect.query.all(),
        "scripts": Script.query.all(),
        "glyphs": Glyph.query.all()
    }

    return render_template('db_structure.html', **context)

@languages_bp.route('/add', methods=['GET', 'POST'])
def add_language():
    if request.method == 'POST':
        
        new_language = Language()
        db.session.add(new_language)
        db.session.commit()

        return redirect(url_for('languages.languages_home'))

    return render_template('add_language.html')