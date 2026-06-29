"""
lexicon.py — Lexicon blueprint
Covers Phase 2 + Phase 3 routes:
  words, morphemes, senses, semantic fields,
  inflection paradigms, pronunciations,
  grammar rules, phonology rules

URL conventions:
  - All list routes:   GET  (returns all) + POST (creates one)
  - All detail routes: GET  (returns one) + PUT (full update) + PATCH (partial) + DELETE
  - Scoping:           words/morphemes/paradigms scoped by language_id
                       pronunciations/inflected forms scoped by dialect_id
                       phonology_rules scoped by dialect_id (always dialect-owned)
                       grammar_rules scoped by language_id (dialect_id is a filter param)
"""

from flask import Blueprint, request, jsonify, abort, render_template, redirect, url_for
from app.models import (
    db,
    Language, Dialect,
    Lexeme, Morpheme,
    Sense, SemanticField,
    Pronunciation,
    InflectionParadigm,
    GrammarRule, PhonologyRule,
)

lexicon_bp = Blueprint("lexicon", __name__, url_prefix="/lexicon")

# ===========================================================================
# Words  (scoped to language; dialect optional filter)
# ===========================================================================

@lexicon_bp.route("/<int:language_id>", methods=["GET", "POST"])
def lexemes(language_id):
    """
    GET  — list all lexemes for a language.
           Optional query params: ?dialect_id=, ?pos=, ?register=, ?q= (lemma search)
    POST — create a new lexeme.
    """

    language = Language.query.get_or_404(language_id)

    print(language.lexemes)
    print(len(language.lexemes))

    context = {
        "language" : language
    }

    if request.method == "POST" :
        return redirect( url_for('lexicon.add_lexeme', language_id = language.id))

    return render_template('lexicon.html', **context)

@lexicon_bp.route("/<int:language_id>/add_lexeme", methods=["GET", "POST"])
def add_lexeme(language_id) :

    language = Language.query.get_or_404(language_id)

    context = {
        "language" : language
    }

    if request.method == "POST" :

        print(request.form)

        lemma = request.form['lemma']
        gloss = request.form['gloss']
        part_of_speech = request.form['part_of_speech']
        notes = request.form['notes']

        lexeme = Lexeme(
            lemma=lemma,
            gloss=gloss,
            part_of_speech=part_of_speech,
            notes=notes,
            language_id=language.id
        )

        db.session.add(lexeme)
        db.session.commit()

        return redirect(url_for("lexicon.lexemes", language_id=language.id))

    return render_template("add_lexeme.html", **context)

