# FreshRoute v2 — User flow

## Main flow

1. The app loads the bundled synthetic hackathon kickoff scenario and calculates the initial plan.
2. Dispatch overview shows contribution, spoilage, fulfillment, feasibility, At-risk batches, route capacity, and allocations.
3. The user opens allocation evidence to inspect departure, arrival, handling completion, expiry, receiving window, and freshness slack.
4. The user can review rejected batch-route combinations and their reasons.
5. Inventory & demand lets the user edit data, import a validated JSON scenario or batch CSV, export inputs, or reset to the seed.
6. Scenario lab separates controllable decisions (base-price sales, eligible surplus markdowns, hold stock) from seven hypothetical stress cases.
7. Financial estimate compares FIFO, earliest-expiry-first, and FreshRoute using the same horizon and disclosed cost model.
8. The user exports current dispatch CSV or evidence JSON. Edits mark results stale and disable result exports until recalculation.

## At-risk batches

The overview lists batches inside the configured at-risk rule. It shows at-risk quantity, time to expiry, selected destination or a feasible route to review, and a concise action hint. “View allocation” opens the existing freshness timeline. If the batch has no selected allocation, the list does not fabricate one; the user can inspect constraints and rerun after changing inputs.

## What-if comparisons

Decision options are ranked separately from stress tests. Decision options compare actions under current assumptions; stress cases show changes relative to current conditions and are not forecasts. Selecting a case loads its scenario and result for review; further edits mark that result stale.

## Key states

- Initial loading, API unavailable, validation error, and no-dispatch states are explicit.
- A failed plan request retains editable inputs and displays the error.
- Stale results are visibly flagged; stale exports are disabled.
- Reset returns to the bundled sample and regenerates a plan.
- Tables scroll horizontally on narrow screens; action buttons remain keyboard accessible.
