"""
models.py — Full schema: Phase 1 + Phase 2
Phase 1 tables: languages, language_relationships, dialects, scripts, glyphs
Phase 2 tables: words, morphemes, senses, sense_fields, semantic_fields,
                pronunciations, inflection_paradigms, word_paradigms, inflected_forms
"""

import enum
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ===========================================================================
# Enums
# ===========================================================================

# --- Phase 1 ----------------------------------------------------------------

class LanguageStatus(enum.Enum):
    living      = "living"
    extinct     = "extinct"
    liturgical  = "liturgical"
    constructed = "constructed"


class WordOrder(enum.Enum):
    SOV  = "SOV"
    SVO  = "SVO"
    VSO  = "VSO"
    VOS  = "VOS"
    OVS  = "OVS"
    OSV  = "OSV"
    free = "free"


class MorphologicalType(enum.Enum):
    isolating     = "isolating"
    agglutinative = "agglutinative"
    fusional      = "fusional"
    polysynthetic = "polysynthetic"


class RelationshipType(enum.Enum):
    common_ancestor  = "common_ancestor"
    borrowing        = "borrowing"
    creole           = "creole"
    contact          = "contact"
    constructed_from = "constructed_from"


class ScriptType(enum.Enum):
    alphabet    = "alphabet"
    abjad       = "abjad"
    abugida     = "abugida"
    syllabary   = "syllabary"
    logographic = "logographic"
    mixed       = "mixed"
    other       = "other"


class ScriptDirection(enum.Enum):
    ltr           = "ltr"
    rtl           = "rtl"
    ttb           = "ttb"
    boustrophedon = "boustrophedon"


class GlyphCategory(enum.Enum):
    letter      = "letter"
    vowel_mark  = "vowel_mark"
    punctuation = "punctuation"
    numeral     = "numeral"
    ligature    = "ligature"
    other       = "other"


class DialectTag(enum.Enum):
    regional    = "regional"
    class_based = "class_based"
    archaic     = "archaic"
    pidgin      = "pidgin"
    creole      = "creole"
    liturgical  = "liturgical"
    informal    = "informal"
    other       = "other"


# --- Phase 2 ----------------------------------------------------------------

class PartOfSpeech(enum.Enum):
    noun         = "noun"
    verb         = "verb"
    adjective    = "adjective"
    adverb       = "adverb"
    pronoun      = "pronoun"
    numeral      = "numeral"
    particle     = "particle"
    conjunction  = "conjunction"
    adposition   = "adposition"
    interjection = "interjection"
    root         = "root"
    other        = "other"


class Register(enum.Enum):
    neutral    = "neutral"
    formal     = "formal"
    informal   = "informal"
    archaic    = "archaic"
    vulgar     = "vulgar"
    liturgical = "liturgical"
    poetic     = "poetic"


class MorphemeType(enum.Enum):
    root       = "root"
    prefix     = "prefix"
    suffix     = "suffix"
    infix      = "infix"
    circumfix  = "circumfix"
    clitic     = "clitic"


# ===========================================================================
# Phase 1 — Foundation
# ===========================================================================

class Language(db.Model):
    __tablename__ = "languages"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False, unique=True)
    native_name = db.Column(db.String(120))
    status      = db.Column(db.Enum(LanguageStatus), nullable=False,
                            default=LanguageStatus.constructed)
    description = db.Column(db.Text)

    default_word_order       = db.Column(db.Enum(WordOrder))
    morphological_type       = db.Column(db.Enum(MorphologicalType))
    phonemic_inventory_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Phase 1 back-refs
    dialects = db.relationship("Dialect", back_populates="language",
                               cascade="all, delete-orphan")
    relationships_as_source = db.relationship(
        "LanguageRelationship",
        foreign_keys="LanguageRelationship.source_language_id",
        back_populates="source_language",
        cascade="all, delete-orphan",
    )
    relationships_as_target = db.relationship(
        "LanguageRelationship",
        foreign_keys="LanguageRelationship.target_language_id",
        back_populates="target_language",
        cascade="all, delete-orphan",
    )

    # Phase 2 back-refs
    words                = db.relationship("Word", back_populates="language",
                                           cascade="all, delete-orphan")
    morphemes            = db.relationship("Morpheme", back_populates="language",
                                           cascade="all, delete-orphan")
    inflection_paradigms = db.relationship("InflectionParadigm",
                                           back_populates="language",
                                           cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Language {self.name!r} ({self.status.value})>"


class LanguageRelationship(db.Model):
    """
    Directed edge between two languages.
      borrowing:        source borrowed FROM target
      common_ancestor:  source and target share a proto-language
      creole:           source is the creole; target is substrate/superstrate
      contact:          mutual influence
      constructed_from: source was built from target
    """
    __tablename__ = "language_relationships"

    id                 = db.Column(db.Integer, primary_key=True)
    source_language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                                   ondelete="CASCADE"), nullable=False)
    target_language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                                   ondelete="CASCADE"), nullable=False)
    relationship_type  = db.Column(db.Enum(RelationshipType), nullable=False)

    era        = db.Column(db.String(120))
    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    source_language = db.relationship("Language", foreign_keys=[source_language_id],
                                      back_populates="relationships_as_source")
    target_language = db.relationship("Language", foreign_keys=[target_language_id],
                                      back_populates="relationships_as_target")

    __table_args__ = (
        db.UniqueConstraint("source_language_id", "target_language_id",
                            "relationship_type", name="uq_lang_rel"),
    )

    def __repr__(self):
        return (f"<LanguageRelationship {self.source_language_id} "
                f"--[{self.relationship_type.value}]--> {self.target_language_id}>")


