"""
Docstring for app.translator

--- Functions ---

translate - (text, language_id, dialect_id, save=False)

validate - (source, target, dialect_id)


--- Note ---

__init__.py — the only public surface of the module. translate() runs the full pipeline and returns a TranslationResult. 
validate() checks a source/target pair against translation_memory and returns a match score. 
Routes import only from here — never directly from pipeline.py or lookup.py.

"""
