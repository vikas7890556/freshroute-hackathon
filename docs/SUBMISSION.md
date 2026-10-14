# Hackathon submission preparation

## Draft description

FreshRoute is a human-reviewed decision-support demo for perishable produce dispatch. It compares batch-to-destination plans under shelf-life, demand, receiving-window, handling, and dedicated-trip constraints. The control tower shows allocation evidence, at-risk batches, scenario changes, and a reconciled estimate of net contribution, fulfillment, and spoilage against a disclosed provisional FIFO baseline. Its markdown suggestions are bounded rules; demand does not increase in response. The bundled data is synthetic and all results are modeled estimates, not operational evidence.

## Evidence checklist

- [x] Batch-level inventory, expiry, and acquisition cost.
- [x] Produce-specific demand, prices, destination windows, and transport capacity/costs.
- [x] Arrival, handling, receiving window, expiry, and horizon feasibility checks.
- [x] Explainable allocation and rejected-route evidence.
- [x] At-risk batches and bounded markdown suggestions.
- [x] Shared accounting and evaluation horizon for proposal and FIFO.
- [x] Seven hypothetical scenarios compared against current conditions.
- [x] Synthetic data provenance and model limits disclosed.
- [ ] Organizer dataset, baseline, and cost model confirmed if provided.
- [ ] AI/reuse policy and required disclosures confirmed.
- [ ] Deadline and submission format confirmed.
- [ ] Judge access to deployment verified, if hosted.
- [ ] Final demo rehearsed and submission receipt retained.

## Disclosure draft

This is a hackathon prototype developed with AI coding assistance. Bundled data is synthetic, FIFO is provisional, and outcomes are estimates under documented assumptions. The planner uses a bounded deterministic search and does not guarantee global optimality or real-world results. Update this statement to reflect actual team contributions, data sources, and organizer requirements before submitting.
