# Persistence And Data Guidelines

## Current Storage Model

There is no database, ORM, migration system, or server-side state store.
`web/widgets.json` is the complete runtime data file. Do not add a database
unless a new requirement first changes `PLAN_web.md`.

## JSON Contract

- Preserve the top-level fields `updated_at`, `layout`, `refresh_seconds`, and
  `widgets`.
- Treat `widgets.example.json` and the updater tests as executable contract
  examples.
- Update only the target widget and preserve unrelated widgets and fields.
- Crop source data to display fields. Never persist tokens, credentials, raw
  logs, transcripts, source IDs, attendee data, meeting links, or private notes.
- Enforce list limits at the producer: calendar at most four events, todo at
  most five items, and weather at most two forecast rows.

## Writes

Write the full document atomically:

1. Serialize formatted UTF-8 JSON with a trailing newline.
2. Write a temporary file in the destination directory.
3. Set mode `0644` so Caddy can read it.
4. Replace the destination with `os.replace`.

Examples: `scripts/web_update.py:atomic_write_json` and
`scripts/update_weather.py:atomic_write_json`.

## Forbidden Patterns

- Partial in-place writes to `widgets.json`.
- Mirroring an upstream API or local application record wholesale.
- Adding SQLite, an ORM, or migrations for the static MVP.
- Clearing good data because one source refresh failed.
