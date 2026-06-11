"""
Docstring for app.translator.render

--- Functions ---

render_output - (tokens, script_id)
    -  Script render — tables touched: glyphs scripts
    Map each token's script_code to a Glyph row via script_code_to_glyph(). 
    Build three parallel output representations: romanization (from token.romanization), 
    script codes joined by spaces, and IPA (post-phonology). Return a TranslationResult dataclass with all three, 
    plus the source text and dialect_id for provenance.

script_code_to_glyph - (script_code, script_id)

tokens_to_romanization - (tokens)

tokens_to_ipa - (tokens)

build_translation_result - (romanization, script, ipa)


--- Note ---

render.py — assembles the final output from transformed tokens. 
Queries glyphs once per script_id and caches the mapping for the request.
Returns a TranslationResult dataclass with romanization, script_codes, and ipa fields. 
The route decides which representation to return to the client.

"""