# FreshRoute · Freshness Control Tower

**Live demo:** [freshroute-dispatch.vercel.app](https://freshroute-dispatch.vercel.app) · [API health check](https://freshroute-dispatch.vercel.app/api/health)

FreshRoute is a decision-support demo for Wild Bugs PS 03: perishable produce distribution. It turns inventory, destination demand, shelf life and transport limits into an explainable dispatch plan, financial estimate and scenario comparison.

**Stack:** React, TypeScript, Vite and Tailwind for the interface; FastAPI and a deterministic Python planner for the API. The bundled sample data is synthetic. No API keys, database or Docker are required. Dependency installation needs internet once; normal operation does not.

> **Demo data notice:** All bundled scenario values are synthetic and intended for demonstration. Financial and spoilage outputs are estimates under the assumptions below, not operational or accounting advice.

## What the demo includes

- Dispatch recommendations constrained by stock, demand, shelf life, receiving windows, route capacity, travel, departure delay and handling time.
- A financial estimate that itemizes modeled revenue and costs, plus fulfillment, spoilage and remaining usable inventory.
- FIFO and earliest-expiry baselines, at-risk batch review and conditional markdown suggestions.
- Decision comparisons, disruption scenarios, explainable constraint checks, and JSON/CSV import and export.

## Start here

- [Run locally](#setup-from-a-laptop-with-only-vs-code)
- [Deployment and live URL](docs/DEPLOYMENT.md)
- [Four-minute demo script](docs/DEMO.md)
- [Verification notes](docs/VERIFICATION.md)
- [Data, method and assumptions](#data-method-and-assumptions)

The GitHub `main` branch is connected to Vercel. Changes committed to `main` trigger a new deployment; the live alias is managed in Vercel and does not need to be embedded in application code.

## Setup from a laptop with only VS Code

1. Install **Node.js 24 LTS** using the Windows x64 MSI from [Node.js downloads](https://nodejs.org/en/download). Keep npm and Add to PATH selected. Choose ARM64 on ARM laptops.
2. Install **Python 3.13** using the Windows installer from [Python downloads](https://www.python.org/downloads/windows/). Enable the launcher and Add Python to PATH. The Python install manager also supports `py install 3.13`. This source targets Python 3.13+; verification used the project’s Python 3.13 runtime.
3. Install **Git for Windows** from [Git's official installer](https://git-scm.com/install/windows). Keep Git available from the command line. Git is useful for collaboration but not needed to run the supplied folder.
4. Restart VS Code, open the `freshroute` folder, and open Terminal → New Terminal:

```powershell
node --version
npm.cmd --version
py -3.13 --version
git --version
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-lock.txt
npm.cmd install
npm.cmd run build
```

The Python lock file records tested dependencies; `backend/requirements.txt` lists supported direct ranges. The project uses the npm lockfile (`package-lock.json`) for repeatable installs. Import a full JSON scenario or batch rows from CSV. CSV headers accept batch id, produce, quantity, acquisition cost, received time, expiry or shelf-life hours, grade, and source aliases; the built-in template and import report explain which active demand, route, and cost assumptions are retained.

## Offline demo — one server

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. Leave the terminal running; Ctrl+C stops it. FastAPI serves the compiled frontend and API. `./Start-FreshRoute.ps1` runs the same command after setup. If PowerShell scripts are restricted, use the Python command; no policy changes are needed.

The included `dist/` has the compiled frontend. Teammates need only Python and the backend requirements to run this packaged demo; Node is needed to edit/rebuild. Do not open index.html directly. Reload resets seeded data; use JSON export to preserve edits.

## Development — two terminals

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
npm.cmd run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` to port 8000. No environment file is needed locally. See `.env.example` and [deployment](docs/DEPLOYMENT.md) for separate hosting.

On macOS/Linux install Node 24 LTS, Python 3.13 and Git; use `python3.13 -m venv .venv`, `.venv/bin/python` instead of the Windows Python path, and `npm` instead of `npm.cmd`.

## Verification and demo

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
npm.cmd run build
.\.venv\Scripts\python.exe scripts/evaluate.py
```

The evaluator writes `output/evaluation-v2.json`. See [verification](docs/VERIFICATION.md) and the [four-minute demo](docs/DEMO.md).

The complete flow is dashboard → edit inventory/demand/transport → generate → review At-risk batches and allocation timeline → inspect rejected routes and finances/FIFO → compare seven scenarios with deltas versus Current conditions → select a case → export CSV/JSON or reset. Stale-result exports are disabled. The at-risk panel is a rule-based review aid and does not change the plan. The full JSON editor supports adding destinations and routes; imports are validated before applying.

## Data, method and assumptions

No official dataset or organizer baseline was found. `backend/data/sample.json` is manually constructed, entirely synthetic: five batches, three destinations, three dedicated routes, nine demand rows. The sample planning time is **2026-10-15 12:00 IST**, aligned to the announced event start, with a fixed 12-hour horizon. All quantities are divisible kg and currency is INR. Grade/source are metadata. Changing planning time does not automatically shift batch dates.

Each route is one dedicated vehicle trip. One hub is assumed; origin is a label, not multi-hub routing. Arrival = planning time + departure delay + travel; usable arrival adds handling. Arrival and handling must fit receiving windows, expiry and horizon. Early arrival is rejected; edit departure delay to arrive later. Eligibility, stock, route capacity and demand are hard constraints. Empty eligibility means all produce. Valid delivered demand is assumed sold.

The bounded planner enumerates route subsets and tries four greedy orderings, both all feasible and positive-margin-only variants, alongside FIFO and holding stock. It returns the **best feasible plan found**, not a certified global optimum. Limits: 30 batches, 6 routes/destinations, 10 produce-demand rows per destination. Unknown fields are rejected so supplied cost components cannot disappear silently. Invalid dates, missing prices, negative/non-finite quantities and incompatible units are rejected.

- **Contribution:** maximize estimated net contribution.
- **Balanced:** maximize contribution subject to fulfillment ≥ FIFO and spoilage ≤ FIFO.
- **Spoilage:** minimize spoilage with contribution ≥ best checked contribution minus max(₹100, 10% of its absolute value).
- **Tie-breakers:** lower spoilage, higher fulfillment, lower transport cost for contribution/balanced; higher fulfillment, higher contribution, lower transport cost for spoilage. Remaining exact ties use stable candidate order.
- **FIFO:** oldest received timestamp first; stable batch input order for ties; route input order. Provisional until organizers supply a baseline.
- **Dispatch priority:** smaller of shelf-life and receiving-window slack, then demand priority, departure, batch ID and route ID. The ranking is a review order; actual departure timestamps remain visible.
- **Discounts:** at-risk batches may receive a rule-based markdown suggestion. A markdown can allocate only surplus demand above the base quantity, up to the explicitly supplied maximum; this uplift is an assumption, not a demand forecast. It is never recommended for stock that already meets its declared maximum. Break-even covers any incremental fixed trip cost; variable costs and avoided disposal are included in the plan economics.

Net contribution = sales − acquisition cost of sold stock − acquisition write-off of unsold stock expiring within the evaluation horizon − transport − handling − disposal − any supplied packaging, storage, platform and simplified tax costs. Remaining usable stock is shown separately at acquisition value and is not deducted as a sold cost or spoilage. Platform/tax are modeled fractions, not statutory calculations. Optional `null` cost means not provided/excluded; zero means explicitly zero. Discounts already appear in sales prices and are not deducted twice. This is a provisional model until organizers confirm their cost rules; future sales and salvage value are excluded.

Unsold stock expiring on or before horizon end is estimated spoilage; stock expiring later is remaining usable inventory. Every comparison uses the same horizon. Scenario cases derive from current edits, not hidden default fixtures. Scenario conditions are hypothetical and may not be controllable.

## Project layout

- `src/`: typed React UI and Tailwind/CSS styling.
- `backend/`: strict contracts, feasibility, planner, FIFO, metrics, scenario evaluation, tests and seed.
- `dist/`: compiled frontend for offline serving.
- `scripts/evaluate.py`: reproducible synthetic report.
- `docs/batch-import-template.csv`: sample batch import format (synthetic values).

## Public demo deployment

The public demo runs on Vercel with the Vite UI and FastAPI planner as two services. The `/api/*` route is sent to FastAPI; other paths are served by the UI. Open [freshroute-dispatch.vercel.app](https://freshroute-dispatch.vercel.app), or check [API health](https://freshroute-dispatch.vercel.app/api/health). See [deployment notes](docs/DEPLOYMENT.md) for the setup and smoke checks. Vercel Hobby is subject to its current usage limits; check the [Hobby plan details](https://vercel.com/docs/plans/hobby). The app has no database or accounts, so edits are not shared or persisted after reload unless exported.

Older documents are labeled historical. The original parent ZIP is untouched; use this source tree for the current implementation. The old static Site manifest is not a deployment of this Python-backed version.

## Implemented / estimated / future

Implemented: complete local flow, input validation, health endpoint, three objectives, FIFO and earliest-expiry baselines, controllable decision comparison, seven stress cases, timeline/network interactions, financial reconciliation, JSON scenario import, batch CSV import, JSON/CSV export and reset. Costs and spoilage are estimates using disclosed assumptions. Future work: official data integration, calibrated freshness, integer pallets, shared vehicles, multi-stop routing, uncertainty, accounts and shared persistence. No booking or market-price changes occur. No real operational impact or public deployment is claimed.
