# Codex Quota Freshness Design

## Research Gate

The implementation begins with a source inventory, not a parser patch. Inspect
recent Codex storage surfaces with privacy-cropped tooling that emits only:

```text
source_kind, event_kind, schema keys, timestamp, freshness, bounded file count
```

Determine which of these cases is true:

1. `token_count.rate_limits` still exists but bounded discovery misses it.
2. The event exists under a new structural envelope or field names.
3. A different existing local Codex surface exposes the same bounded quota.
4. No current authoritative quota is available.

Case 4 is a valid no-go; increasing `DEFAULT_STALE_AFTER_SECONDS` is not.

## Source Adapter Boundary

Keep source-specific parsing pure and testable. Normalize an accepted source to
the existing internal shape before it reaches `merge_quota`:

```json
{
  "source": "bounded-source-label",
  "updated_at": "ISO-8601",
  "stale": false,
  "five_hour": {
    "remaining_percent": 0,
    "window_minutes": 300,
    "resets_at": 0
  },
  "weekly": {
    "remaining_percent": 0,
    "window_minutes": 10080,
    "resets_at": 0
  }
}
```

Unavailable windows may be omitted, but a source must contain at least one
recognized bounded window to count as authoritative.

## Selection And Freshness

- Compare candidate timestamps and select the newest valid authoritative
  record, not the newest file.
- Apply the source's real observation timestamp. File modification time cannot
  turn an old observation fresh.
- Preserve existing 600-second semantics unless evidence proves the selected
  source has a different documented cadence. Any cadence change requires an
  explicit test and spec update.
- If all candidates are missing, malformed, or old, return `None` or a stale
  result through the existing merge path.

## Privacy Boundary

Parsers use explicit field allowlists. They never pass through raw source
objects. Diagnostic output reports source health and structural reason labels
only. Test fixtures must include forbidden fields and prove they are absent
from the normalized quota and routine output.

## Rollout

1. Prove the source and parser locally with fixtures.
2. Run full local checks and a redacted source check.
3. Preview against the live baseline.
4. Publish only the owned payload through the existing locked installer.
5. Verify weather preservation, fresh live quota, and one natural scheduler
   tick.

If production evidence does not stay fresh, revert the quota source change and
retain the prior explicit stale behavior.
