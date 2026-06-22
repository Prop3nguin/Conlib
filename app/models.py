"""
models.py — Full schema, restructured to match ERD
Tables:
  languages, language_relationships,
  dialects, scripts, glyphs,
  morphemes, semantic_fields,
  inflection_paradigms,
  lexemes, word_forms,
  senses, sense_semantic_fields,
  pronunciations,
  idioms, idiom_words,
  grammar_rules, phonology_rules,
  translation_memories,
  etymology_articles, etymology_events,
  sample_texts

After any edit:
    flask db migrate -m "describe change"
    flask db upgrade

Fresh start (no existing data):
    delete instance/conlang.db and migrations/versions/*.py
    flask db init
    flask db migrate -m "initial schema"
    flask db upgrade
"""

import enum
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ===========================================================================
# Enums
# ===========================================================================

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
    borrowing        = "borrowing"        # source borrowed FROM target
    creole           = "creole"           # source is the creole
    contact          = "contact"          # mutual influence
    constructed_from = "constructed_from"


class ScriptType(enum.Enum):
    alphabet    = "alphabet"
    abjad         = "abjad"
    polysynthetic = "polysynthetic"
    abugida       = "abugida"
    syllabary     = "syllabary"
    logographic   = "logographic"
    mixed         = "mixed"
    other         = "other"


class ScriptDirection(enum.Enum):
    ltr           = "ltr"
    rtl           = "rtl"
    ttb           = "ttb"
    boustrophedon = "boustrophedon"


class DialectTag(enum.Enum):
    regional    = "regional"
    class_based = "class_based"
    archaic     = "archaic"
    pidgin      = "pidgin"
    creole      = "creole"
    liturgical  = "liturgical"
    informal    = "informal"
    other       = "other"


class Register(enum.Enum):
    neutral    = "neutral"
    formal     = "formal"
    informal   = "informal"
    archaic    = "archaic"
    vulgar     = "vulgar"
    liturgical = "liturgical"
    poetic     = "poetic"


class TranslationSource(enum.Enum):
    manual     = "manual"      # hand-entered; highest trust
    translator = "translator"  # produced by the rule-based engine
    imported   = "imported"    # bulk-imported


class TranslationStatus(enum.Enum):
    approved = "approved"  # confirmed correct; safe for regression tests
    draft    = "draft"     # plausible but not yet verified
    rejected = "rejected"  # known wrong; kept for audit trail


class ArticleType(enum.Enum):
    history    = "history"
    dialect    = "dialect"
    vocabulary = "vocabulary"
    loanwords  = "loanwords"
    cultural   = "cultural"
    other      = "other"


class EventType(enum.Enum):
    sound_change   = "sound_change"
    grammar_change = "grammar_change"
    dialect_split  = "dialect_split"
    contact_event  = "contact_event"
    cultural_event = "cultural_event"
    lexical_event  = "lexical_event"
    other          = "other"


# ===========================================================================
# Languages
# ===========================================================================

