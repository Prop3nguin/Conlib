# Language Data Structure

## Overview

A **Language** is the top-level entity. It has no parent or child languages,
but can be related to other languages via defined relationship types. Everything
below it — etymology, dialects, lexicons, and scripts — descends from it.

---

## Language
- Name, status (living / extinct / liturgical / constructed)
- Typological metadata
  - Default word order (SOV, SVO, VSO, etc.)
  - Morphological type (isolating, agglutinative, fusional, polysynthetic)
  - Phonemic inventory summary
- Language relationships *(many-to-many with other Languages)*
  - Relationship type (common ancestor, borrowing/contact, creole, etc.)
  - Directionality (e.g. Language A borrowed from Language B)

---

## Etymology
Articles and structured data explaining the origin and evolution of the language.

- ### Articles
  - Evolution of dialects over time
  - History and origin of the language
  - Cultural influences on vocabulary and usage
    - How beliefs, events, and social structures shaped popular phrases
  - Loanword sources — which languages borrowed from which, and in what era

- ### Timeline
  - Structured chronological record of sound changes and grammatical shifts
  - Anchors historical translation rules for the rule-based translator

---

## Dialects
Dialects form a tree. Each dialect can have a parent dialect and child dialects.

- Name, geographic or social tag (regional, class-based, archaic, pidgin, etc.)
- Mutual intelligibility rating with sibling dialects
- Phonological shift rules from parent dialect
  - e.g. /k/ → /tʃ/ before front vowels
  - These are the rules the translator runs on

- ### Phonology *(dialect-level)*
  - Phonemic inventory (vowels, consonants, tones)
  - Phonotactics — legal and illegal sound combinations
  - Prosody — stress patterns, tone, intonation
  - Phonological rules — assimilation, elision, sandhi, etc.

- ### Lexicon
  - #### Morpheme Table
    - Roots, prefixes, and suffixes as first-class entries
    - Each morpheme has meaning, IPA, and grammatical role
    - Essential for agglutinative and fusional languages

  - #### Words
    - Script code (glyph identifier for the custom font)
    - Romanization
    - Part of speech and subtype
    - Register (formal, informal, archaic, vulgar)
    - Senses (one word may have multiple meanings)
      - Definition
      - Example sentence
      - Semantic field tags
    - Inflected forms (dialect-aware, paradigm-linked)

  - #### Idioms and Collocations
    - Multi-word phrases whose meaning is not compositional
    - Cannot be translated word-by-word

  - #### Grammar Rules
    - **Morphology** — how words inflect (paradigms, agreement, case, etc.)
    - **Phonology rules** — how sounds behave in context
    - **Syntax** — sentence construction, clause embedding, word order details
    - **CV Structure** — consonant-vowel templates and syllable shape

  - #### Inflection Paradigms
    - Named templates (e.g. "Class I Verb", "Animate Noun")
    - Form labels and their script codes + romanizations
    - Dialect-aware (forms may differ across dialects)

  - #### Translation Memory
    - Stored sentence pairs (source → translated)
    - Used for consistency and validation of the rule-based translator

- ### Script *(writing system)*
  - Custom font (font-face name, file reference)
  - Directionality (LTR, RTL, top-to-bottom)
  - Script type (alphabet, syllabary, abjad, logographic, etc.)
  - Orthographic rules
    - How glyphs combine or change form in context
    - Ligatures, contextual alternates, mandatory joins

  - #### Glyph Table
    - Individual characters as atomic entries
    - Script code (maps to custom font glyph)
    - Unicode codepoint
    - Romanization equivalent
    - IPA value

  - #### Punctuation and Numerals
    - Separate glyph entries for punctuation marks
    - Numeral system (if distinct from a borrowed one)

  - #### Unicode Romanization
    - Full romanization scheme for the language
    - Mapping table: glyph → romanization character(s)

  - #### International Phonetic Alphabet
    - Full IPA mapping for the language
    - Dialect-aware (IPA may differ per dialect)

---

## Sample Texts
Canonical passages used to demonstrate the language, test font rendering,
and anchor the translator. Acts as a Rosetta Stone for the language.

- Title and description
- Source text (in script code / custom font)
- Romanization
- IPA transcription
- Translation
- Dialect tag

---

## SQL Coverage Notes

| Feature | Status |
|---|---|
| Languages + relationships | ✅ `languages` table; relationship table needed |
| Dialects (tree structure) | ✅ `dialects` with `parent_dialect_id` |
| Scripts + font faces | ✅ `scripts` table |
| Words + script codes | ✅ `words` table |
| Senses + semantic fields | ✅ `senses`, `semantic_fields`, `sense_fields` |
| Inflection paradigms | ✅ `inflection_paradigms`, `word_paradigms`, `inflected_forms` |
| Pronunciations (dialect-aware IPA) | ✅ `pronunciations` table |
| Morpheme table | ⬜ Needs new table |
| Phonology rules | ⬜ Needs new table |
| Grammar / syntax rules | ⬜ Needs new table |
| Idioms and collocations | ⬜ Needs new table |
| Etymology articles + timeline | ⬜ Needs new tables |
| Glyph table | ⬜ Needs new table |
| Sample texts | ⬜ Needs new table |
| Translation memory | ⬜ Needs new table |
| Language typology metadata | ⬜ Needs columns on `languages` |
| Language relationships | ⬜ Needs junction table |
| Register on words | ⬜ Needs column on `words` |
| Dialect social/geographic tag | ⬜ Needs column on `dialects` |