@lexicon_bp.route("/<int:language_id>/lexeme/<int:lexeme_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def lexeme(language_id, lexeme_id):
    """Single word — fetch, update, or delete."""
    pass


# ===========================================================================
# Search  (cross-language lexicon search)
# ===========================================================================

@lexicon_bp.route("/search", methods=["GET"])
def search():
    """
    Full-text search across lemma, romanization, and sense definitions.
    Required: ?q=  Optional: ?language_id=, ?pos=
    """
    pass


# ===========================================================================
# Senses  (children of a word)
# ===========================================================================

@lexicon_bp.route("/lexeme/<int:lexeme_id>/senses", methods=["GET", "POST"])
def senses(word_id):
    """
    GET  — list all senses for a word, in sense_order.
    POST — add a new sense.
    """
    pass


@lexicon_bp.route("/lexeme/<int:lexeme_id>/senses/<int:sense_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def sense(lexeme_id, sense_id):
    pass


# ===========================================================================
# Semantic fields  (language-agnostic taxonomy)
# ===========================================================================

@lexicon_bp.route("/semantic-fields", methods=["GET", "POST"])
def semantic_fields():
    """
    GET  — full hierarchy; ?parent_id= to fetch one level.
    POST — create a field.
    """
    pass


@lexicon_bp.route("/semantic-fields/<int:field_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def semantic_field(field_id):
    pass


@lexicon_bp.route("/senses/<int:sense_id>/semantic-fields", methods=["GET", "POST", "DELETE"])
def sense_semantic_fields(sense_id):
    """
    GET    — list semantic fields tagged on this sense.
    POST   — tag a semantic field onto this sense. Body: {"semantic_field_id": N}
    DELETE — remove a tag.                          Body: {"semantic_field_id": N}
    """
    pass


# ===========================================================================
# Pronunciations  (scoped to dialect)
# ===========================================================================

@lexicon_bp.route("/dialects/<int:dialect_id>/words/<int:word_id>/pronunciations",
                  methods=["GET", "POST"])
def pronunciations(dialect_id, word_id):
    """
    GET  — pronunciation for this word in this dialect.
    POST — add or update (upsert by unique constraint).
    """
    pass


@lexicon_bp.route("/dialects/<int:dialect_id>/pronunciations",
                  methods=["GET"])
def dialect_pronunciations(dialect_id):
    """All pronunciations recorded for a dialect — useful for bulk export."""
    pass


# ===========================================================================
# Morphemes  (scoped to language)
# ===========================================================================

@lexicon_bp.route("/languages/<int:language_id>/morphemes", methods=["GET", "POST"])
def morphemes(language_id):
    """
    GET  — list morphemes. ?type= (root/prefix/suffix/…), ?pos=, ?q= (form search)
    POST — create a morpheme.
    """
    pass


@lexicon_bp.route("/languages/<int:language_id>/morphemes/<int:morpheme_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def morpheme(language_id, morpheme_id):
    pass


# ===========================================================================
# Inflection paradigms  (scoped to language)
# ===========================================================================

@lexicon_bp.route("/languages/<int:language_id>/inflection-paradigms",
                  methods=["GET", "POST"])
def inflection_paradigms(language_id):
    """
    GET  — list paradigms. ?pos= to filter by part of speech.
    POST — create a paradigm.
    """
    pass


@lexicon_bp.route("/languages/<int:language_id>/inflection-paradigms/<int:paradigm_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def inflection_paradigm(language_id, paradigm_id):
    pass


@lexicon_bp.route("/words/<int:word_id>/paradigms", methods=["GET", "POST", "DELETE"])
def word_paradigms(word_id):
    """
    GET    — list paradigms this word follows.
    POST   — assign a paradigm. Body: {"paradigm_id": N}
    DELETE — remove a paradigm assignment. Body: {"paradigm_id": N}
    """
    pass


@lexicon_bp.route("/lexeme/<int:lexeme_id>/inflected-forms", methods=["GET", "POST"])
def inflected_forms(lexeme_id):
    """
    GET  — all inflected forms for a word. ?dialect_id= to filter.
    POST — add a form.
    """
    pass


@lexicon_bp.route("/words/<int:word_id>/inflected-forms/<int:form_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def inflected_form(word_id, form_id):
    pass


# ===========================================================================
# Grammar rules  (Phase 3 — scoped to language, dialect optional filter)
# ===========================================================================

@lexicon_bp.route("/languages/<int:language_id>/grammar-rules", methods=["GET", "POST"])
def grammar_rules(language_id):
    """
    GET  — list grammar rules.
           ?rule_type= (morphology/syntax/phonology/cv_structure)
           ?dialect_id= (include rules for this dialect AND language-wide rules)
           ?active_only=true
    POST — create a rule.
    """
    pass


@lexicon_bp.route("/languages/<int:language_id>/grammar-rules/<int:rule_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def grammar_rule(language_id, rule_id):
    pass


@lexicon_bp.route("/languages/<int:language_id>/grammar-rules/<int:rule_id>/toggle",
                  methods=["POST"])
def toggle_grammar_rule(language_id, rule_id):
    """Flip is_active without a full PUT — useful when testing the translator."""
    pass


# ===========================================================================
# Phonology rules  (Phase 3 — always scoped to dialect)
# ===========================================================================

@lexicon_bp.route("/dialects/<int:dialect_id>/phonology-rules", methods=["GET", "POST"])
def phonology_rules(dialect_id):
    """
    GET  — list phonology rules for a dialect, in rule_order.
           ?rule_type= (assimilation/elision/sandhi/…)
           ?active_only=true
    POST — create a rule.
    """
    pass



@lexicon_bp.route("/dialects/<int:dialect_id>/phonology-rules/<int:rule_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def phonology_rule(dialect_id, rule_id):
    pass


@lexicon_bp.route("/dialects/<int:dialect_id>/phonology-rules/<int:rule_id>/toggle",
                  methods=["POST"])
def toggle_phonology_rule(dialect_id, rule_id):
    """Flip is_active — useful when testing translator output rule-by-rule."""
    pass

# ===========================================================================
# Serialisation helpers
# ===========================================================================

def _pick(data, *keys):
    """Return only the keys that are present in data."""
    return {k: data[k] for k in keys if k in data}


def _apply(obj, data, *keys):
    """Write present keys from data onto obj."""
    for k in keys:
        if k in data:
            setattr(obj, k, data[k])


def _word_summary(w):
    return {
        "id": w.id, "lemma": w.lemma, "romanization": w.romanization,
        "pos": w.pos.value if w.pos else None,
        "register": w.register.value if w.register else None,
        "dialect_id": w.dialect_id,
    }


def _word_detail(w):
    return {
        **_word_summary(w),
        "script_code": w.script_code,
        "pos_subtype": w.pos_subtype,
        "notes": w.notes,
        "senses": [_sense_dict(s) for s in w.senses],
        "pronunciations": [_pron_dict(p) for p in w.pronunciations],
        "paradigms": [wp.paradigm_id for wp in w.word_paradigms],
    }


def _sense_dict(s):
    return {
        "id": s.id, "word_id": s.word_id, "sense_order": s.sense_order,
        "definition": s.definition,
        "example_sentence": s.example_sentence,
        "example_translation": s.example_translation,
        "notes": s.notes,
        "semantic_fields": [f.id for f in s.semantic_fields],
    }


def _sf_dict(f):
    return {
        "id": f.id, "name": f.name,
        "parent_field_id": f.parent_field_id,
        "description": f.description,
        "children": [c.id for c in f.children],
    }


def _pron_dict(p):
    return {
        "id": p.id, "word_id": p.word_id, "dialect_id": p.dialect_id,
        "ipa": p.ipa, "romanization": p.romanization,
        "audio_url": p.audio_url, "notes": p.notes,
    }


def _morpheme_dict(m):
    return {
        "id": m.id, "language_id": m.language_id,
        "form": m.form, "romanization": m.romanization,
        "script_code": m.script_code, "ipa": m.ipa,
        "morpheme_type": m.morpheme_type.value if m.morpheme_type else None,
        "pos": m.pos.value if m.pos else None,
        "gloss": m.gloss, "meaning": m.meaning, "notes": m.notes,
    }


def _paradigm_dict(p):
    return {
        "id": p.id, "language_id": p.language_id,
        "name": p.name,
        "pos": p.pos.value if p.pos else None,
        "description": p.description,
    }


def _form_dict(f):
    return {
        "id": f.id, "word_id": f.word_id,
        "paradigm_id": f.paradigm_id, "dialect_id": f.dialect_id,
        "form_label": f.form_label, "form": f.form,
        "script_code": f.script_code, "ipa": f.ipa,
    }


def _grammar_rule_dict(r):
    return {
        "id": r.id, "language_id": r.language_id, "dialect_id": r.dialect_id,
        "name": r.name,
        "rule_type": r.rule_type.value if r.rule_type else None,
        "rule_order": r.rule_order,
        "pattern": r.pattern, "result": r.result,
        "example": r.example, "notes": r.notes,
        "is_active": r.is_active,
    }


def _phonology_rule_dict(r):
    return {
        "id": r.id, "dialect_id": r.dialect_id,
        "name": r.name,
        "rule_type": r.rule_type.value if r.rule_type else None,
        "rule_order": r.rule_order,
        "input_ipa": r.input_ipa, "output_ipa": r.output_ipa,
        "environment": r.environment,
        "formal_notation": r.formal_notation,
        "scope": r.scope.value if r.scope else None,
        "is_feeding": r.is_feeding, "is_bleeding": r.is_bleeding,
        "example": r.example, "notes": r.notes,
        "is_active": r.is_active,
    }