class Language(db.Model):
    __tablename__ = "languages"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False, unique=True)
    native_name = db.Column(db.String(120))
    status      = db.Column(db.Enum(LanguageStatus), nullable=False,
                            default=LanguageStatus.constructed)
    description = db.Column(db.Text)

    # Typological metadata
    default_word_order       = db.Column(db.Enum(WordOrder))
    morphological_type       = db.Column(db.Enum(MorphologicalType))
    phonemic_inventory_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

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
    morphemes            = db.relationship("Morpheme", back_populates="language",
                                           cascade="all, delete-orphan")
    inflection_paradigms = db.relationship("InflectionParadigm",
                                           back_populates="language",
                                           cascade="all, delete-orphan")
    lexemes              = db.relationship("Lexeme", back_populates="language",
                                           cascade="all, delete-orphan")
    idioms               = db.relationship("Idiom", back_populates="language",
                                           cascade="all, delete-orphan")
    translation_memories = db.relationship(
        "TranslationMemory",
        foreign_keys="[TranslationMemory.language_id]",
        back_populates="language",
        cascade="all, delete-orphan",
    )
    etymology_articles = db.relationship("EtymologyArticle",
                                         back_populates="language",
                                         cascade="all, delete-orphan")
    etymology_events   = db.relationship("EtymologyEvent",
                                         back_populates="language",
                                         cascade="all, delete-orphan")
    sample_texts       = db.relationship("SampleText",
                                         back_populates="language",
                                         cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Language {self.name!r} ({self.status.value})>"


# ===========================================================================
# Language relationships  (directed edge with metadata)
# ===========================================================================

class LanguageRelationship(db.Model):
    """
    Directed edge between two languages.
    Directionality: source -> target.
      borrowing:        source borrowed FROM target
      common_ancestor:  both share a proto-language
      creole:           source is the creole; target is substrate/superstrate
      contact:          mutual (create one row per direction if needed)
      constructed_from: source was built from target
    """
    __tablename__ = "language_relationships"

    id                 = db.Column(db.Integer, primary_key=True)
    source_language_id = db.Column(db.Integer,
                                   db.ForeignKey("languages.id", ondelete="CASCADE"),
                                   nullable=False)
    target_language_id = db.Column(db.Integer,
                                   db.ForeignKey("languages.id", ondelete="CASCADE"),
                                   nullable=False)
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


# ===========================================================================
# Dialects  (self-referential tree)
# ===========================================================================

class Dialect(db.Model):
    __tablename__ = "dialects"

    id                = db.Column(db.Integer, primary_key=True)
    language_id       = db.Column(db.Integer,
                                  db.ForeignKey("languages.id", ondelete="CASCADE"),
                                  nullable=False)
    parent_dialect_id = db.Column(db.Integer,
                                  db.ForeignKey("dialects.id", ondelete="SET NULL"),
                                  nullable=True)

    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    geo_tag     = db.Column(db.Enum(DialectTag), default=DialectTag.regional)
    region      = db.Column(db.String(200))
    intelligibility_with_parent = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="dialects")
    parent   = db.relationship("Dialect", remote_side="Dialect.id",
                               back_populates="children")
    children = db.relationship("Dialect", back_populates="parent",
                               cascade="all, delete-orphan")
    scripts          = db.relationship("Script", back_populates="dialect",
                                       cascade="all, delete-orphan")
    word_forms       = db.relationship("WordForm", back_populates="dialect",
                                       cascade="all, delete-orphan")
    idioms           = db.relationship("Idiom", back_populates="dialect")
    grammar_rules    = db.relationship("GrammarRule", back_populates="dialect",
                                       cascade="all, delete-orphan")
    phonology_rules  = db.relationship("PhonologyRule", back_populates="dialect",
                                       cascade="all, delete-orphan")
    translation_memories = db.relationship("TranslationMemory",
                                           back_populates="dialect",
                                           cascade="all, delete-orphan")
    etymology_events = db.relationship("EtymologyEvent", back_populates="dialect")
    sample_texts     = db.relationship("SampleText", back_populates="dialect")

    def __repr__(self):
        return f"<Dialect {self.name!r} (lang={self.language_id})>"

    def ancestors(self):
        """Walk up the tree and return the chain of parent dialects."""
        chain, current = [], self.parent
        while current:
            chain.append(current)
            current = current.parent
        return chain


# ===========================================================================
# Scripts + Glyphs
# ===========================================================================

