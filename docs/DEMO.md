# Four-minute FreshRoute demo

Start the local server and load the bundled hackathon kickoff scenario before presenting. All sample values are synthetic; the planner is deterministic and bounded, not a trained model.

## Walkthrough

**0:00–0:40 — Frame the decision.** Show the available stock, demand, transport limits, and the contribution/fulfillment/spoilage estimates. Explain that the goal is to make a feasible dispatch decision under time and capacity constraints.

**0:40–1:20 — Show the risk.** Point to At-risk batches. Use the Banana or Spinach example if it appears under the configured threshold. Explain its quantity, expiry timing, and suggested action. State that markdown advice is rule-based and does not assume increased demand.

**1:20–2:00 — Open the evidence.** Select “View allocation” on an at-risk allocated batch, or open an allocation from the dispatch table. Walk through departure delay, travel, handling, usable arrival, receiving window, and expiry. Then show one rejected batch-route reason.

**2:00–3:00 — Change conditions.** Open Scenario lab and compare decision options first; then switch to Stress tests and compare current conditions with a route delay or reduced capacity. Point out the stated change and the contribution, fulfillment, and spoilage deltas versus Current conditions. Explain one trade-off; these are hypothetical stress tests, not forecasts.

**3:00–3:40 — Explain the economics.** Show the financial estimate and FIFO comparison. Clarify that unknown costs are excluded, inventory acquisition and modeled route costs are counted once, and markdown revenue uses the reduced selling price.

**3:40–4:00 — Close honestly.** Select a scenario to review, reset if desired, and mention the limits: synthetic input data, provisional FIFO, dedicated one-trip routes, divisible kilograms, and a bounded heuristic. Say “best feasible plan found,” not globally optimal.

## Recovery

If the API is unavailable, start it using the README instructions and use Retry connection. If edits make results stale, regenerate before exporting. Reset to the seed for a known starting point.
