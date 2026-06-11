"""
Docstring for app.translator.utils

--- Functions ---

normalise_text - (text)

longest_match - (candidates, text, start)

ipa_to_regex - (environment_str)

score_confidence - (result, rules_fired)


--- Note ---
utils.py — stateless helpers with no db imports. ipa_to_regex() is the most critical: 
it parses environment notation (e.g. "C _", "# _", "_ [+nasal]") into Python regex patterns used by apply.py. 
longest_match() powers the idiom scanner.

"""