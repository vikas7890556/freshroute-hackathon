# Public demo deployment with Vercel

Vercel Hobby can host this project without a Google Cloud billing account. The deployment keeps the existing React UI and FastAPI planner. Vercel builds the Vite frontend, uses `app.py` as the FastAPI entry point, and promotes the frontend mounted by FastAPI to its CDN. `vercel.json` sets the function region to Mumbai and the maximum function duration to 60 seconds.

## What you need

- A Vercel account on the free Hobby plan.
- A GitHub repository containing the contents of this `freshroute` folder. Vercel deploys from a connected Git provider; do not upload only the ZIP to Vercel.

Vercel Hobby includes usage limits (currently 1 million function invocations, 4 CPU-hours and 360 GB-hours for functions). The plan is for personal and non-commercial use. A hackathon demonstration is a non-commercial demo; if you plan to use the app commercially, select an appropriate paid plan. See [Hobby plan details](https://vercel.com/docs/plans/hobby) and [Vercel terms](https://vercel.com/legal/terms) before deploying.

## Deploy

1. Extract the deployment ZIP and create a GitHub repository. Upload the files **inside** the `freshroute` folder so `app.py`, `package.json`, `vercel.json` and `requirements.txt` appear at the repository root. Keep `.python-version` and the backend directory.
2. Sign in to Vercel and choose **Add New → Project**. Import the GitHub repository and select the Hobby plan.
3. Set the project root directory to the folder that contains `package.json` and `app.py` (the repository root if you uploaded the folder contents).
4. Keep the build settings from `vercel.json`. It runs `npm ci && npm run build`; Python dependencies are installed from the root `requirements.txt`.
5. Deploy, open the assigned URL, and check `/api/health`. Then load the sample, generate a plan, compare scenarios and review finances.

The first API request after a quiet period may take longer while the serverless function starts. Open the app and try the main flow shortly before judging. Static files are served through Vercel's CDN; API requests run as a FastAPI function. Vercel Hobby function time and request limits apply.

## Data and app limitations

- The bundled data is synthetic. Its sample planning time is 15 October 2026, noon IST; if presenting later, change planning time and the related batch and destination timestamps together.
- The planner is a bounded deterministic heuristic, not a certified optimizer. Financial values are estimates under the README assumptions.
- There is no account system or database. Scenario edits are request-scoped and are not shared across users or retained after reload unless exported.
- Do not enter personal or confidential data. For production use, add authentication, persistent storage, rate limits, monitoring and backups.