class Dialect(db.Model):
    __tablename__ = "dialects"

    id                = db.Column(db.Integer, primary_key=True)
    language_id       = db.Column(db.Integer, db.ForeignKey("languages.id",
                                  ondelete="CASCADE"), nullable=False)
    parent_dialect_id = db.Column(db.Integer, db.ForeignKey("dialects.id",
                                  ondelete="SET NULL"), nullable=True)

    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    geo_tag     = db.Column(db.Enum(DialectTag), default=DialectTag.regional)
    region      = db.Column(db.String(200))
    intelligibility_with_parent = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Phase 1 back-refs
    language = db.relationship("Language", back_populates="dialects")
    parent   = db.relationship("Dialect", remote_side="Dialect.id",
                               back_populates="children")
    children = db.relationship("Dialect", back_populates="parent",
                               cascade="all, delete-orphan")
    scripts  = db.relationship("Script", back_populates="dialect",
                               cascade="all, delete-orphan")

    # Phase 2 back-refs
    words           = db.relationship("Word", back_populates="dialect")
    pronunciations  = db.relationship("Pronunciation", back_populates="dialect",
                                      cascade="all, delete-orphan")
    inflected_forms = db.relationship("InflectedForm", back_populates="dialect")

    def __repr__(self):
        return f"<Dialect {self.name!r} (lang={self.language_id})>"

    def ancestors(self):
        """Walk up the tree and return the chain of parent dialects."""
        chain, current = [], self.parent
        while current:
            chain.append(current)
            current = current.parent
        return chain


class Script(db.Model):
    """
    Writing system for a language, optionally scoped to a dialect.
    dialect_id = NULL → shared across all dialects of the language.
    """
    __tablename__ = "scripts"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    name               = db.Column(db.String(120), nullable=False)
    script_type        = db.Column(db.Enum(ScriptType), nullable=False)
    direction          = db.Column(db.Enum(ScriptDirection), nullable=False,
                                   default=ScriptDirection.ltr)
    font_face_name     = db.Column(db.String(120))
    font_file_ref      = db.Column(db.String(255))
    orthographic_notes = db.Column(db.Text)
    created_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dialect = db.relationship("Dialect", back_populates="scripts")
    glyphs  = db.relationship("Glyph", back_populates="script",
                              cascade="all, delete-orphan",
                              order_by="Glyph.glyph_order")

    def __repr__(self):
        return f"<Script {self.name!r} ({self.script_type.value})>"


class Glyph(db.Model):
    """
    One atomic character in a script.
    script_code is the stable app-internal identifier referenced by words
    and inflected forms (soft FK — not enforced at DB level).
    """
    __tablename__ = "glyphs"

    id                = db.Column(db.Integer, primary_key=True)
    script_id         = db.Column(db.Integer, db.ForeignKey("scripts.id",
                                  ondelete="CASCADE"), nullable=False)
    script_code       = db.Column(db.String(40), nullable=False)
    unicode_codepoint = db.Column(db.String(10))
    category          = db.Column(db.Enum(GlyphCategory), default=GlyphCategory.letter)
    romanization      = db.Column(db.String(40))
    ipa_value         = db.Column(db.String(40))
    name              = db.Column(db.String(120))
    description       = db.Column(db.Text)
    glyph_order       = db.Column(db.Integer, default=0)
    contextual_notes  = db.Column(db.Text)

    script = db.relationship("Script", back_populates="glyphs")

    __table_args__ = (
        db.UniqueConstraint("script_id", "script_code", name="uq_glyph_code"),
    )

    def __repr__(self):
        return f"<Glyph {self.script_code!r} rom={self.romanization!r} ipa={self.ipa_value!r}>"


