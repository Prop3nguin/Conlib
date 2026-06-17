"""
models.py — Full schema: Phases 1–6
Phase 1: languages, language_relationships, dialects, scripts, glyphs
Phase 2: words, morphemes, senses, sense_fields, semantic_fields,
         pronunciations, inflection_paradigms, word_paradigms, inflected_forms
Phase 3: grammar_rules, phonology_rules
Phase 4: idioms, idiom_words, translation_memory
Phase 5: translator engine — no DB changes (see app/translator/)
Phase 6: etymology_articles, etymology_events, sample_texts

after editing run:
    flask db migrate -m "Description of your model changes"
    flask db upgrade

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
    root      = "root"
    prefix    = "prefix"
    suffix    = "suffix"
    infix     = "infix"
    circumfix = "circumfix"
    clitic    = "clitic"


# --- Phase 3 ----------------------------------------------------------------

class GrammarRuleType(enum.Enum):
    morphology   = "morphology"
    syntax       = "syntax"
    phonology    = "phonology"
    cv_structure = "cv_structure"


class PhonologyRuleType(enum.Enum):
    assimilation  = "assimilation"
    dissimilation = "dissimilation"
    elision       = "elision"
    insertion     = "insertion"
    sandhi        = "sandhi"
    metathesis    = "metathesis"
    tone          = "tone"
    other         = "other"


class RuleScope(enum.Enum):
    word_internal     = "word_internal"
    morpheme_boundary = "morpheme_boundary"
    word_boundary     = "word_boundary"
    phrase            = "phrase"
    clause            = "clause"


# --- Phase 4 ----------------------------------------------------------------

class IdiomType(enum.Enum):
    """
    idiom        — fixed phrase with non-compositional meaning
                   e.g. "kick the bucket" ≠ kick + bucket
    collocation  — words that strongly prefer each other's company
                   e.g. "make a decision" (not "do a decision")
    proverb      — culturally-transmitted saying with moral/practical meaning
    greeting     — conventional opener/closer (often opaque to non-speakers)
    """
    idiom       = "idiom"
    collocation = "collocation"
    proverb     = "proverb"
    greeting    = "greeting"
    other       = "other"


class TranslationSource(enum.Enum):
    """
    How did this translation memory entry get here?

    manual      — hand-entered by the conlang author; highest trust
    translator  — produced by the rule-based translator engine
    imported    — bulk-imported from an external source
    """
    manual     = "manual"
    translator = "translator"
    imported   = "imported"


class TranslationStatus(enum.Enum):
    """
    Validation status of a translation memory entry.

    approved  — confirmed correct by the author; safe to use for regression
    draft     — plausible but not yet verified
    rejected  — known to be wrong; kept for audit trail, never matched
    """
    approved = "approved"
    draft    = "draft"
    rejected = "rejected"


# --- Phase 6 ----------------------------------------------------------------

class ArticleType(enum.Enum):
    """
    What kind of etymology article is this?

    history      — origin and history of the language itself
    dialect      — evolution and divergence of a specific dialect
    vocabulary   — how a semantic domain or word class developed
    loanwords    — borrowing from another language, with era and direction
    cultural     — how beliefs, events, or social structures shaped the lexicon
    """
    history   = "history"
    dialect   = "dialect"
    vocabulary = "vocabulary"
    loanwords = "loanwords"
    cultural  = "cultural"
    other     = "other"


class EventType(enum.Enum):
    """
    What kind of historical event does this timeline entry record?

    sound_change   — a phonological shift (links to a PhonologyRule)
    grammar_change — a grammatical restructuring (links to a GrammarRule)
    dialect_split  — a dialect diverges from its parent
    contact_event  — contact with another language causes borrowing/shift
    cultural_event — a social or cultural shift that affected the language
    lexical_event  — a word enters, leaves, or changes meaning
    """
    sound_change   = "sound_change"
    grammar_change = "grammar_change"
    dialect_split  = "dialect_split"
    contact_event  = "contact_event"
    cultural_event = "cultural_event"
    lexical_event  = "lexical_event"
    other          = "other"


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

    # Phase 1
    default_dialect_id = db.Column(
        db.Integer,
        db.ForeignKey("dialects.id"),
        nullable=True
    )

    default_dialect = db.relationship(
        "Dialect",
        foreign_keys=[default_dialect_id]
    )

    dialects = db.relationship(
        "Dialect", 
        foreign_keys="Dialect.language_id",
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
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

    # Phase 2
    words                = db.relationship(
        "Word", 
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
    morphemes            = db.relationship(
        "Morpheme", 
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
    inflection_paradigms = db.relationship(
        "InflectionParadigm",
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
    # Phase 3

    grammar_rules = db.relationship(
        "GrammarRule", 
        back_populates="language",
        cascade="all, delete-orphan",
        order_by="GrammarRule.rule_order"
        )
    
    # Phase 4

    idioms             = db.relationship(
        "Idiom", 
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
    translation_memory = db.relationship(
        "TranslationMemory",
        foreign_keys="[TranslationMemory.language_id]",
        back_populates="language",
        cascade="all, delete-orphan"
        )
    
    # Phase 6

    etymology_articles = db.relationship(
        "EtymologyArticle",
        back_populates="language", 
        cascade="all, delete-orphan"
        )
    
    sample_texts       = db.relationship(
        "SampleText",
        back_populates="language",
        cascade="all, delete-orphan"
        )

    def __repr__(self):
        return f"<Language {self.name!r} ({self.status.value})>"


class LanguageRelationship(db.Model):
    """
    Directed edge between two languages.
      borrowing:        source borrowed FROM target
      common_ancestor:  both share a proto-language
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

    source_language = db.relationship(
        "Language", 
        foreign_keys=[source_language_id],
        back_populates="relationships_as_source"
        )
    
    target_language = db.relationship(
        "Language", 
        foreign_keys=[target_language_id],
        back_populates="relationships_as_target"
        )

    __table_args__ = (
        db.UniqueConstraint(
            "source_language_id", 
            "target_language_id",
            "relationship_type", 
            name="uq_lang_rel"
        ),
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

    # Phase 1

    language = db.relationship(
        "Language", 
        foreign_keys=[language_id],
        back_populates="dialects"
        )
    
    parent   = db.relationship(
        "Dialect", 
        remote_side="Dialect.id",
        back_populates="children"
        )
    
    children = db.relationship(
        "Dialect", back_populates="parent",
        cascade="all, delete-orphan"
        )
    
    scripts  = db.relationship(
        "Script", back_populates="dialect",
        cascade="all, delete-orphan"
        )
    
    # Phase 2
    words           = db.relationship(
        "Word", 
        back_populates="dialect"
        )
    
    pronunciations  = db.relationship(
        "Pronunciation", 
        back_populates="dialect",
        cascade="all, delete-orphan"
        )
    
    inflected_forms = db.relationship(
        "InflectedForm", 
        back_populates="dialect"
        )
    
    # Phase 3
    grammar_rules   = db.relationship(
        "GrammarRule", 
        back_populates="dialect"
        )
    
    phonology_rules = db.relationship(
        "PhonologyRule", 
        back_populates="dialect",
        cascade="all, delete-orphan",
        order_by="PhonologyRule.rule_order"
        )
    
    # Phase 4
    idioms             = db.relationship(
        "Idiom",
        back_populates="dialect"
        )
    
    translation_memory = db.relationship(
        "TranslationMemory",
        back_populates="dialect",
        cascade="all, delete-orphan"
        )
    
    # Phase 6
    etymology_events = db.relationship(
        "EtymologyEvent",
        back_populates="dialect"
        )
    
    sample_texts     = db.relationship(
        "SampleText",
        back_populates="dialect"
        )

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
    created_at         = db.Column(db.DateTime,
                                   default=lambda: datetime.now(timezone.utc))

    dialect = db.relationship(
        "Dialect", 
        back_populates="scripts"
        )
    
    glyphs  = db.relationship(
        "Glyph", 
        back_populates="script",
        cascade="all, delete-orphan",
        order_by="Glyph.glyph_order"
        )

    def __repr__(self):
        return f"<Script {self.name!r} ({self.script_type.value})>"


class Glyph(db.Model):
    """
    One atomic character in a script.
    script_code is the stable app-internal identifier — a soft FK referenced
    by words and inflected_forms (not DB-enforced).
    """
    __tablename__ = "glyphs"

    id                = db.Column(db.Integer, primary_key=True)
    script_id         = db.Column(db.Integer, db.ForeignKey("scripts.id",
                                  ondelete="CASCADE"), nullable=False)
    script_code       = db.Column(db.String(40), nullable=False)
    unicode_codepoint = db.Column(db.String(10))
    category          = db.Column(db.Enum(GlyphCategory),
                                  default=GlyphCategory.letter)
    romanization      = db.Column(db.String(40))
    ipa_value         = db.Column(db.String(40))
    name              = db.Column(db.String(120))
    description       = db.Column(db.Text)
    glyph_order       = db.Column(db.Integer, default=0)
    contextual_notes  = db.Column(db.Text)

    script = db.relationship(
        "Script", 
        back_populates="glyphs"
        )

    __table_args__ = (
        db.UniqueConstraint("script_id", "script_code", name="uq_glyph_code"),
    )

    def __repr__(self):
        return (f"<Glyph {self.script_code!r} "
                f"rom={self.romanization!r} ipa={self.ipa_value!r}>")


# ===========================================================================
# Phase 2 — Core Lexicon
# ===========================================================================

class Word(db.Model):
    """
    A lexical entry at the language level.
    dialect_id = NULL → shared across all dialects.
    script_code → soft FK into glyphs.script_code, validated at route level.
    """
    __tablename__ = "words"

    id           = db.Column(db.Integer, primary_key=True)
    language_id  = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id   = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    lemma        = db.Column(db.String(255), nullable=False)
    romanization = db.Column(db.String(255))
    script_code  = db.Column(db.String(40))

    pos          = db.Column(db.Enum(PartOfSpeech), nullable=False)
    pos_subtype  = db.Column(db.String(80))
    register     = db.Column(db.Enum(Register), nullable=False,
                            default=Register.neutral)

    notes        = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language        = db.relationship(
        "Language", 
        back_populates="words"
        )
    
    dialect         = db.relationship(
        "Dialect",  
        back_populates="words"
        )

    senses          = db.relationship(
        "Sense", 
        back_populates="word",
        cascade="all, delete-orphan",
        order_by="Sense.sense_order"
        )
    
    pronunciations  = db.relationship(
        "Pronunciation", 
        back_populates="word",
        cascade="all, delete-orphan"
        )
    
    inflected_forms = db.relationship(
        "InflectedForm", 
        back_populates="word",
        cascade="all, delete-orphan"
        )
    
    word_paradigms  = db.relationship(
        "WordParadigm", 
        back_populates="word",
        cascade="all, delete-orphan"
        )
    
    # Phase 4 — word may appear in idioms via IdiomWord junction
    idiom_words     = db.relationship(
        "IdiomWord", 
        back_populates="word"
        )

    def __repr__(self):
        return f"<Word {self.lemma!r} ({self.pos.value})>"


class Morpheme(db.Model):
    """
    First-class morpheme entry — roots, affixes, clitics.
    form        — canonical shape, e.g. "-ek", "vel-"
    gloss       — Leipzig label, e.g. "PL", "PAST", "CAUS"
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

    language = db.relationship(
        "Language", 
        back_populates="morphemes"
        )

    def __repr__(self):
        return (f"<Morpheme {self.form!r} "
                f"[{self.morpheme_type.value}] gloss={self.gloss!r}>")


# Junction: senses ↔ semantic_fields
sense_fields = db.Table(
    "sense_fields",
    db.Column("sense_id", db.Integer,
              db.ForeignKey("senses.id", ondelete="CASCADE"), primary_key=True),
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
    example_sentence    = db.Column(db.Text)
    example_translation = db.Column(db.Text)
    notes               = db.Column(db.Text)

    word            = db.relationship(
        "Word", 
        back_populates="senses"
        )
    
    semantic_fields = db.relationship(
        "SemanticField",
        secondary="sense_fields",
        back_populates="senses"
        )

    def __repr__(self):
        preview = (self.definition or "")[:40]
        return f"<Sense word={self.word_id} order={self.sense_order} {preview!r}>"


class SemanticField(db.Model):
    __tablename__ = "semantic_fields"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False, unique=True)
    parent_field_id = db.Column(db.Integer,
                                db.ForeignKey("semantic_fields.id",
                                              ondelete="SET NULL"), nullable=True)
    description     = db.Column(db.Text)

    parent   = db.relationship(
        "SemanticField", 
        remote_side="SemanticField.id",
        back_populates="children"
        )
    
    children = db.relationship(
        "SemanticField", 
        back_populates="parent"
        )
    
    senses   = db.relationship(
        "Sense", 
        secondary="sense_fields",
        back_populates="semantic_fields"
        )

    def __repr__(self):
        return f"<SemanticField {self.name!r}>"


class Pronunciation(db.Model):
    """One IPA record per word per dialect."""
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

    word    = db.relationship(
        "Word",    
        back_populates="pronunciations"
        )
    
    dialect = db.relationship(
        "Dialect", 
        back_populates="pronunciations"
        )

    __table_args__ = (
        db.UniqueConstraint("word_id", "dialect_id", name="uq_pronunciation"),
    )

    def __repr__(self):
        return (f"<Pronunciation word={self.word_id} "
                f"dialect={self.dialect_id} /{self.ipa}/>")


class InflectionParadigm(db.Model):
    """Named inflection template, e.g. 'Class I Verb', 'Animate Noun'."""
    __tablename__ = "inflection_paradigms"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)

    name        = db.Column(db.String(120), nullable=False)
    pos         = db.Column(db.Enum(PartOfSpeech))
    description = db.Column(db.Text)

    language        = db.relationship(
        "Language",
        back_populates="inflection_paradigms"
        )
    
    word_paradigms  = db.relationship(
        "WordParadigm", 
        back_populates="paradigm",
        cascade="all, delete-orphan"
        )
    
    inflected_forms = db.relationship(
        "InflectedForm",
        back_populates="paradigm",
        cascade="all, delete-orphan"
        )

    def __repr__(self):
        return f"<InflectionParadigm {self.name!r}>"


class WordParadigm(db.Model):
    """Junction: which paradigm(s) a word follows."""
    __tablename__ = "word_paradigms"

    word_id     = db.Column(db.Integer, db.ForeignKey("words.id",
                            ondelete="CASCADE"), primary_key=True)
    paradigm_id = db.Column(db.Integer, db.ForeignKey("inflection_paradigms.id",
                            ondelete="CASCADE"), primary_key=True)

    word     = db.relationship(
        "Word",               
        back_populates="word_paradigms"
        )
    
    paradigm = db.relationship(
        "InflectionParadigm", 
        back_populates="word_paradigms"
        )


class InflectedForm(db.Model):
    """
    One realised form per word per paradigm slot.
    form_label  — slot name e.g. "1SG.PRES", "NOM.PL"
    dialect_id  — NULL = applies to all dialects
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

    word     = db.relationship(
        "Word",               
        back_populates="inflected_forms"
        )
    
    paradigm = db.relationship(
        "InflectionParadigm", 
        back_populates="inflected_forms"
        )
    
    dialect  = db.relationship(
        "Dialect",            
        back_populates="inflected_forms"
        )

    __table_args__ = (
        db.UniqueConstraint("word_id", "paradigm_id", "form_label", "dialect_id",
                            name="uq_inflected_form"),
    )

    def __repr__(self):
        return (f"<InflectedForm {self.form_label}={self.form!r} "
                f"word={self.word_id}>")


# ===========================================================================
# Phase 3 — Grammar & Phonology Rules
# ===========================================================================

class GrammarRule(db.Model):
    """
    A named grammatical rule scoped to a language, optionally a dialect.

    rule_order  — translator applies ascending order within each rule_type
    dialect_id  — NULL = applies to all dialects
    is_active   — flip False to disable without deleting (translator testing)

    pattern / result format by rule_type:
      morphology:   structural description → output template
      syntax:       default constituent order → exceptions
      phonology:    broad notes only (use PhonologyRule for IPA-precise rules)
      cv_structure: CV template ("CVC") → restriction notes
    """
    __tablename__ = "grammar_rules"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    name       = db.Column(db.String(200), nullable=False)
    rule_type  = db.Column(db.Enum(GrammarRuleType), nullable=False)
    rule_order = db.Column(db.Integer, nullable=False, default=100)

    pattern    = db.Column(db.Text)
    result     = db.Column(db.Text)
    example    = db.Column(db.Text)
    notes      = db.Column(db.Text)
    is_active  = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship(
        "Language", 
        back_populates="grammar_rules"
        )
    dialect  = db.relationship(
        "Dialect",  
        back_populates="grammar_rules"
        )

    __table_args__ = (
        db.Index("ix_grammar_rules_lang_type_order",
                 "language_id", "rule_type", "rule_order"),
    )

    def __repr__(self):
        return (f"<GrammarRule [{self.rule_type.value}] "
                f"order={self.rule_order} {self.name!r}>")


class PhonologyRule(db.Model):
    """
    An IPA-precise phonological rule, always scoped to a dialect.

    input_ipa   — sound/class being changed, e.g. "k", "[+velar]", "V"
    output_ipa  — result; empty string = deletion/elision
    environment — standard phonological context notation, e.g.:
                  "_ [+front vowel]"  (before a front vowel)
                  "C _"               (after any consonant)
                  "# _"               (word-initial)
                  "_ #"               (word-final)
                  NULL = no environment restriction

    is_feeding / is_bleeding — documentation aids; translator uses rule_order only
    """
    __tablename__ = "phonology_rules"

    id         = db.Column(db.Integer, primary_key=True)
    dialect_id = db.Column(db.Integer, db.ForeignKey("dialects.id",
                           ondelete="CASCADE"), nullable=False)

    name       = db.Column(db.String(200), nullable=False)
    rule_type  = db.Column(db.Enum(PhonologyRuleType), nullable=False)
    rule_order = db.Column(db.Integer, nullable=False, default=100)

    input_ipa       = db.Column(db.String(120), nullable=False)
    output_ipa      = db.Column(db.String(120), nullable=False, default="")
    environment     = db.Column(db.String(255))
    formal_notation = db.Column(db.Text)

    scope       = db.Column(db.Enum(RuleScope), default=RuleScope.word_internal)
    is_feeding  = db.Column(db.Boolean, default=False)
    is_bleeding = db.Column(db.Boolean, default=False)

    example    = db.Column(db.Text)
    notes      = db.Column(db.Text)
    is_active  = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    dialect = db.relationship(
        "Dialect", 
        back_populates="phonology_rules"
        )

    __table_args__ = (
        db.Index("ix_phonology_rules_dialect_order", "dialect_id", "rule_order"),
    )

    def __repr__(self):
        env = f" / {self.environment}" if self.environment else ""
        return (f"<PhonologyRule [{self.rule_type.value}] "
                f"order={self.rule_order} {self.input_ipa!r} → "
                f"{self.output_ipa!r}{env}>")


# ===========================================================================
# Phase 4 — Idioms, Collocations & Translation Memory
# ===========================================================================

class Idiom(db.Model):
    """
    A multi-word expression whose meaning is not compositional.

    These must be looked up BEFORE the translator attempts word-by-word
    processing — the idiom match wins and the component words are not
    translated individually.

    Surface forms
    -------------
    phrase           — the canonical romanized surface form used for matching,
                       e.g. "vel etek mora"
    phrase_script    — the same phrase in script codes (soft FK into glyphs),
                       space-separated, e.g. "V-03 K-07 M-02"

    Both fields are indexed for fast substring search.

    Dialect scoping
    ---------------
    dialect_id = NULL → the idiom is valid in all dialects of the language.
    Set dialect_id to restrict to one dialect's usage.

    Variability
    -----------
    is_fixed = True  → the phrase must appear verbatim (no inflection of parts)
    is_fixed = False → individual components may inflect; the IdiomWord
                       component_role column records which slots are flexible
    """
    __tablename__ = "idioms"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    phrase        = db.Column(db.String(512), nullable=False)
                              # romanized, used for translator matching
    phrase_script = db.Column(db.String(512))
                              # space-separated script codes

    idiom_type  = db.Column(db.Enum(IdiomType), nullable=False,
                            default=IdiomType.idiom)
    register    = db.Column(db.Enum(Register), nullable=False,
                            default=Register.neutral)

    meaning     = db.Column(db.Text, nullable=False)
                              # English gloss of the whole expression
    literal     = db.Column(db.Text)
                              # word-by-word literal meaning for reference
    example     = db.Column(db.Text)
                              # usage example in the conlang
    example_translation = db.Column(db.Text)
                              # English translation of the example

    is_fixed    = db.Column(db.Boolean, nullable=False, default=True)
                              # True = verbatim match only
    notes       = db.Column(db.Text)

    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    language    = db.relationship(
        "Language", 
        back_populates="idioms"
        )
    
    dialect     = db.relationship(
        "Dialect",  
        back_populates="idioms"
        )
    
    idiom_words = db.relationship(
        "IdiomWord", 
        back_populates="idiom",
        cascade="all, delete-orphan",
        order_by="IdiomWord.position"
        )

    __table_args__ = (
        db.Index("ix_idioms_phrase", "language_id", "phrase"),
    )

    def __repr__(self):
        return (f"<Idiom {self.phrase!r} "
                f"[{self.idiom_type.value}] lang={self.language_id}>")


class IdiomWord(db.Model):
    """
    Junction: which words make up an idiom, and in what order.

    position       — 0-based index of this word in the phrase
    component_role — free-text slot label for inflectable components
                     e.g. "subject", "verb", "object"
                     NULL for fixed/non-inflecting positions
    inflected_form_id — optional FK to a specific InflectedForm if this slot
                        always uses a particular inflected form (e.g. the verb
                        is always in the imperative)
    word_id        — NULL is allowed: the slot is a function word or particle
                     that exists in the phrase but has no lexicon entry yet
    """
    __tablename__ = "idiom_words"

    id        = db.Column(db.Integer, primary_key=True)
    idiom_id  = db.Column(db.Integer, db.ForeignKey("idioms.id",
                          ondelete="CASCADE"), nullable=False)
    word_id   = db.Column(db.Integer, db.ForeignKey("words.id",
                          ondelete="SET NULL"), nullable=True)

    position          = db.Column(db.Integer, nullable=False)
    component_role    = db.Column(db.String(80))
    inflected_form_id = db.Column(db.Integer,
                                  db.ForeignKey("inflected_forms.id",
                                                ondelete="SET NULL"),
                                  nullable=True)
    surface_form      = db.Column(db.String(255))
                                  # literal token as it appears in the phrase,
                                  # useful when word_id is NULL or inflected

    idiom          = db.relationship(
        "Idiom", 
        back_populates="idiom_words"
        )
    
    word           = db.relationship(
        "Word",  
        back_populates="idiom_words"
        )
    
    inflected_form = db.relationship(
        "InflectedForm"
        )

    __table_args__ = (
        db.UniqueConstraint("idiom_id", "position", name="uq_idiom_position"),
    )

    def __repr__(self):
        return (f"<IdiomWord idiom={self.idiom_id} "
                f"pos={self.position} word={self.word_id}>")


class TranslationMemory(db.Model):
    """
    Stored sentence pairs used to validate and improve the rule-based
    translator over time.

    Scoping
    -------
    language_id  — the conlang this entry belongs to (always required)
    dialect_id   — the specific dialect; NULL = applies to all dialects

    Source / target convention
    --------------------------
    source_text       — text in the SOURCE language (typically English or
                        whatever natural language the author is working from)
    source_language_id — FK to a Language row if the source is another
                         conlang in this app; NULL for natural languages
                         (store the natural language name in source_lang_name)
    source_lang_name  — free-text name of the source language when it is a
                        natural language not tracked in this app, e.g. "English"
    target_text       — text in the conlang (romanized)
    target_script     — target_text in script codes (optional)

    Validation workflow
    -------------------
    status: draft → approved (author confirms) or rejected (known wrong).
    Rejected entries are kept for audit — they document failure cases useful
    for debugging the translator.

    confidence        — float 0.0–1.0, auto-set by the translator engine when
                        source = 'translator'.  NULL for manual entries.
    """
    __tablename__ = "translation_memory"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="CASCADE"), nullable=True)

    # Source side
    source_text        = db.Column(db.Text, nullable=False)
    source_language_id = db.Column(db.Integer,
                                   db.ForeignKey("languages.id",
                                                 ondelete="SET NULL"),
                                   nullable=True)
                                   # FK if source is another tracked conlang
    source_lang_name   = db.Column(db.String(120))
                                   # free-text if source is a natural language

    # Target side
    target_text   = db.Column(db.Text, nullable=False)
                               # romanized conlang text
    target_script = db.Column(db.Text)
                               # same text in script codes (optional)

    # Provenance & quality
    source     = db.Column(db.Enum(TranslationSource), nullable=False,
                           default=TranslationSource.manual)
    status     = db.Column(db.Enum(TranslationStatus), nullable=False,
                           default=TranslationStatus.draft)
    confidence = db.Column(db.Float)
                           # 0.0–1.0; set by translator engine, NULL for manual

    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language        = db.relationship(
        "Language",
        foreign_keys=[language_id],
        back_populates="translation_memory"
        )
    
    source_language = db.relationship(
        "Language",
        foreign_keys=[source_language_id]
        )
    
    dialect         = db.relationship(
        "Dialect",
        back_populates="translation_memory"
        )

    __table_args__ = (
        db.Index("ix_tm_language_status", "language_id", "status"),
        db.Index("ix_tm_dialect_status",  "dialect_id",  "status"),
    )

    def __repr__(self):
        preview = (self.source_text or "")[:30]
        return (f"<TranslationMemory [{self.status.value}] "
                f"lang={self.language_id} {preview!r}>")

