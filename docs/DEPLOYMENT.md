# Vercel deployment

**Live demo:** [freshroute-dispatch.vercel.app](https://freshroute-dispatch.vercel.app)  
**Health check:** [freshroute-dispatch.vercel.app/api/health](https://freshroute-dispatch.vercel.app/api/health)

FreshRoute is deployed as one Vercel project with two services from this repository:

- **`app`** — the Vite frontend at `/`.
- **`backend`** — the FastAPI planner, routed through `/api/*`.

The root `vercel.json` defines these services and their rewrites. Keep the service roots and routes as configured; the frontend calls the backend using same-origin `/api/...` URLs. The application does not need environment variables, API keys, a database, or Google Cloud billing for the synthetic demo.

## Deploy from GitHub

1. Connect the GitHub repository to a Vercel project. The repository root should contain `vercel.json`, `package.json`, `backend/`, and `src/`.
2. Set **Root Directory** to `./` and keep the detected **Services** preset and configuration from `vercel.json`.
3. Deploy. Vercel builds the frontend and backend services independently. Commits pushed to the connected production branch (currently `main`) trigger a new deployment.
4. In Vercel **Settings → Domains**, assign the project a `.vercel.app` domain. The current demo alias is [freshroute-dispatch.vercel.app](https://freshroute-dispatch.vercel.app); [freshroute-hackathon.vercel.app](https://freshroute-hackathon.vercel.app) is also retained as a backup.

## Smoke-check after deployment

1. Open the demo URL and confirm the dashboard loads with the **Synthetic demo data** label.
2. Open `/api/health` on that same domain. It should return JSON with `"status":"ok"`.
3. Click **Generate plan**. Confirm allocations and financial metrics appear and the feasibility card reports zero constraint violations for the sample.
4. Visit **Scenario lab** and **Financial estimate** to verify comparison requests work too.

If the frontend loads but the plan request fails, inspect the failed `/api/plan` request in the browser Network panel and the Vercel runtime logs. A frontend-only check is not sufficient: `/api/health`, `/api/sample`, `/api/plan`, and comparison endpoints exercise separate backend paths.

## Deployment limits and data handling

- The included scenario data is synthetic. Do not present it as organizer-supplied or real-world data.
- Planning and financial results are estimates under the model assumptions in the [README](../README.md#data-method-and-assumptions). The planner is a bounded deterministic heuristic, not a certified global optimizer.
- There is no account system or persistent database. Scenario edits are request-scoped and are not shared across users; export them before reloading if needed.
- Vercel Hobby has usage limits and plan terms. Review the current [Hobby plan details](https://vercel.com/docs/plans/hobby) before using this project beyond a non-commercial demo.
- A first request after inactivity may take longer while a serverless function starts. Open the demo and try the main flow shortly before presenting.
