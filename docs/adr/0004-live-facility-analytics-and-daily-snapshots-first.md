# ADR 0004: Live Facility Analytics and Daily Snapshots First

## Status

Accepted for Week 8.

## Context

ShieldTB now has enough workflow data to support dashboard-like analytics:

- patient enrollment
- risk tiers
- household tracing
- workflow task progress
- notification activity

The long-term platform may need scheduled aggregation jobs, warehouse-style
tables, materialized views, and more advanced reporting infrastructure.

At Week 8, the immediate need is operational visibility for facilities and
pilot teams without introducing a separate analytics stack too early.

## Decision

Started with two analytics layers:

- live facility summary endpoints computed directly from transactional tables
- `FacilityDailyMetric` snapshots refreshed explicitly for the current day

The daily snapshot refresh is available through a management command and an
admin/analyst-only API action.

## Why This Is Acceptable Now

- It provides useful dashboards immediately.
- The logic stays close to the domain models that already exist.
- It avoids premature warehouse or queue complexity.
- The snapshot model gives us a clean handoff point for scheduled aggregation
  later.

## Consequences

Positive:

- Week 8 delivers usable facility metrics now.
- API consumers can build dashboards without waiting for background jobs.
- The refresh path is explicit and easy to test.

Tradeoffs:

- Live summaries query transactional tables directly.
- Snapshot refresh currently captures today's state, not a full historical
  reconstruction engine.
- This design will not be ideal for heavy reporting load or long-range trends.

## Revisit Triggers

Move to scheduled/background aggregation when any of these become true:

- dashboard traffic becomes large enough to pressure transactional queries
- we need county or national rollups with more history
- we need scheduled daily snapshots without manual/API refresh
- we add charts or reports that depend on longer time-series windows

## Future Design

Keep the API surface stable while moving implementation toward:

- Celery-scheduled daily metric refresh
- Redis-backed task scheduling
- materialized summary tables or views
- richer cohort and trend analytics
