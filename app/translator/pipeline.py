"""
Docstring for app.translator.pipeline

--- Functions ---

run_pipeline - (tokens, dialect_id)

tokenise - (text)
    - Tokenise — tables touched: no db queries
    Split the (now idiom-annotated) input into a list of Token objects. 
    Each token carries its surface form, its span offset, 
    and a flag indicating whether it belongs to an idiom match from step 1. 
    Idiom spans produce a single IdiomToken; remaining text produces WordTokens.

build_token_spans - (text, idiom_matches)

merge_results - (spans, romanization, script)


--- Note ---
pipeline.py — pure orchestration, no db calls. 
Calls lookup.py and apply.py in order, passes results through each stage. 
run_pipeline() is the internal entrypoint called by __init__.translate(). 
Keeping this db-free makes it trivially testable with mocked lookup functions.
"""