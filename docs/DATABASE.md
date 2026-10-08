# VisionNext AI — Database Schema Documentation

Built on PostgreSQL (with SQLite async support for local execution). Uses SQLAlchemy 2 and Alembic migrations.

## Entity Relationship Diagram

```
[ users ] 1────N [ conversations ] 1────N [ messages ]
   │                     │                     │
   1                     1                     1
   │                     │                     │
   N                     N                     N
[ refresh_tokens ]   [ images ] ──────────> [ verification_runs ]
                         │                     │
       ┌─────────────────┼─────────────────┐   1
       │                 │                 │   │
       N                 N                 N   N
[ visual_objects ] [ ocr_results ] [ visual_evidence ] [ claims ]
```

## Indexes & Caching
- `images.sha256`: Indexed for instant detection lookup & re-upload caching.
- `messages(conversation_id, created_at)`: Composite index for fast conversation retrieval.
- `visual_objects.image_id`: Indexed for overlay rendering.
- `verification_runs.image_id`: Indexed for audit logs.
