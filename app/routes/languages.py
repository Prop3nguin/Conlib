from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Language, Dialect, Script, Glyph

languages_bp = Blueprint("languages", __name__)


# ------------------------------------------------------------------------------------------------------------
# Language-level database Editing
# ------------------------------------------------------------------------------------------------------------


@languages_bp.route('/')
def languages_home():
    """
    this route should contain the following sections & features: (Does not include elements initialized in base.html)
        priority ---
    - language list: table of all languages in the database, with links to their detail pages
        - a sub-list of dialects for each language, also linking to their detail pages and adding context for their relationships.

        later additions (QOL features) ---
    - search bar: allows users to search for languages by name, id, etc
    - filters: dropdowns or checkboxes to filter the language list by various criteria
    - stats: summary of how many languages and dialects currently shown with filters and search applied.
    """
    context = {
        "languages": Language.query.all(),
        "dialects" : Dialect.query.all()
    }

    return render_template('languages.html', **context)

@languages_bp.route('/<int:language_id>', methods=['GET', 'POST'])
def language_detail(language_id):
    language = Language.query.get_or_404(language_id)
    return render_template('language_detail.html', language=language)

@languages_bp.route('/add', methods=['GET', 'POST'])
def add_language():
    if request.method == 'POST':

        print(request.form)
        
        name = request.form['name']
        status = request.form['status']
        description = request.form['description']

        language = Language(
            name=name, 
            status=status,
            description=description
            )

        db.session.add(language)
        db.session.flush()

        root_dialect = Dialect(
            language_id=language.id,
            name="Root",
            description="Default dialect"
        )

        db.session.add(root_dialect)
        db.session.flush()

        language.default_dialect_id = root_dialect.id

        db.session.commit()

        return redirect(url_for('languages.languages_home'))

    return render_template('add_language.html')

@languages_bp.route('/delete/<int:language_id>', methods=["GET", "POST"])
def delete_language(language_id):

    context = {
        "language" : Language.query.get_or_404(language_id)
    }
    if request.method == "POST":
        language = Language.query.get_or_404(language_id)
        try:
            db.session.delete(language)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem deleting that Language'
    
    else :

        context = {
            "language" : Language.query.get_or_404(language_id)
        }

        return render_template('delete_lang_confirm.html', **context)


# ------------------------------------------------------------------------------------------------------------
# Dialect-level database Editing
# ------------------------------------------------------------------------------------------------------------

@languages_bp.route('/<int:language_id>/dialects/<int:dialect_id>', methods=['GET', 'POST'])
def dialects(dialect_id, language_id):
    # View specific page for a single dialect of a language
    context = {
        "language": Language.query.get_or_404(language_id),
        "dialect" : Dialect.query.get_or_404(dialect_id)
    }

    return render_template('dialect_detail.html', **context)

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