# ===========================================================================
# Phase 2 — Core Lexicon
# ===========================================================================

class Word(db.Model):
    """
    A lexical entry at the language level.

    dialect_id is nullable — NULL means the word is shared across all dialects.
    Set it only for dialect-exclusive vocabulary (regional slang, archaic forms).

    script_code is a soft FK into glyphs.script_code for the primary written
    form.  Dialect-specific written realisations live in InflectedForm.
    """
    __tablename__ = "words"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    lemma        = db.Column(db.String(255), nullable=False)
    romanization = db.Column(db.String(255))
    script_code  = db.Column(db.String(40))   # soft FK → glyphs.script_code

    pos         = db.Column(db.Enum(PartOfSpeech), nullable=False)
    pos_subtype = db.Column(db.String(80))    # e.g. "transitive", "animate", "mass noun"
    register    = db.Column(db.Enum(Register), nullable=False, default=Register.neutral)

    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language        = db.relationship("Language", back_populates="words")
    dialect         = db.relationship("Dialect",  back_populates="words")
    senses          = db.relationship("Sense", back_populates="word",
                                      cascade="all, delete-orphan",
                                      order_by="Sense.sense_order")
    pronunciations  = db.relationship("Pronunciation", back_populates="word",
                                      cascade="all, delete-orphan")
    inflected_forms = db.relationship("InflectedForm", back_populates="word",
                                      cascade="all, delete-orphan")
    word_paradigms  = db.relationship("WordParadigm", back_populates="word",
                                      cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Word {self.lemma!r} ({self.pos.value})>"


class Morpheme(db.Model):
    """
    First-class morpheme entry — roots, affixes, clitics.

    form        — canonical shape, e.g. "-ek", "vel-", "-al-"
    gloss       — Leipzig-style label, e.g. "PL", "PAST", "CAUS"
    script_code — soft FK → glyphs.script_code
    """
    __tablename__ = "morphemes"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)

    form          = db.Column(db.String(120), nullable=False)
    romanization  = db.Column(db.String(120))
    script_code   = db.Column(db.String(40))
    ipa           = db.Column(db.String(120))

    morpheme_type = db.Column(db.Enum(MorphemeType), nullable=False)
    pos           = db.Column(db.Enum(PartOfSpeech))
    gloss         = db.Column(db.String(80))
    meaning       = db.Column(db.Text)
    notes         = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="morphemes")

    def __repr__(self):
        return f"<Morpheme {self.form!r} [{self.morpheme_type.value}] gloss={self.gloss!r}>"


# ---------------------------------------------------------------------------
# Senses + semantic fields
# ---------------------------------------------------------------------------

# Junction table — no model class; accessed via secondary= on both sides
sense_fields = db.Table(
    "sense_fields",
    db.Column("sense_id", db.Integer,
              db.ForeignKey("senses.id", ondelete="CASCADE"),
              primary_key=True),
    db.Column("semantic_field_id", db.Integer,
              db.ForeignKey("semantic_fields.id", ondelete="CASCADE"),
              primary_key=True),
)


class Sense(db.Model):
    __tablename__ = "senses"

    id          = db.Column(db.Integer, primary_key=True)
    word_id     = db.Column(db.Integer, db.ForeignKey("words.id",
                            ondelete="CASCADE"), nullable=False)
    sense_order = db.Column(db.Integer, nullable=False, default=1)

    definition          = db.Column(db.Text, nullable=False)
    example_sentence    = db.Column(db.Text)   # in the conlang
    example_translation = db.Column(db.Text)   # English gloss

    notes = db.Column(db.Text)

    word            = db.relationship("Word", back_populates="senses")
    semantic_fields = db.relationship("SemanticField",
                                      secondary="sense_fields",
                                      back_populates="senses")

    def __repr__(self):
        preview = (self.definition or "")[:40]
        return f"<Sense word={self.word_id} order={self.sense_order} {preview!r}>"


