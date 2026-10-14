# FreshRoute v2 — Implementation and demo readiness

## Current product slices

- **Working:** typed React interface, FastAPI contracts, synthetic sample, input validation, deterministic bounded planner, provisional FIFO baseline, financial reconciliation, three objectives, seven scenario comparisons, freshness timeline, markdown recommendations, JSON/CSV export, reset, and offline serving after dependency setup.
- **Added in this update:** At-risk batches summary on the dispatch overview; scenario deltas versus Current conditions; refreshed active documentation and demo story.
- **Assumed:** all bundled inputs and operational costs are synthetic; FIFO is a provisional baseline; demand is treated as sold when validly delivered; discount response is not predicted; conditional markdown volume above base demand is an explicit scenario assumption up to the configured maximum.
- **Future:** organizer data/baseline integration, validated demand response, calibrated shelf-life uncertainty, shared vehicles, multi-stop routing, accounts, and persistent multi-user operations.

## Suggested hackathon ownership

| Workstream | Owner focus | Integration evidence |
| --- | --- | --- |
| Data and product | Challenge interpretation, data provenance, assumptions | Reviewed scenario and field map |
| Planner | Feasibility, allocation search, dispatch evidence | API response and focused checks |
| Evaluation | FIFO, metrics, accounting, scenario comparisons | Hand-checked example and report |
| Frontend | Inputs, overview, at-risk list, responsive interface | Working user flow |
| Integration and demo | Run instructions, packaging, rehearsal | One-command local demo path |

Agree on contracts before parallel work. Keep a working end-to-end slice early and freeze feature scope before the final demo rehearsal.

## Remaining external gates

1. Replace provisional assumptions only when organizers provide authoritative rules or data.
2. Confirm permitted AI assistance, reused-code disclosure, submission format, and cutoff.
3. Confirm the judges can access the submitted demo URL, if hosting is used.
4. Run organizer-provided hidden checks if they become available and report results accurately.
5. Rehearse the walkthrough in `DEMO.md` against the final packaged build.
