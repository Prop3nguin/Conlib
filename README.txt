```mermaid
erDiagram

    Language {
        int id PK
        string name
        string status
        text description
    }

    LanguageRelationship {
        int id PK
        int source_language_id FK
        int target_language_id FK
        string relationship_type
    }

    Dialect {
        int id PK
        int language_id FK
        string name
    }

    Script {
        int id PK
        int dialect_id FK
        string name
    }

    Glyph {
        int id PK
        int script_id FK
        string symbol
    }

    Morpheme {
        int id PK
        int language_id FK
        string form
    }

    Lexeme {
        int id PK
        int language_id FK
        int paradigm_id FK
        string lemma
        string pos
    }

    Sense {
        int id PK
        int lexeme_id FK
        text definition
    }

    SemanticField {
        int id PK
        string name
    }

    InflectionParadigm {
        int id PK
        int language_id FK
        string name
    }

    WordForm {
        int id PK
        int lexeme_id FK
        int dialect_id FK
        string written_form
    }

    Pronunciation {
        int id PK
        int word_form_id FK
        string ipa
    }

    InflectedForm {
        int id PK
        int word_form_id FK
        string form
    }

    GrammarRule {
        int id PK
        int dialect_id FK
    }

    PhonologyRule {
        int id PK
        int dialect_id FK
    }

    Idiom {
        int id PK
        int dialect_id FK
    }

    IdiomWord {
        int idiom_id FK
        int word_form_id FK
    }

    TranslationMemory {
        int id PK
        int dialect_id FK
    }

    EtymologyArticle {
        int id PK
        int language_id FK
    }

    EtymologyEvent {
        int id PK
        int language_id FK
    }

    SampleText {
        int id PK
        int language_id FK
    }

    Language ||--o{ Dialect : contains
    Language ||--o{ Morpheme : contains
    Language ||--o{ Lexeme : contains
    Language ||--o{ InflectionParadigm : defines
    Language ||--o{ EtymologyArticle : documents
    Language ||--o{ EtymologyEvent : records
    Language ||--o{ SampleText : contains

    Language ||--o{ LanguageRelationship : source
    Language ||--o{ LanguageRelationship : target

    Dialect ||--o{ Script : uses
    Script ||--o{ Glyph : contains

    Dialect ||--o{ GrammarRule : defines
    Dialect ||--o{ PhonologyRule : defines
    Dialect ||--o{ Idiom : contains
    Dialect ||--o{ TranslationMemory : stores

    Lexeme ||--o{ Sense : has
    Sense }o--o{ SemanticField : categorized_as

    InflectionParadigm ||--o{ Lexeme : governs

    Lexeme ||--o{ WordForm : realized_as
    Dialect ||--o{ WordForm : uses

    WordForm ||--o{ Pronunciation : has
    WordForm ||--o{ InflectedForm : generates

    Idiom ||--o{ IdiomWord : contains
    WordForm ||--o{ IdiomWord : participates_in
```