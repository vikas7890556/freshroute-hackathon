# FreshRoute v2 — Product requirements

## Purpose

FreshRoute is a human-reviewed dispatch planning demo for Wild Bugs PS 03. It helps a produce distributor compare feasible batch-to-destination allocations under shelf-life, receiving-window, demand, and dedicated-trip constraints. It estimates modeled economics and makes the reasoning visible.

There is no organizer dataset or confirmed organizer baseline in this project. The bundled data and FIFO baseline are explicitly synthetic/provisional; they must not be presented as official or as real-world evidence.

## Primary user journey

1. Load the bundled synthetic hackathon kickoff scenario.
2. Review or edit batches, demand, destinations, and transport inputs.
3. Generate a plan and inspect allocations, route rejections, urgency, and financials.
4. Review the At-risk batches panel and its rule-based action hints.
5. Compare controllable options (base-price sales, markdowns on eligible surplus, holding stock) and separately inspect delay, capacity, demand, price, handling, and markdown stress cases.
6. Select a case for review, recalculate after edits, and export a current plan.

## Scope and constraints

Included: one hub; one dedicated direct trip per route; divisible kilograms; produce-specific base demand and maximum; explicit planning time and evaluation horizon; deterministic bounded candidate search; FIFO and earliest-expiry-first baselines; three objectives; explainable conditional markdowns; decision comparison and seven stress scenarios; JSON import and JSON/CSV export.

Excluded: demand prediction or guaranteed markdown uplift, CSV import, real-time market feeds, biological shelf-life prediction, shared vehicles, multi-stop routing, booking, user accounts, shared persistence, and claims of globally optimal real-world plans.

## At-risk batches

A batch appears on the overview when a non-expired batch has either (a) remaining shelf life at or below the configured at-risk threshold, or (b) a selected feasible allocation with 0–3 hours of usable-arrival slack. The panel shows an estimated at-risk quantity, expiry timing, the selected destination or a feasible route to review, and an action hint. It uses planner results and existing rule thresholds; it does not create a new dispatch or change the plan.

Rule-based markdown suggestions remain separate from the action hint. A markdown does not guarantee a sale or increase demand. If discounts are applied in a scenario, sales revenue uses the discounted sale price once.

## Economic and comparison language

The app reports **estimated net contribution**, not audited profit. It applies the same evaluation horizon and cost treatment to the proposed plan and FIFO. Unknown costs remain excluded and disclosed. Scenario table deltas are relative to the “Current conditions” case. Stress cases are hypothetical and not forecasts.

The planner reports “Best feasible plan found” because it searches a bounded deterministic set of candidates and does not certify global optimality.

## Acceptance criteria

- Every allocation shown as feasible passes stock, route, demand, receiving-time, handling, expiry, and horizon checks.
- Allocation evidence identifies selected timing and the constraints behind the decision.
- At-risk quantities are derived from the same scenario snapshot as the displayed plan and do not exceed batch quantity.
- Scenario deltas are calculated against Current conditions and all plans use the same rules within each case.
- Editing inputs marks results stale; stale results cannot be exported as current.
- Synthetic inputs, estimates, and provisional FIFO status are disclosed.
- The existing reset, import, export, scenario comparison, and financial views continue to work.
- The app remains usable on desktop and phone widths, with keyboard-visible focus and text labels in addition to color.
