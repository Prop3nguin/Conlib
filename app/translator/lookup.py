"""
Docstring for app.translator.lookup

--- Functions ---

scan_idioms - (text, language_id, dialect_id)
    - Idiom scan — tables touched: idioms idiom_words
    Before tokenising, scan the full input string for idiom.phrase matches using a longest-match algorithm.
    Matched spans are marked and their idiom.meaning substituted directly — their component words are never processed individually. 
    This must run first or the tokeniser will split idioms apart.

lookup_word - (token, language_id, dialect_id)

analyze_morphemes - (token, language_id)
    - Morpheme analysis — tables touched: words morphemes
    For each WordToken, attempt a lexicon lookup first (lookup_word). 
    If no direct hit, decompose the token using the morpheme table — find the longest matching root, then identify prefix/suffix affixes. 
    Returns a MorphemeAnalysis with root word_id, list of morpheme_ids, and any unmatched residual.

resolve_inflected_form - (word_id, slot, dialect_id)
    - Paradigm lookup + inflection — tables touched: inflection_paradigms word_paradigms inflected_forms grammar_rules
    Given the word and the grammatical context (tense, case, number inferred from surrounding tokens and morphology rules), 
    look up the correct form slot label (e.g. '2SG.PAST'). Query inflected_forms for that slot, 
    filtering by dialect_id with a fallback to NULL (dialect-neutral forms). 
    Grammar rules of type 'morphology' are consulted to determine agreement and slot selection.

get_active_phonology_rules - (dialect_id)

get_active_grammar_rules - (language_id, dialect_id)

check_translation_memory - (source, language_id, dialect_id)
    - TM check + optional save — tables touched: translation_memory
    Query translation_memory for an exact or near-match on source_text + dialect_id with status='approved'. 
    If a match exists, attach it to the result as a reference (useful for the route to flag when output matches known-good translations).
    If save=True was passed to translate(), write the new result as a draft entry via save_to_translation_memory()
    with a confidence score from score_confidence().

save_to_translation_memory - (source, target, dialect_id, confidence)


--- Note ---

lookup.py — all SQLAlchemy queries live here and nowhere else. 
Each function returns plain Python objects (dataclasses or lists), never raw ORM instances. 
This isolation means the rest of the module can be tested without a database.
"""