class Script(db.Model):
    """
    Writing system for a language, optionally scoped to a dialect.
    dialect_id = NULL means shared across all dialects of the language.
    """
    __tablename__ = "scripts"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    dialect_id  = db.Column(db.Integer,
                            db.ForeignKey("dialects.id", ondelete="SET NULL"),
                            nullable=True)

    name               = db.Column(db.String(120), nullable=False)
    script_type        = db.Column(db.Enum(ScriptType), nullable=False)
    direction          = db.Column(db.Enum(ScriptDirection), nullable=False,
                                   default=ScriptDirection.ltr)
    font_face_name     = db.Column(db.String(120))
    font_file_ref      = db.Column(db.String(255))
    orthographic_notes = db.Column(db.Text)
    created_at         = db.Column(db.DateTime,
                                   default=lambda: datetime.now(timezone.utc))

    dialect = db.relationship("Dialect", back_populates="scripts")
    glyphs  = db.relationship("Glyph", back_populates="script",
                              cascade="all, delete-orphan",
                              order_by="Glyph.id")

    def __repr__(self):
        return f"<Script {self.name!r} ({self.script_type.value})>"


class Glyph(db.Model):
    """
    One atomic character in a script.

    symbol        — the glyph identifier / font code used throughout the app
    meaning       — human-readable label, e.g. "voiceless dental fricative"
    unicode_value — hex codepoint, e.g. "E001" or "0041"
    """
    __tablename__ = "glyphs"

    id            = db.Column(db.Integer, primary_key=True)
    script_id     = db.Column(db.Integer,
                              db.ForeignKey("scripts.id", ondelete="CASCADE"),
                              nullable=False)
    symbol        = db.Column(db.String(40), nullable=False)
    meaning       = db.Column(db.String(255))
    unicode_value = db.Column(db.String(10))

    script = db.relationship("Script", back_populates="glyphs")

    __table_args__ = (
        db.UniqueConstraint("script_id", "symbol", name="uq_glyph_symbol"),
    )

    def __repr__(self):
        return f"<Glyph {self.symbol!r} ({self.meaning!r})>"


# ===========================================================================
# Morphemes
# ===========================================================================

class Morpheme(db.Model):
    """
    First-class morpheme entry — roots, prefixes, suffixes, infixes, clitics.
    Scoped to a language (morphemes are language-level, not dialect-specific).
    """
    __tablename__ = "morphemes"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)

    form    = db.Column(db.String(120), nullable=False)
    meaning = db.Column(db.Text)
    notes   = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="morphemes")

    def __repr__(self):
        return f"<Morpheme {self.form!r} (lang={self.language_id})>"


# ===========================================================================
# Semantic fields  (hierarchical tagging taxonomy)
# ===========================================================================

class SemanticField(db.Model):
    __tablename__ = "semantic_fields"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False, unique=True)
    parent_field_id = db.Column(db.Integer,
                                db.ForeignKey("semantic_fields.id",
                                              ondelete="SET NULL"),
                                nullable=True)
    description     = db.Column(db.Text)

    parent   = db.relationship("SemanticField", remote_side="SemanticField.id",
                               back_populates="children")
    children = db.relationship("SemanticField", back_populates="parent")
    senses   = db.relationship("Sense", secondary="sense_semantic_fields",
                               back_populates="semantic_fields")

    def __repr__(self):
        return f"<SemanticField {self.name!r}>"


# ===========================================================================
# Inflection paradigms
# ===========================================================================

class InflectionParadigm(db.Model):
    """
    Named inflection template, e.g. "Class I Verb", "Animate Noun".
    Scoped to a language. Lexemes reference a paradigm directly via FK
    (one paradigm per lexeme — replaces the old word_paradigms junction).
    """
    __tablename__ = "inflection_paradigms"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)

    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    language = db.relationship("Language", back_populates="inflection_paradigms")
    lexemes  = db.relationship("Lexeme", back_populates="paradigm")

    def __repr__(self):
        return f"<InflectionParadigm {self.name!r}>"


# ===========================================================================
# Lexemes  (core lexical entries — replaces "words")
# ===========================================================================