# ===========================================================================
# Phase 6 — Etymology Articles, Timeline Events & Sample Texts
# ===========================================================================

class EtymologyArticle(db.Model):
    """
    A long-form article documenting the origin and evolution of the language
    or one of its aspects.

    body_md stores the article body as Markdown. export.py renders this via
    the etymology_article.html Jinja2 template and saves the result to
    exports/ as a self-contained .html file.

    References to specific words, dialects, or other DB objects should be
    embedded in the Markdown as inline IDs and resolved at render time by
    the template, e.g. {{word:42}} or {{dialect:3}}.

    dialect_id is nullable — set it when the article is specifically about
    one dialect rather than the language as a whole.
    """
    __tablename__ = "etymology_articles"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="SET NULL"), nullable=True)

    title        = db.Column(db.String(255), nullable=False)
    article_type = db.Column(db.Enum(ArticleType), nullable=False,
                             default=ArticleType.history)
    summary      = db.Column(db.Text)   # short abstract shown in article lists
    body_md      = db.Column(db.Text, nullable=False)
                             # full article body in Markdown

    # Export tracking — set when export.py renders the article to exports/
    last_exported_at  = db.Column(db.DateTime)
    exported_filename = db.Column(db.String(255))
                             # e.g. "vethian_origins_2024.html"

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship(
        "Language", 
        back_populates="etymology_articles"
        )
    
    dialect  = db.relationship(
        "Dialect",  
        foreign_keys=[dialect_id]
        )
    
    events   = db.relationship(
        "EtymologyEvent",
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="EtymologyEvent.era_sort_key"
        )

    def __repr__(self):
        return f"<EtymologyArticle {self.title!r} (lang={self.language_id})>"


