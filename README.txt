# Test

```mermaid
erDiagram
    LANGUAGE ||--o{ DIALECT : has

    LANGUAGE {
        int id
        string name
    }

    DIALECT {
        int id
        string name
    }
```