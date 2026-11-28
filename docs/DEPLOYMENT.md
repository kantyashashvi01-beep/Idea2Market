# Idea2market: Production Deployment Guide

This guide describes how to deploy the Idea2market monorepo with:
- **Backend on Render** (FastAPI, Python 3.12)
- **Frontend on Netlify** (Next.js 14 App Router, TypeScript, Tailwind)
- **PostgreSQL Database** (Neon Free Postgres or Render Postgres)

---

## 1. Database Provisioning (Neon Free Postgres Recommended)

1. Create a free PostgreSQL database on [Neon.tech](https://neon.tech) (or Render / Supabase).
2. Copy the connection string. Neon provides a pooled connection string:
   `postgresql://user:password@ep-xyz-pooler.region.aws.neon.tech/neondb?sslmode=require`
3. Note: If using Render Free Postgres, note that free Render databases automatically expire and are deleted after 30 days.

---

## 2. Backend Deployment on Render

1. Log into your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** &rarr; **Blueprint**.
3. Connect your GitHub repository: `https://github.com/kantyashashvi01-beep/Idea2Market`.
4. Render will read `render.yaml` and configure the web service:
   - **Runtime**: Python 3.12
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
5. Fill in the required environment variables in Render Dashboard:
   - `DATABASE_URL`: Your production PostgreSQL connection string
   - `SECRET_KEY`: A secure random 64-character secret string
   - `LLM_PROVIDER`: `gemini` (or `anthropic`)
   - `LLM_API_KEY`: Your provider API key
   - `LLM_MODEL_STRONG`: `gemini-2.5-pro` (or `claude-3-5-sonnet-20241022`)
   - `LLM_MODEL_FAST`: `gemini-2.5-flash` (or `claude-3-5-haiku-20241022`)
   - `CORS_ORIGINS`: Temporary placeholder: `http://localhost:3000` (will be updated once Netlify URL is assigned)
   - `ADMIN_EMAIL`: Your administrator email
6. Click **Apply**.
7. Once deployed, verify `/health` and `/docs` on your Render URL:
   `https://<your-render-service>.onrender.com/health`

---

## 3. Database Seeding (One-Time Execution)

The database tables are automatically created on startup via `alembic upgrade head`.
To populate the curated ~120 components and facilities:

Option A: Run from your local terminal with the production connection string:
```bash
cd backend
DATABASE_URL="postgresql+psycopg://..." python -m app.seed.seed
```

Option B: In the Render Dashboard, open the **Shell** tab on your backend service:
```bash
python -m app.seed.seed
```

---

## 4. Frontend Deployment on Netlify

1. Log into your [Netlify Dashboard](https://app.netlify.com).
2. Click **Add new site** &rarr; **Import an existing project** &rarr; **GitHub**.
3. Select `kantyashashvi01-beep/Idea2Market`.
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `.next` (or leave default Netlify auto-detect)
5. Add the Environment Variable:
   - `NEXT_PUBLIC_API_BASE_URL`: `https://<your-render-service>.onrender.com`
6. Click **Deploy Site**.
7. Copy your Netlify site URL (e.g., `https://idea2market-demo.netlify.app`).

---

## 5. Update CORS in Render

1. Go back to Render Dashboard &rarr; `idea2market-backend` &rarr; **Environment**.
2. Update `CORS_ORIGINS`:
   `http://localhost:3000,https://<your-netlify-site>.netlify.app`
3. Click **Save Changes** (Render will trigger a quick redeploy).

---

## 6. End-to-End Smoke Test Verification

Run the automated smoke test script against your live deployment:

```bash
python scripts/smoke_test.py https://<your-render-service>.onrender.com
```

The script verifies user registration, project creation, clarification Q&A, pipeline execution, closed-world BOM resolution, and PDF report download.
