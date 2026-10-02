# Assignment 2 — Architecture

```mermaid
flowchart LR
  U[Business user] --> I[File intake]
  I --> V[File, schema and row validation]
  V --> E[Actionable exception report]
  V --> N[Normalized records]
  N --> B[Confirmed business rules]
  B --> L[LetterData]
  T[Approved versioned template] --> R[PDF renderer]
  L --> R
  R --> Q[Output checks]
  Q --> H[Preview and agreed review]
  H --> D[Controlled release / delivery boundary]
  I -.-> M[Batch manifest, identity and audit]
  Q -.-> M
  H -.-> M
```

**POC:** local synchronous file processing and manifest. **Proposed production:** authenticated intake, private storage, durable row states, template registry, bounded retries, monitoring, and a delivery integration only when specified. Add a queue only if observed scale or processing time warrants it.
