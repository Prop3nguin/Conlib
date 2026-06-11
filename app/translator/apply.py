"""
Docstring for app.translator.apply

--- Functions ---

apply_phonology_rules - (ipa, rules)
    - Phonology rules — tables touched: phonology_rules
    Fetch all active PhonologyRules for the target dialect, ordered by rule_order. 
    Apply them sequentially to each token's IPA string using apply_single_rule(), 
    which uses ipa_to_regex() to convert the environment field into a Python regex. 
    Empty output_ipa = deletion. Rules are applied to the token in isolation first, 
    then to adjacent token boundaries (scope: morpheme_boundary or word_boundary).

apply_single_rule - (ipa, rule)

match_environment - (ipa, position, environment)

apply_syntax_rules - (tokens, rules)
    - Syntax / word order — tables touched: grammar_rules
    Fetch active GrammarRules of type 'syntax' and 'cv_structure' for the language + dialect. 
    Reorder the token list according to the target dialect's constituent order (SOV, VSO, etc). 
    This is a structural transform — tokens keep their content, only position changes. Returns the reordered list.

apply_morphology_rules - (token, rules)


--- Note ---

apply.py — pure functions, no imports from models or db. 
Takes rule lists (already fetched by lookup.py) and token lists, returns transformed token lists. 
match_environment() converts a PhonologyRule.environment string like "_ [+front vowel]" into a Python regex via utils.ipa_to_regex().
"""