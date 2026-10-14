# FreshRoute v2 — Scenario and result schema

The source of truth for request and response types is `backend/models.py`; matching frontend types are in `src/types.ts`. The API rejects unknown fields, invalid dates, non-finite values, negative quantities/costs, duplicate IDs, incompatible units, and invalid references.

## Inputs

| Entity | Main fields |
| --- | --- |
| Scenario | id, name, synthetic, planningTime, horizonHours, currency, maxDiscount, riskHours, cost assumptions, applyDiscounts |
| Batch | id, produce, grade, quantity in kg, received, expiry, acquisition cost per kg, source |
| Destination | id, name, receiving opens/closes, produce-specific demands |
| Demand | produce, quantity, maximum, price, minimumPrice, priority |
| Route | id, origin, destination, travel, delay, handling, capacity in kg, fixedCost, perKg, handlingCost, eligible produce |

All timestamps include a timezone. Currency is INR and quantity unit is kg in the current version. Null optional cost values mean not provided and excluded; numeric zero is an explicit zero cost.

## Results

`POST /api/plan` returns FreshRoute, provisional FIFO and earliest-expiry-first plans, rejected batch-route pairs, conditional markdown suggestions, selected objective, candidate count, guardrail, and binding constraints. Each allocation includes batch, destination, route, quantity, price, planned departure, latest safe departure, arrival, usable time, expiry, freshness slack, urgency, and reason.

`POST /api/compare` returns seven stress cases, each with a changed scenario and plan results. `POST /api/decisions` ranks base-price sales, markdown-eligible surplus, and holding stock as controllable choices. The browser accepts full JSON scenarios or a batch CSV. Batch CSV aliases include batch id, produce, quantity, acquisition cost, received time, expiry/shelf-life hours, grade, and source. Naive timestamps are interpreted as IST; missing receipt time defaults to planning time. CSV import retains active scenario demand, routes, and economic settings and reports these assumptions.

## At-risk display rule

A non-expired batch is displayed when its remaining life is within `riskHours` or when a selected allocation has 0–3 hours of usable-arrival slack. Displayed quantity is the selected allocation quantity that meets the rule, plus unallocated quantity when the batch's remaining life meets the threshold, capped at starting batch quantity. This is a decision aid and does not mutate the plan.

## Accounting conventions

Sales equal allocated quantity multiplied by the applied sale price. Acquisition cost is charged for stock sold plus a write-off for unallocated stock expiring within the shared horizon. Usable stock after the horizon remains inventory and is shown separately. Fixed transport is charged once per used route; variable transport and handling use shipped quantity; optional packaging, storage, platform, tax and disposal costs follow the scenario inputs. Discounts are reflected in the sale price and never deducted twice. Spoilage is unallocated stock expiring on or before the shared evaluation horizon; stock usable after that horizon remains inventory.
