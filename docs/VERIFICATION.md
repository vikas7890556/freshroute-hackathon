# FreshRoute v2 verification — 14 October 2026

## Checks run for this update

- `npm run build`: passed TypeScript checking and the Vite production build using the dependencies already present in the earlier FreshRoute workspace. No packages were downloaded. The packaged `dist/` was refreshed from the updated source.
- 14 focused Python planning tests passed, including new checks for the lower-demand maximum and the decision explanation. The HTTP `TestClient` integration check was not completed in this restricted environment because its local request stalled; direct calls to the health, sample, plan, comparison, and decision handlers passed.
- The synthetic evaluator completed all seven stress cases across the three objectives. The generated report is in ignored `output/` and is not part of the source ZIP.
- A browser smoke check and public Vercel deployment were not repeated after this update. No deployment is claimed.

A deprecation warning from the installed Starlette TestClient/httpx combination appears during tests. No claim is made that every browser, operating system, or every individual control has undergone exhaustive manual testing. CSV import is batch-only and was type/build checked, not exercised by uploading a file in this update.

## Synthetic contribution-objective estimates

| Case | FIFO net INR | Proposed net INR | Spoilage kg | Fulfillment % |
|---|---:|---:|---:|---:|
| Current conditions | 1,270.00 | 2,185.00 | 25 | 81.8 |
| Route delay | -95.00 | 820.00 | 60 | 72.7 |
| Reduced capacity | -1,569.00 | -215.00 | 61 | 59.2 |
| Lower demand | -54.50 | -54.50 | 85 | 93.5 |
| Lower price | -6.00 | 815.50 | 25 | 81.8 |
| Extra handling | 1,140.00 | 1,380.00 | 35 | 68.8 |
| Conditional at-risk markdowns | 2,049.50 | 2,964.50 | 0 | 81.8 |

The markdown case assumes that demand above the base estimate, up to the explicitly entered maximum, can be sold at the suggested lower price. This is a scenario assumption, not a measured demand response or forecast. The sample dataset, prices, routes, cost inputs, and organizer baseline are synthetic or provisional.

## Known limits

The bundled sample is synthetic and the organizer’s official baseline/cost model is not available. Net contribution is a provisional estimate: sold-stock acquisition and expired-stock write-off are charged; usable inventory remains reported at acquisition value. The deterministic search remains bounded to six routes and 30 batches, and is not a global-optimality certificate. CSV import supports batch rows only; it retains active destinations, demand, routes, and scenario costs, and displays that fact in its import report. Exact MILP sensitivity analysis, custom continuous stress sliders, and fixed-plan-versus-replanned disruption analysis are not implemented.

The API does not book shipments or change prices. No production authentication, public deployment, or real-world operational impact has been verified.