class Lexeme(db.Model):
    """
    A lexical entry at the language level.

    paradigm_id  — direct FK to the lexeme's inflection paradigm.
                   NULL = uninflected or paradigm not yet assigned.
                   Replaces the old word_paradigms many-to-many junction.

    gloss        — brief English meaning used in glosses and search.
    part_of_speech — free-text POS label (noun, verb, adj, etc.)
    """
    __tablename__ = "lexemes"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    paradigm_id = db.Column(db.Integer,
                            db.ForeignKey("inflection_paradigms.id",
                                          ondelete="SET NULL"),
                            nullable=True)

    lemma          = db.Column(db.String(255), nullable=False)
    gloss          = db.Column(db.Text)
    part_of_speech = db.Column(db.String(80))
    notes          = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language   = db.relationship("Language", back_populates="lexemes")
    paradigm   = db.relationship("InflectionParadigm", back_populates="lexemes")
    senses     = db.relationship("Sense", back_populates="lexeme",
                                 cascade="all, delete-orphan")
    word_forms = db.relationship("WordForm", back_populates="lexeme",
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lexeme {self.lemma!r} (lang={self.language_id})>"


# ===========================================================================
# Word forms  (dialect-aware surface forms — replaces "inflected_forms")
# ===========================================================================

class WordForm(db.Model):
    """
    A single realised surface form of a lexeme in a given dialect.

    written_form  — the form as it appears in writing / romanization
    dialect_id    — which dialect; NULL = dialect-neutral default
    notes         — free-text for grammatical slot label, e.g. "1SG.PRES"
    """
    __tablename__ = "word_forms"

    id         = db.Column(db.Integer, primary_key=True)
    lexeme_id  = db.Column(db.Integer,
                           db.ForeignKey("lexemes.id", ondelete="CASCADE"),
                           nullable=False)
    dialect_id = db.Column(db.Integer,
                           db.ForeignKey("dialects.id", ondelete="SET NULL"),
                           nullable=True)

    written_form = db.Column(db.String(255), nullable=False)
    notes        = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    lexeme         = db.relationship("Lexeme", back_populates="word_forms")
    dialect        = db.relationship("Dialect", back_populates="word_forms")
    pronunciations = db.relationship("Pronunciation", back_populates="word_form",
                                     cascade="all, delete-orphan")
    idiom_words    = db.relationship("IdiomWord", back_populates="word_form")

    def __repr__(self):
        return (f"<WordForm {self.written_form!r} "
                f"lexeme={self.lexeme_id} dialect={self.dialect_id}>")


# ===========================================================================
# Senses
# ===========================================================================

class Sense(db.Model):
    """One meaning of a lexeme. A lexeme may have many senses."""
    __tablename__ = "senses"

    id        = db.Column(db.Integer, primary_key=True)
    lexeme_id = db.Column(db.Integer,
                          db.ForeignKey("lexemes.id", ondelete="CASCADE"),
                          nullable=False)

    definition = db.Column(db.Text, nullable=False)
    notes      = db.Column(db.Text)

    lexeme          = db.relationship("Lexeme", back_populates="senses")
    semantic_fields = db.relationship("SemanticField",
                                      secondary="sense_semantic_fields",
                                      back_populates="senses")

    def __repr__(self):
        preview = (self.definition or "")[:50]
        return f"<Sense lexeme={self.lexeme_id} {preview!r}>"


# Junction: senses <-> semantic_fields
sense_semantic_fields = db.Table(
    "sense_semantic_fields",
    db.Column("sense_id", db.Integer,
              db.ForeignKey("senses.id", ondelete="CASCADE"),
              primary_key=True),
    db.Column("semantic_field_id", db.Integer,
              db.ForeignKey("semantic_fields.id", ondelete="CASCADE"),
              primary_key=True),
)


# ===========================================================================
# Pronunciations  (attached to word_forms)
# ===========================================================================

class Pronunciation(db.Model):
    """
    IPA record for a specific word form.
    Dialect context is inherited from word_form.dialect_id — no separate
    dialect_id needed here.
    """
    __tablename__ = "pronunciations"

    id           = db.Column(db.Integer, primary_key=True)
    word_form_id = db.Column(db.Integer,
                             db.ForeignKey("word_forms.id", ondelete="CASCADE"),
                             nullable=False)

    ipa   = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)

    word_form = db.relationship("WordForm", back_populates="pronunciations")

    def __repr__(self):
        return f"<Pronunciation word_form={self.word_form_id} /{self.ipa}/>"