class EtymologyEvent(db.Model):
    """
    A single entry in the chronological timeline of a language or dialect.

    Timeline entries anchor historical translation rules — the translator
    can use era_sort_key to select the appropriate phonology and grammar
    rules for a given historical period.

    Linking to rules
    ----------------
    phonology_rule_id and grammar_rule_id are optional FKs. Set them when
    this event directly corresponds to a rule already in the DB, so the
    UI can cross-link between the timeline and the rule editor.

    era_label    — human-readable period name, e.g. "Early Classical Period"
    era_sort_key — integer for chronological ordering (can be a year, decade,
                   or any consistent ordinal — negative values for pre-history)

    dialect_id   — NULL = event applies to the whole language; set to scope
                   it to a dialect divergence or dialect-specific change.
    """
    __tablename__ = "etymology_events"

    id         = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("etymology_articles.id",
                           ondelete="CASCADE"), nullable=False)
    dialect_id = db.Column(db.Integer, db.ForeignKey("dialects.id",
                           ondelete="SET NULL"), nullable=True)

    event_type   = db.Column(db.Enum(EventType), nullable=False)
    era_label    = db.Column(db.String(120), nullable=False)
                             # e.g. "Early Classical Period", "~300 BP"
    era_sort_key = db.Column(db.Integer, nullable=False, default=0)
                             # chronological sort order; negative = pre-history

    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    example     = db.Column(db.Text)   # illustrative form change or example

    # Optional cross-links to rules already in the DB
    phonology_rule_id = db.Column(db.Integer,
                                  db.ForeignKey("phonology_rules.id",
                                                ondelete="SET NULL"),
                                  nullable=True)
    grammar_rule_id   = db.Column(db.Integer,
                                  db.ForeignKey("grammar_rules.id",
                                                ondelete="SET NULL"),
                                  nullable=True)

    # Optional cross-link to a word whose etymology this event explains
    word_id = db.Column(db.Integer, db.ForeignKey("words.id",
                        ondelete="SET NULL"), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    article        = db.relationship(
        "EtymologyArticle", 
        back_populates="events"
        )
    
    dialect        = db.relationship(
        "Dialect", 
        back_populates="etymology_events"
        )
    
    phonology_rule = db.relationship(
        "PhonologyRule"
        )
    
    grammar_rule   = db.relationship(
        "GrammarRule"
        )
    
    word           = db.relationship(
        "Word"
        )

    __table_args__ = (
        db.Index("ix_etymology_events_article_sort",
                 "article_id", "era_sort_key"),
    )

    def __repr__(self):
        return (f"<EtymologyEvent [{self.event_type.value}] "
                f"{self.era_label!r} {self.title!r}>")


class SampleText(db.Model):
    """
    A canonical passage used to demonstrate the language, test font rendering,
    and anchor the translator as a Rosetta Stone.

    All four representations are stored in parallel:
      source_text   — the original passage (in English or another source language)
      script_text   — the conlang rendered in script codes (→ custom font)
      romanization  — romanized conlang text
      ipa           — IPA transcription (dialect-aware)
      translation   — English gloss / translation

    dialect_id is required — sample texts are always dialect-specific because
    phonology and script may differ across dialects.

    Translator regression
    ---------------------
    SampleText rows double as regression test cases for the translator engine.
    After a rule change, run the translator on source_text for each sample
    and compare to romanization — drift indicates a broken rule.
    is_regression_test flags which samples are actively used for this purpose.
    """
    __tablename__ = "sample_texts"

    id          = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id",
                            ondelete="CASCADE"), nullable=False)
    dialect_id  = db.Column(db.Integer, db.ForeignKey("dialects.id",
                            ondelete="CASCADE"), nullable=False)

    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # The four parallel representations
    source_text  = db.Column(db.Text, nullable=False)
                             # original text in the source/natural language
    script_text  = db.Column(db.Text)
                             # conlang in space-separated script codes
    romanization = db.Column(db.Text, nullable=False)
                             # romanized conlang
    ipa          = db.Column(db.Text)
                             # IPA transcription
    translation  = db.Column(db.Text, nullable=False)
                             # English gloss

    # Regression testing
    is_regression_test = db.Column(db.Boolean, nullable=False, default=False)
                             # True = used to validate translator output

    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    language = db.relationship(
        "Language", 
        back_populates="sample_texts"
        )
    
    dialect  = db.relationship(
        "Dialect",  
        back_populates="sample_texts"
        )

    def __repr__(self):
        return (f"<SampleText {self.title!r} "
                f"dialect={self.dialect_id} regression={self.is_regression_test}>")