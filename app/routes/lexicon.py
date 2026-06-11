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

from flask import Blueprint, request, jsonify, abort
from app.models import (
    db,
    Word, Morpheme,
    Sense, SemanticField,
    Pronunciation,
    InflectionParadigm, WordParadigm, InflectedForm,
    GrammarRule, PhonologyRule,
)

lexicon_bp = Blueprint("lexicon", __name__, url_prefix="/lexicon")

# ===========================================================================
# Words  (scoped to language; dialect optional filter)
# ===========================================================================

@lexicon_bp.route("/languages/<int:language_id>/words", methods=["GET", "POST"])
def words(language_id):
    """
    GET  — list all words for a language.
           Optional query params: ?dialect_id=, ?pos=, ?register=, ?q= (lemma search)
    POST — create a new word.
    """
    if request.method == "GET":
        query = Word.query.filter_by(language_id=language_id)
        if dialect_id := request.args.get("dialect_id", type=int):
            query = query.filter_by(dialect_id=dialect_id)
        if pos := request.args.get("pos"):
            query = query.filter_by(pos=pos)
        if register := request.args.get("register"):
            query = query.filter_by(register=register)
        if q := request.args.get("q"):
            query = query.filter(Word.lemma.ilike(f"%{q}%"))
        words = query.order_by(Word.lemma).all()
        return jsonify([_word_summary(w) for w in words])

    data = request.get_json(force=True)
    word = Word(language_id=language_id, **_pick(data,
        "lemma", "romanization", "script_code", "pos",
        "pos_subtype", "register", "dialect_id", "notes"))
    db.session.add(word)
    db.session.commit()
    return jsonify(_word_detail(word)), 201


