# FreshRoute v2 — Technical overview

## Runtime

- React 19, TypeScript, Vite, and Tailwind CSS frontend.
- Python FastAPI backend with Pydantic request and response contracts.
- Local synthetic JSON seed; no database, API key, or external runtime service.
- FastAPI serves the built frontend from `dist/` when that directory exists.

## API

- `GET /api/health` — local engine health and version.
- `GET /api/sample` — bundled scenario.
- `POST /api/plan` — plan and baseline for a scenario and objective.
- `POST /api/compare` — evaluate seven hypothetical stress cases.
- `POST /api/decisions` — compare three controllable planning options.

## Planning and evidence

The backend validates dates, units, quantities, IDs, demand bounds, and route references. Feasibility checks include route eligibility, demand, arrival time, receiving window, destination handling, batch expiry, and the evaluation horizon. Rejected batch-route pairs retain human-readable reasons.

The planner enumerates a bounded deterministic set of route subsets and allocation orderings. It compares those candidates with FIFO and hold-all plans. This is a bounded heuristic, not a global-optimality certificate.

FIFO uses the oldest received timestamp, then stable input order. It is provisional until an organizer baseline is supplied.

## Discount rule

The current implementation is a rule-based markdown suggestion: 15% when usable-arrival slack is at most three hours, otherwise 10% for eligible at-risk stock, bounded by the configured discount cap and minimum price. Risk is triggered by remaining shelf life within the configured threshold or usable-arrival slack within three hours. Markdowns can use only at-risk stock expiring within the shared evaluation horizon and demand headroom above the declared base quantity, up to the explicit maximum. Extra demand is assumed only up to the declared maximum, not forecast from price elasticity. The plan shows the resulting contribution and a fixed-trip break-even amount when applicable.

## Economics and horizon

Net contribution uses sales revenue less sold-stock acquisition, expired-stock acquisition write-off, and applicable modeled transport, handling, packaging, storage, platform, tax, and disposal costs. Remaining usable inventory is shown separately at cost. Null optional costs are excluded and shown as not provided; explicit zero remains zero. This cost convention is provisional until organizer rules are available. Unsold items expiring on or before horizon end count as estimated spoilage; usable inventory after the horizon remains inventory. All compared plans share the same horizon and cost rules.

## At-risk view

The frontend derives the overview list from the active result snapshot. It uses the configured life threshold plus selected allocation slack, reports estimated affected quantity without exceeding available stock, and links allocated items to the existing freshness timeline. It does not change allocation decisions or claim that a markdown increases sales.