# ===========================================================================
# Idioms + IdiomWords
# ===========================================================================

class Idiom(db.Model):
    """
    A multi-word expression whose meaning is not compositional.
    Must be matched BEFORE word-by-word translation.
    dialect_id = NULL means valid in all dialects of the language.
    """
    __tablename__ = "idioms"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    dialect_id  = db.Column(db.Integer,
                            db.ForeignKey("dialects.id", ondelete="SET NULL"),
                            nullable=True)

    phrase  = db.Column(db.String(512), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    notes   = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language    = db.relationship("Language", back_populates="idioms")
    dialect     = db.relationship("Dialect",  back_populates="idioms")
    idiom_words = db.relationship("IdiomWord", back_populates="idiom",
                                  cascade="all, delete-orphan",
                                  order_by="IdiomWord.id")

    __table_args__ = (
        db.Index("ix_idioms_language_phrase", "language_id", "phrase"),
    )

    def __repr__(self):
        return f"<Idiom {self.phrase!r} lang={self.language_id}>"


class IdiomWord(db.Model):
    """
    Junction: which word forms make up an idiom.
    References word_forms (not lexemes) — idioms are fixed at surface-form level.
    word_form_id is nullable for particles not yet in the lexicon.
    """
    __tablename__ = "idiom_words"

    id           = db.Column(db.Integer, primary_key=True)
    idiom_id     = db.Column(db.Integer,
                             db.ForeignKey("idioms.id", ondelete="CASCADE"),
                             nullable=False)
    word_form_id = db.Column(db.Integer,
                             db.ForeignKey("word_forms.id", ondelete="SET NULL"),
                             nullable=True)

    idiom     = db.relationship("Idiom", back_populates="idiom_words")
    word_form = db.relationship("WordForm", back_populates="idiom_words")

    def __repr__(self):
        return f"<IdiomWord idiom={self.idiom_id} word_form={self.word_form_id}>"


# ===========================================================================
# Grammar rules  (scoped to dialect)
# ===========================================================================

class GrammarRule(db.Model):
    """
    A named grammatical rule owned by a dialect.
    For language-wide rules, attach to the root/standard dialect.
    """
    __tablename__ = "grammar_rules"

    id         = db.Column(db.Integer, primary_key=True)
    dialect_id = db.Column(db.Integer,
                           db.ForeignKey("dialects.id", ondelete="CASCADE"),
                           nullable=False)

    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    dialect = db.relationship("Dialect", back_populates="grammar_rules")

    def __repr__(self):
        return f"<GrammarRule {self.name!r} dialect={self.dialect_id}>"


# ===========================================================================
# Phonology rules  (scoped to dialect)
# ===========================================================================

class PhonologyRule(db.Model):
    """
    A phonological rule owned by a dialect.
    Phonology is always dialect-specific — no nullable dialect_id here.
    """
    __tablename__ = "phonology_rules"

    id         = db.Column(db.Integer, primary_key=True)
    dialect_id = db.Column(db.Integer,
                           db.ForeignKey("dialects.id", ondelete="CASCADE"),
                           nullable=False)

    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    dialect = db.relationship("Dialect", back_populates="phonology_rules")

    def __repr__(self):
        return f"<PhonologyRule {self.name!r} dialect={self.dialect_id}>"


# ===========================================================================
# Translation memory
# ===========================================================================

class TranslationMemory(db.Model):
    """
    Stored sentence pairs for validating and improving the rule-based translator.
    status:     draft -> approved (confirmed correct) or rejected (known wrong).
    confidence: 0.0-1.0, set by translator engine; NULL for manual entries.
    """
    __tablename__ = "translation_memories"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    dialect_id  = db.Column(db.Integer,
                            db.ForeignKey("dialects.id", ondelete="CASCADE"),
                            nullable=True)

    source_text = db.Column(db.Text, nullable=False)
    target_text = db.Column(db.Text, nullable=False)

    source     = db.Column(db.Enum(TranslationSource), nullable=False,
                           default=TranslationSource.manual)
    status     = db.Column(db.Enum(TranslationStatus), nullable=False,
                           default=TranslationStatus.draft)
    confidence = db.Column(db.Float)

    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language",
                               foreign_keys=[language_id],
                               back_populates="translation_memories")
    dialect  = db.relationship("Dialect",
                               back_populates="translation_memories")

    __table_args__ = (
        db.Index("ix_tm_language_status", "language_id", "status"),
        db.Index("ix_tm_dialect_status",  "dialect_id",  "status"),
    )

    def __repr__(self):
        preview = (self.source_text or "")[:30]
        return (f"<TranslationMemory [{self.status.value}] "
                f"lang={self.language_id} {preview!r}>")