@lexicon_bp.route("/languages/<int:language_id>/words/<int:word_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def word(language_id, word_id):
    """Single word — fetch, update, or delete."""
    w = Word.query.filter_by(id=word_id, language_id=language_id).first_or_404()

    if request.method == "GET":
        return jsonify(_word_detail(w))

    if request.method == "DELETE":
        db.session.delete(w)
        db.session.commit()
        return "", 204

    data = request.get_json(force=True)
    _apply(w, data, "lemma", "romanization", "script_code", "pos",
           "pos_subtype", "register", "dialect_id", "notes")
    db.session.commit()
    return jsonify(_word_detail(w))


# ===========================================================================
# Search  (cross-language lexicon search)
# ===========================================================================

@lexicon_bp.route("/search", methods=["GET"])
def search():
    """
    Full-text search across lemma, romanization, and sense definitions.
    Required: ?q=  Optional: ?language_id=, ?pos=
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    query = Word.query.filter(
        db.or_(
            Word.lemma.ilike(f"%{q}%"),
            Word.romanization.ilike(f"%{q}%"),
        )
    )
    if lang_id := request.args.get("language_id", type=int):
        query = query.filter_by(language_id=lang_id)
    if pos := request.args.get("pos"):
        query = query.filter_by(pos=pos)

    results = query.order_by(Word.lemma).limit(50).all()
    return jsonify([_word_summary(w) for w in results])


# ===========================================================================
# Senses  (children of a word)
# ===========================================================================

@lexicon_bp.route("/words/<int:word_id>/senses", methods=["GET", "POST"])
def senses(word_id):
    """
    GET  — list all senses for a word, in sense_order.
    POST — add a new sense.
    """
    Word.query.get_or_404(word_id)

    if request.method == "GET":
        rows = (Sense.query.filter_by(word_id=word_id)
                .order_by(Sense.sense_order).all())
        return jsonify([_sense_dict(s) for s in rows])

    data = request.get_json(force=True)
    sense = Sense(word_id=word_id, **_pick(data,
        "sense_order", "definition", "example_sentence",
        "example_translation", "notes"))
    db.session.add(sense)
    db.session.commit()
    return jsonify(_sense_dict(sense)), 201


@lexicon_bp.route("/words/<int:word_id>/senses/<int:sense_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def sense(word_id, sense_id):
    s = Sense.query.filter_by(id=sense_id, word_id=word_id).first_or_404()

    if request.method == "GET":
        return jsonify(_sense_dict(s))
    if request.method == "DELETE":
        db.session.delete(s)
        db.session.commit()
        return "", 204

    data = request.get_json(force=True)
    _apply(s, data, "sense_order", "definition",
           "example_sentence", "example_translation", "notes")
    db.session.commit()
    return jsonify(_sense_dict(s))


# ===========================================================================
# Semantic fields  (language-agnostic taxonomy)
# ===========================================================================

@lexicon_bp.route("/semantic-fields", methods=["GET", "POST"])
def semantic_fields():
    """
    GET  — full hierarchy; ?parent_id= to fetch one level.
    POST — create a field.
    """
    if request.method == "GET":
        query = SemanticField.query
        if parent_id := request.args.get("parent_id", type=int):
            query = query.filter_by(parent_field_id=parent_id)
        else:
            # Return roots by default
            query = query.filter_by(parent_field_id=None)
        return jsonify([_sf_dict(f) for f in query.order_by(SemanticField.name).all()])

    data = request.get_json(force=True)
    field = SemanticField(**_pick(data, "name", "parent_field_id", "description"))
    db.session.add(field)
    db.session.commit()
    return jsonify(_sf_dict(field)), 201


@lexicon_bp.route("/semantic-fields/<int:field_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def semantic_field(field_id):
    f = SemanticField.query.get_or_404(field_id)
    if request.method == "GET":
        return jsonify(_sf_dict(f))
    if request.method == "DELETE":
        db.session.delete(f)
        db.session.commit()
        return "", 204
    _apply(f, request.get_json(force=True), "name", "parent_field_id", "description")
    db.session.commit()
    return jsonify(_sf_dict(f))


@lexicon_bp.route("/senses/<int:sense_id>/semantic-fields", methods=["GET", "POST", "DELETE"])
def sense_semantic_fields(sense_id):
    """
    GET    — list semantic fields tagged on this sense.
    POST   — tag a semantic field onto this sense. Body: {"semantic_field_id": N}
    DELETE — remove a tag.                          Body: {"semantic_field_id": N}
    """
    s = Sense.query.get_or_404(sense_id)
    if request.method == "GET":
        return jsonify([_sf_dict(f) for f in s.semantic_fields])

    field_id = request.get_json(force=True).get("semantic_field_id")
    field = SemanticField.query.get_or_404(field_id)

    if request.method == "POST":
        if field not in s.semantic_fields:
            s.semantic_fields.append(field)
            db.session.commit()
        return jsonify(_sf_dict(field)), 201

    s.semantic_fields.remove(field)
    db.session.commit()
    return "", 204


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
    if request.method == "GET":
        rows = Pronunciation.query.filter_by(
            word_id=word_id, dialect_id=dialect_id).all()
        return jsonify([_pron_dict(p) for p in rows])

    data = request.get_json(force=True)
    pron = Pronunciation(word_id=word_id, dialect_id=dialect_id,
                         **_pick(data, "ipa", "romanization", "audio_url", "notes"))
    db.session.merge(pron)   # merge handles upsert on unique constraint
    db.session.commit()
    return jsonify(_pron_dict(pron)), 201


@lexicon_bp.route("/dialects/<int:dialect_id>/pronunciations",
                  methods=["GET"])
def dialect_pronunciations(dialect_id):
    """All pronunciations recorded for a dialect — useful for bulk export."""
    rows = Pronunciation.query.filter_by(dialect_id=dialect_id).all()
    return jsonify([_pron_dict(p) for p in rows])


# ===========================================================================
# Morphemes  (scoped to language)
# ===========================================================================

@lexicon_bp.route("/languages/<int:language_id>/morphemes", methods=["GET", "POST"])
def morphemes(language_id):
    """
    GET  — list morphemes. ?type= (root/prefix/suffix/…), ?pos=, ?q= (form search)
    POST — create a morpheme.
    """
    if request.method == "GET":
        query = Morpheme.query.filter_by(language_id=language_id)
        if mtype := request.args.get("type"):
            query = query.filter_by(morpheme_type=mtype)
        if pos := request.args.get("pos"):
            query = query.filter_by(pos=pos)
        if q := request.args.get("q"):
            query = query.filter(Morpheme.form.ilike(f"%{q}%"))
        return jsonify([_morpheme_dict(m) for m in
                        query.order_by(Morpheme.morpheme_type, Morpheme.form).all()])

    data = request.get_json(force=True)
    m = Morpheme(language_id=language_id, **_pick(data,
        "form", "romanization", "script_code", "ipa",
        "morpheme_type", "pos", "gloss", "meaning", "notes"))
    db.session.add(m)
    db.session.commit()
    return jsonify(_morpheme_dict(m)), 201


@lexicon_bp.route("/languages/<int:language_id>/morphemes/<int:morpheme_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def morpheme(language_id, morpheme_id):
    m = Morpheme.query.filter_by(id=morpheme_id,
                                  language_id=language_id).first_or_404()
    if request.method == "GET":
        return jsonify(_morpheme_dict(m))
    if request.method == "DELETE":
        db.session.delete(m)
        db.session.commit()
        return "", 204
    _apply(m, request.get_json(force=True),
           "form", "romanization", "script_code", "ipa",
           "morpheme_type", "pos", "gloss", "meaning", "notes")
    db.session.commit()
    return jsonify(_morpheme_dict(m))


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
    if request.method == "GET":
        query = InflectionParadigm.query.filter_by(language_id=language_id)
        if pos := request.args.get("pos"):
            query = query.filter_by(pos=pos)
        return jsonify([_paradigm_dict(p) for p in
                        query.order_by(InflectionParadigm.name).all()])

    data = request.get_json(force=True)
    paradigm = InflectionParadigm(language_id=language_id,
                                   **_pick(data, "name", "pos", "description"))
    db.session.add(paradigm)
    db.session.commit()
    return jsonify(_paradigm_dict(paradigm)), 201


@lexicon_bp.route("/languages/<int:language_id>/inflection-paradigms/<int:paradigm_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def inflection_paradigm(language_id, paradigm_id):
    p = InflectionParadigm.query.filter_by(
        id=paradigm_id, language_id=language_id).first_or_404()
    if request.method == "GET":
        return jsonify(_paradigm_dict(p))
    if request.method == "DELETE":
        db.session.delete(p)
        db.session.commit()
        return "", 204
    _apply(p, request.get_json(force=True), "name", "pos", "description")
    db.session.commit()
    return jsonify(_paradigm_dict(p))


@lexicon_bp.route("/words/<int:word_id>/paradigms", methods=["GET", "POST", "DELETE"])
def word_paradigms(word_id):
    """
    GET    — list paradigms this word follows.
    POST   — assign a paradigm. Body: {"paradigm_id": N}
    DELETE — remove a paradigm assignment. Body: {"paradigm_id": N}
    """
    w = Word.query.get_or_404(word_id)
    if request.method == "GET":
        return jsonify([_paradigm_dict(wp.paradigm) for wp in w.word_paradigms])

    paradigm_id = request.get_json(force=True).get("paradigm_id")
    paradigm = InflectionParadigm.query.get_or_404(paradigm_id)

    if request.method == "POST":
        if not WordParadigm.query.filter_by(
                word_id=word_id, paradigm_id=paradigm_id).first():
            db.session.add(WordParadigm(word_id=word_id, paradigm_id=paradigm_id))
            db.session.commit()
        return jsonify(_paradigm_dict(paradigm)), 201

    wp = WordParadigm.query.filter_by(
        word_id=word_id, paradigm_id=paradigm_id).first_or_404()
    db.session.delete(wp)
    db.session.commit()
    return "", 204


@lexicon_bp.route("/words/<int:word_id>/inflected-forms", methods=["GET", "POST"])
def inflected_forms(word_id):
    """
    GET  — all inflected forms for a word. ?dialect_id= to filter.
    POST — add a form.
    """
    Word.query.get_or_404(word_id)
    if request.method == "GET":
        query = InflectedForm.query.filter_by(word_id=word_id)
        if dialect_id := request.args.get("dialect_id", type=int):
            query = query.filter_by(dialect_id=dialect_id)
        return jsonify([_form_dict(f) for f in
                        query.order_by(InflectedForm.form_label).all()])

    data = request.get_json(force=True)
    form = InflectedForm(word_id=word_id, **_pick(data,
        "paradigm_id", "dialect_id", "form_label",
        "form", "script_code", "ipa"))
    db.session.add(form)
    db.session.commit()
    return jsonify(_form_dict(form)), 201


@lexicon_bp.route("/words/<int:word_id>/inflected-forms/<int:form_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def inflected_form(word_id, form_id):
    f = InflectedForm.query.filter_by(id=form_id, word_id=word_id).first_or_404()
    if request.method == "GET":
        return jsonify(_form_dict(f))
    if request.method == "DELETE":
        db.session.delete(f)
        db.session.commit()
        return "", 204
    _apply(f, request.get_json(force=True),
           "paradigm_id", "dialect_id", "form_label", "form", "script_code", "ipa")
    db.session.commit()
    return jsonify(_form_dict(f))


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
    if request.method == "GET":
        query = GrammarRule.query.filter_by(language_id=language_id)
        if rule_type := request.args.get("rule_type"):
            query = query.filter_by(rule_type=rule_type)
        if dialect_id := request.args.get("dialect_id", type=int):
            query = query.filter(
                db.or_(GrammarRule.dialect_id == dialect_id,
                       GrammarRule.dialect_id == None)  # noqa: E711
            )
        if request.args.get("active_only", "").lower() == "true":
            query = query.filter_by(is_active=True)
        rules = query.order_by(GrammarRule.rule_type, GrammarRule.rule_order).all()
        return jsonify([_grammar_rule_dict(r) for r in rules])

    data = request.get_json(force=True)
    rule = GrammarRule(language_id=language_id, **_pick(data,
        "dialect_id", "name", "rule_type", "rule_order",
        "pattern", "result", "example", "notes", "is_active"))
    db.session.add(rule)
    db.session.commit()
    return jsonify(_grammar_rule_dict(rule)), 201


@lexicon_bp.route("/languages/<int:language_id>/grammar-rules/<int:rule_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def grammar_rule(language_id, rule_id):
    r = GrammarRule.query.filter_by(
        id=rule_id, language_id=language_id).first_or_404()
    if request.method == "GET":
        return jsonify(_grammar_rule_dict(r))
    if request.method == "DELETE":
        db.session.delete(r)
        db.session.commit()
        return "", 204
    _apply(r, request.get_json(force=True),
           "dialect_id", "name", "rule_type", "rule_order",
           "pattern", "result", "example", "notes", "is_active")
    db.session.commit()
    return jsonify(_grammar_rule_dict(r))


@lexicon_bp.route("/languages/<int:language_id>/grammar-rules/<int:rule_id>/toggle",
                  methods=["POST"])
def toggle_grammar_rule(language_id, rule_id):
    """Flip is_active without a full PUT — useful when testing the translator."""
    r = GrammarRule.query.filter_by(
        id=rule_id, language_id=language_id).first_or_404()
    r.is_active = not r.is_active
    db.session.commit()
    return jsonify({"id": r.id, "is_active": r.is_active})


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
    if request.method == "GET":
        query = PhonologyRule.query.filter_by(dialect_id=dialect_id)
        if rule_type := request.args.get("rule_type"):
            query = query.filter_by(rule_type=rule_type)
        if request.args.get("active_only", "").lower() == "true":
            query = query.filter_by(is_active=True)
        rules = query.order_by(PhonologyRule.rule_order).all()
        return jsonify([_phonology_rule_dict(r) for r in rules])

    data = request.get_json(force=True)
    rule = PhonologyRule(dialect_id=dialect_id, **_pick(data,
        "name", "rule_type", "rule_order",
        "input_ipa", "output_ipa", "environment",
        "formal_notation", "scope",
        "is_feeding", "is_bleeding",
        "example", "notes", "is_active"))
    db.session.add(rule)
    db.session.commit()
    return jsonify(_phonology_rule_dict(rule)), 201


@lexicon_bp.route("/dialects/<int:dialect_id>/phonology-rules/<int:rule_id>",
                  methods=["GET", "PUT", "PATCH", "DELETE"])
def phonology_rule(dialect_id, rule_id):
    r = PhonologyRule.query.filter_by(
        id=rule_id, dialect_id=dialect_id).first_or_404()
    if request.method == "GET":
        return jsonify(_phonology_rule_dict(r))
    if request.method == "DELETE":
        db.session.delete(r)
        db.session.commit()
        return "", 204
    _apply(r, request.get_json(force=True),
           "name", "rule_type", "rule_order",
           "input_ipa", "output_ipa", "environment",
           "formal_notation", "scope",
           "is_feeding", "is_bleeding",
           "example", "notes", "is_active")
    db.session.commit()
    return jsonify(_phonology_rule_dict(r))


@lexicon_bp.route("/dialects/<int:dialect_id>/phonology-rules/<int:rule_id>/toggle",
                  methods=["POST"])
def toggle_phonology_rule(dialect_id, rule_id):
    """Flip is_active — useful when testing translator output rule-by-rule."""
    r = PhonologyRule.query.filter_by(
        id=rule_id, dialect_id=dialect_id).first_or_404()
    r.is_active = not r.is_active
    db.session.commit()
    return jsonify({"id": r.id, "is_active": r.is_active})


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