class SemanticField(db.Model):
    __tablename__ = "semantic_fields"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False, unique=True)
    parent_field_id = db.Column(db.Integer, db.ForeignKey("semantic_fields.id",
                                ondelete="SET NULL"), nullable=True)
    description     = db.Column(db.Text)

    parent   = db.relationship("SemanticField", remote_side="SemanticField.id",
                               back_populates="children")
    children = db.relationship("SemanticField", back_populates="parent")
    senses   = db.relationship("Sense", secondary="sense_fields",
                               back_populates="semantic_fields")

    def __repr__(self):
        return f"<SemanticField {self.name!r}>"


# ---------------------------------------------------------------------------
# Pronunciations
# ---------------------------------------------------------------------------

class Pronunciation(db.Model):
    """
    One IPA record per word per dialect.
    romanization here may differ from word.romanization (dialect shift).
    """
    __tablename__ = "pronunciations"

    id         = db.Column(db.Integer, primary_key=True)
    word_id    = db.Column(db.Integer, db.ForeignKey("words.id",
                           ondelete="CASCADE"), nullable=False)
    dialect_id = db.Column(db.Integer, db.ForeignKey("dialects.id",
                           ondelete="CASCADE"), nullable=False)

    ipa          = db.Column(db.String(255), nullable=False)
    romanization = db.Column(db.String(255))
    audio_url    = db.Column(db.String(512))
    notes        = db.Column(db.Text)

    word    = db.relationship("Word",    back_populates="pronunciations")
    dialect = db.relationship("Dialect", back_populates="pronunciations")

    __table_args__ = (
        db.UniqueConstraint("word_id", "dialect_id", name="uq_pronunciation"),
    )

    def __repr__(self):
        return f"<Pronunciation word={self.word_id} dialect={self.dialect_id} /{self.ipa}/>"


# ---------------------------------------------------------------------------
# Inflection paradigms, word_paradigms, inflected forms
# ---------------------------------------------------------------------------

class InflectionParadigm(db.Model):
    """
    Named inflection template, e.g. "Class I Verb", "Animate Noun".
    Scoped to a language; individual slot realisations are dialect-aware
    via InflectedForm.
    """
    __tablename__ = "inflection_paradigms"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)

    name        = db.Column(db.String(120), nullable=False)
    pos         = db.Column(db.Enum(PartOfSpeech))
    description = db.Column(db.Text)

    language        = db.relationship("Language", back_populates="inflection_paradigms")
    word_paradigms  = db.relationship("WordParadigm", back_populates="paradigm",
                                      cascade="all, delete-orphan")
    inflected_forms = db.relationship("InflectedForm", back_populates="paradigm",
                                      cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InflectionParadigm {self.name!r}>"


class WordParadigm(db.Model):
    """Junction: which paradigm(s) a word follows."""
    __tablename__ = "word_paradigms"

    word_id     = db.Column(db.Integer, db.ForeignKey("words.id",
                            ondelete="CASCADE"), primary_key=True)
    paradigm_id = db.Column(db.Integer, db.ForeignKey("inflection_paradigms.id",
                            ondelete="CASCADE"), primary_key=True)

    word     = db.relationship("Word",               back_populates="word_paradigms")
    paradigm = db.relationship("InflectionParadigm", back_populates="word_paradigms")


class InflectedForm(db.Model):
    """
    One realised form of a word in a paradigm slot.

    form_label  — slot name, e.g. "1SG.PRES", "NOM.PL", "IMPERATIVE"
    form        — romanized surface form
    script_code — soft FK → glyphs.script_code
    dialect_id  — NULL = applies to all dialects; set for dialect-specific forms
    """
    __tablename__ = "inflected_forms"

    id          = db.Column(db.Integer, primary_key=True)
    word_id     = db.Column(db.Integer, db.ForeignKey("words.id",
                            ondelete="CASCADE"), nullable=False)
    paradigm_id = db.Column(db.Integer, db.ForeignKey("inflection_paradigms.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    form_label  = db.Column(db.String(80),  nullable=False)
    form        = db.Column(db.String(255), nullable=False)
    script_code = db.Column(db.String(40))
    ipa         = db.Column(db.String(255))

    word     = db.relationship("Word",               back_populates="inflected_forms")
    paradigm = db.relationship("InflectionParadigm", back_populates="inflected_forms")
    dialect  = db.relationship("Dialect",            back_populates="inflected_forms")

    __table_args__ = (
        db.UniqueConstraint("word_id", "paradigm_id", "form_label", "dialect_id",
                            name="uq_inflected_form"),
    )

    def __repr__(self):
        return f"<InflectedForm {self.form_label}={self.form!r} word={self.word_id}>"