# ===========================================================================
# Etymology articles
# ===========================================================================

class EtymologyArticle(db.Model):
    """
    Long-form Markdown article documenting origin and evolution.
    export.py renders content via the etymology_article.html Jinja2 template
    and saves the result to exports/ as a self-contained .html file.
    """
    __tablename__ = "etymology_articles"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)

    title        = db.Column(db.String(255), nullable=False)
    article_type = db.Column(db.Enum(ArticleType), nullable=False,
                             default=ArticleType.history)
    content      = db.Column(db.Text, nullable=False)  # Markdown body

    last_exported_at  = db.Column(db.DateTime)
    exported_filename = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="etymology_articles")

    def __repr__(self):
        return f"<EtymologyArticle {self.title!r} lang={self.language_id}>"


# ===========================================================================
# Etymology events  (timeline)
# ===========================================================================

class EtymologyEvent(db.Model):
    """
    One entry in the chronological timeline of a language or dialect.
    Scoped directly to a language (not a child of an article).

    era_sort_key — integer for chronological ordering; negative = pre-history.
    dialect_id   — NULL means the event applies to the whole language.
    """
    __tablename__ = "etymology_events"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    dialect_id  = db.Column(db.Integer,
                            db.ForeignKey("dialects.id", ondelete="SET NULL"),
                            nullable=True)

    event_type   = db.Column(db.Enum(EventType), nullable=False)
    era_label    = db.Column(db.String(120), nullable=False)
    era_sort_key = db.Column(db.Integer, nullable=False, default=0)

    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="etymology_events")
    dialect  = db.relationship("Dialect",  back_populates="etymology_events")

    __table_args__ = (
        db.Index("ix_etymology_events_lang_sort", "language_id", "era_sort_key"),
    )

    def __repr__(self):
        return (f"<EtymologyEvent [{self.event_type.value}] "
                f"{self.era_label!r} {self.title!r}>")


# ===========================================================================
# Sample texts
# ===========================================================================

class SampleText(db.Model):
    """
    A canonical passage demonstrating the language.

    Doubles as a translator regression test when is_regression_test = True:
    run the translator on any source text, compare output to content, flag drift.
    """
    __tablename__ = "sample_texts"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.id", ondelete="CASCADE"),
                            nullable=False)
    dialect_id  = db.Column(db.Integer,
                            db.ForeignKey("dialects.id", ondelete="CASCADE"),
                            nullable=False)

    title   = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

    is_regression_test = db.Column(db.Boolean, nullable=False, default=False)
    notes              = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship("Language", back_populates="sample_texts")
    dialect  = db.relationship("Dialect",  back_populates="sample_texts")

    def __repr__(self):
        return (f"<SampleText {self.title!r} "
                f"dialect={self.dialect_id} regression={self.is_regression_test}>")