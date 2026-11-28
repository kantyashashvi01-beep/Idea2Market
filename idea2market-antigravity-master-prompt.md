# MASTER PROMPT FOR ANTIGRAVITY: BUILD AND DEPLOY "IDEA2MARKET" FROM SCRATCH

Paste everything below this line into Antigravity as the first message to the agent.

---

## 0. ROLE AND MISSION

You are a senior full-stack engineer, AI engineer and DevOps engineer working as an autonomous coding agent. Build **Idea2market** from an empty folder to a deployed, working product, then document it.

**Idea2market in one sentence:** an AI-assisted planning tool where a non-engineer describes a hardware product idea in plain language and receives a structured, reviewable engineering plan: requirements, preliminary architecture, Bill of Materials (BOM) with cost *ranges*, prototype budget, roadmap, engineering risks, a rule-based DFM/readiness checklist, and a downloadable PDF report.

**Context:** this is an Open Innovation entry for the 13th Protocol: An AI Hackathon 2026, built by a student team. A working end-to-end demo matters more than a long feature list. Prefer simple, boring, reliable technology.

**Final deliverables (all required):**
1. A GitHub repository with clean history, README, CI and `.env.example` files.
2. A backend (FastAPI) deployed on **Render**.
3. A frontend (Next.js) deployed on **Netlify**.
4. A PostgreSQL database wired to the deployed backend, with migrations and seed data.
5. A smoke-test script that proves the deployed system works end to end.
6. Final report to me with live URLs, what works, what does not, and every manual step I must do.

---

## 1. HOW YOU MUST WORK (OPERATING RULES)

1. **Plan first.** Before writing code, produce an implementation plan and a task list as artifacts. **Stop and wait for my approval** of the plan.
2. **Work in phases** (Section 14). At the end of each phase: run the tests, summarise what you did, list anything blocked, and wait for my "continue" only at the checkpoints marked 🛑. Otherwise proceed.
3. **Never invent credentials, URLs or facts.** If you need an API key, a GitHub login, or a Render/Netlify authorisation, **ask me**, tell me exactly what to click or paste, and wait.
4. **Secrets:** never commit secrets, never print secret values in logs, chat, screenshots or artifacts. Use `.env` locally (git-ignored) and the Render/Netlify dashboards for production. Commit only `.env.example` with placeholder values.
5. **Verify, do not assume.** After every meaningful change, run it. Use the terminal for tests and the browser for UI checks (take screenshots as artifacts). For Render, Netlify and any library whose behaviour may have changed, **read the current official documentation** before configuring, and tell me if the docs differ from this prompt.
6. **Small, reviewable commits** using Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`).
7. **Ask before destructive actions** (deleting databases, force-pushing, dropping tables in a non-local database, deleting cloud services).
8. **Be honest in the product and in your reports.** Do not claim anything is verified, tested or deployed unless you actually ran it. If something fails, show the error and your diagnosis.
9. Keep dependencies minimal and pinned. Prefer the standard library and well-known packages.

---

## 2. PRODUCT RULES THAT MUST BE ENFORCED IN CODE (NON-NEGOTIABLE)

Idea2market produces **preliminary AI-generated drafts**, never engineering certification.

- Every generated report, page and PDF shows this notice: *"AI-generated preliminary draft. Not an engineering certification, not a quotation, and not a safety or regulatory approval. Have a qualified engineer review before building or selling anything."*
- **Closed-world BOM:** the BOM may only contain components that exist in the `components` table. The LLM proposes catalogue IDs; the code validates them. Unknown IDs are dropped and logged.
- **Deterministic arithmetic:** all cost totals are computed in Python from catalogue price ranges. The LLM never does arithmetic.
- **Ranges, not points:** costs are always `[low, high]` in INR with a "price checked on" date. Seed prices are **placeholders** and must be flagged `price_verified = false` and displayed in the UI as "unverified placeholder price".
- **Source labels:** every generated item carries `source_type` in `{catalogue, rule, retrieved_doc, model_estimate}`.
- **"Unknown" is allowed:** prompts must tell the model to answer `"unknown"` rather than guess.
- **Safety-critical blocklist:** if the idea falls in medical devices, automotive/road vehicles, high-voltage mains equipment, pressure vessels, explosives/weapons, regulated chemicals, or children's products, the report is still generated as a *discussion draft* but readiness status is forced to `"not assessed: requires qualified engineer"`, and a prominent warning appears.
- **No fake data:** no invented statistics, partnerships, certifications or supplier endorsements anywhere in the app or README.

---

## 3. TECH STACK (USE EXACTLY THIS UNLESS YOU TELL ME WHY NOT)

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router, TypeScript), Tailwind CSS |
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| ORM and migrations | SQLAlchemy 2.x, Alembic |
| Database | PostgreSQL (local via Docker; production per Section 8) |
| Auth | Email + password, Argon2 hashing (`argon2-cffi`), JWT access tokens (short-lived) |
| LLM | Provider-agnostic wrapper (Section 6). Models and keys come only from environment variables |
| PDF | ReportLab (pure Python, no system libraries) |
| Tests | pytest (backend), Vitest or Jest + Playwright (frontend smoke) |
| CI | GitHub Actions |
| Hosting | Render (backend), Netlify (frontend), Neon or Render Postgres (database) |

Do **not** add: a separate vector database, Redis, Celery, Kubernetes, or microservices. Semantic retrieval with `pgvector` is **optional** and only if time remains after everything else works; the default retrieval is filtered SQL over the catalogue.

---

## 4. REPOSITORY STRUCTURE

Create a monorepo named `idea2market`:

```
idea2market/
├── README.md
├── LICENSE                      # ask me which licence; default to MIT if I say "any"
├── .gitignore
├── .editorconfig
├── docker-compose.yml           # local Postgres only
├── render.yaml                  # Render Blueprint (backend)
├── .github/workflows/ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── API.md
│   ├── EVALUATION.md
│   └── DEMO_SCRIPT.md
├── backend/
│   ├── requirements.txt         # pinned
│   ├── requirements-dev.txt
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py            # pydantic-settings; all config from env
│   │   ├── db.py
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas (API + LLM stage outputs)
│   │   ├── api/                 # routers: auth, projects, jobs, bom, report, admin, facilities, health
│   │   ├── core/                # security, rate limiting, logging, errors
│   │   ├── llm/                 # provider wrapper + adapters
│   │   ├── pipeline/            # stages 1-9
│   │   ├── prompts/             # versioned prompt files (.md/.txt)
│   │   ├── rules/               # dfm_rules.yaml, readiness_rules.yaml, safety_blocklist.yaml
│   │   ├── services/            # cost engine, bom validator, pdf builder
│   │   └── seed/                # components.csv, facilities.csv, seed.py
│   └── tests/
├── eval/
│   ├── gold_set.jsonl           # 10-20 example ideas with reference expectations
│   └── run_eval.py              # scores outputs, writes eval/results.md
├── frontend/
│   ├── package.json
│   ├── netlify.toml
│   ├── .env.example
│   └── src/ ...
└── scripts/
    ├── smoke_test.py            # runs against a base URL
    └── dev.sh                   # starts db, backend, frontend locally
```

---

## 5. DATABASE DESIGN

PostgreSQL. Use Alembic for **every** schema change; never create tables by hand.

Tables (suggested names; keep foreign keys and indexes sensible):

- `users` (id UUID, email unique, password_hash, role in {user, reviewer, admin}, created_at)
- `projects` (id UUID, owner_id FK, title, idea_text, domain, status, safety_flag boolean, created_at, updated_at)
- `project_versions` (id, project_id FK, snapshot_json JSONB, model_name, prompt_version, created_at)
- `clarifications` (id, project_id FK, question, answer, position)
- `requirements` (id, project_id FK, kind {functional, constraint, assumption}, text, priority, source_type)
- `subsystems` (id, project_id FK, name, purpose, maps_to_requirement_ids JSONB)
- `interfaces` (id, project_id FK, from_subsystem_id, to_subsystem_id, description)
- `categories` (id, name)
- `components` (id, category_id FK, name, specs_json JSONB, typical_use, active boolean)
- `price_points` (id, component_id FK, low_inr, high_inr, checked_on date NULL, source_note, price_verified boolean default false)
- `bom_items` (id, project_id FK, component_id FK NOT NULL, quantity, role_in_design, confidence)
- `risks` (id, project_id FK, title, severity, reason NOT NULL, needs_expert boolean)
- `roadmap_stages` (id, project_id FK, position, title, deliverable, duration_note)
- `rules` (id, area, text, severity, version)
- `rule_findings` (id, project_id FK, rule_id FK, status, note)
- `reports` (id, project_id FK, version, file_path or blob, status {ai_draft, reviewed}, created_at)
- `jobs` (id UUID, project_id FK, status {queued, running, done, failed}, stage, progress_percent, error_message, created_at, finished_at)
- `facilities` (id, name, type, city, url, notes)  — static directory (see seed)

Rules:
- `bom_items.component_id` is NOT NULL with a foreign key (this enforces the closed-world rule).
- Free hosting has an **ephemeral filesystem**: store generated PDFs in the database (`bytea`) or regenerate on demand. Do not rely on local disk for persistence.
- Add a startup routine that marks any job left in `running` for more than 10 minutes as `failed` (Render free instances can restart at any time).

---

## 6. LLM LAYER AND PIPELINE

### 6.1 Provider wrapper

Create `app/llm/` with one interface:

```python
class LLMClient(Protocol):
    def generate_json(self, *, system: str, user: str, schema: type[BaseModel],
                      model_role: Literal["strong", "fast"]) -> BaseModel: ...
```

- Implement adapters for **Google Gemini** and **Anthropic**, chosen by `LLM_PROVIDER`. Add a `FakeLLMClient` that returns deterministic canned outputs for tests and CI (CI must never call a paid API).
- Models come from env vars (`LLM_MODEL_STRONG`, `LLM_MODEL_FAST`). **Do not hard-code model names.** Look up current model names in the provider's docs and put them in `.env.example` as examples, flagged "verify".
- Validate every response against the Pydantic schema. On validation failure, retry **once** with the validation error appended, then fail the stage with a clear error.
- Enforce a per-project token budget (`MAX_TOKENS_PER_PROJECT`) and a request timeout. Log model name, prompt version, latency and token counts. **Redact idea text from general logs.**

### 6.2 Pipeline stages (each stage = one module, one prompt file, one Pydantic schema)

| # | Stage | Input | Output | Guard |
|---|---|---|---|---|
| 1 | Clarify | idea text | up to 5 questions (JSON) | schema, max 5 |
| 2 | Requirements | idea + answers | requirements list with priorities and explicit assumptions | schema; required fields |
| 3 | Architecture | requirements | subsystems + interfaces | every subsystem maps to a requirement |
| 4 | Retrieve | subsystems | candidate catalogue rows | SQL only; catalogue rows only |
| 5 | BOM | candidates | BOM lines (catalogue IDs + quantities + role) | IDs must exist; quantity bounds |
| 6 | Cost | BOM | total range + allowance lines | pure Python, no LLM |
| 7 | Rules | requirements + BOM | DFM/readiness findings | YAML rule engine, versioned |
| 8 | Roadmap and risks | all above | stages + risks (each risk has `reason`) | schema |
| 9 | Report | all above | structured JSON + PDF | disclaimer block always present |

Cost engine: `total_low = Σ(qty × price_low)`, `total_high = Σ(qty × price_high)`, plus configurable allowances (tools/consumables, enclosure/fabrication, shipping/taxes, rework contingency) stored in config and **editable by the user in the UI**. Output label: "Order-of-magnitude estimate, not a quotation."

Rule engine (`app/rules/*.yaml`): simple declarative checks evaluated in Python, for example: number of unique custom parts, process vs expected volume, standard vs custom parts ratio, battery shipping/safety flag, RF module compliance flag, mains voltage flag, tolerance assumptions missing, single-source components. Each finding has `status` {pass, warn, fail, needs_expert}, `note`, and `rule_id`. Write at least 20 rules.

Prompts: one file per stage in `app/prompts/`, with a version string at the top (`# prompt_version: 1`). Every prompt must instruct the model to (a) state assumptions explicitly, (b) answer `"unknown"` instead of guessing, (c) output only JSON matching the schema, (d) never output prices or totals.

### 6.3 Jobs

`POST /projects/{id}/generate` creates a `jobs` row and runs the pipeline with FastAPI `BackgroundTasks`. Update `stage` and `progress_percent` after each stage. The client polls `GET /jobs/{id}`. Target: full report in under 90 seconds. If a stage fails, keep partial results and return an explanatory error.

---

## 7. API (REST, JSON, bearer-token auth)

All project endpoints are scoped to the authenticated owner. Return consistent error shapes `{ "error": { "code", "message" } }`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + DB check (used by Render health check) |
| POST | `/auth/register`, `/auth/login` | account, token |
| GET | `/auth/me` | current user |
| POST | `/projects` | create project with `idea_text` (length-limited) |
| GET | `/projects`, `/projects/{id}` | list, detail |
| POST | `/projects/{id}/clarify` | generate questions |
| POST | `/projects/{id}/answers` | save answers |
| POST | `/projects/{id}/generate` | start pipeline, returns `job_id` |
| GET | `/jobs/{job_id}` | status + progress |
| PATCH | `/projects/{id}/requirements/{rid}` | edit a requirement |
| GET / PATCH | `/projects/{id}/bom`, `/projects/{id}/bom/{item_id}` | view / edit BOM; recompute cost |
| PATCH | `/projects/{id}/allowances` | edit allowance percentages; recompute cost |
| GET | `/projects/{id}/risks`, `/projects/{id}/readiness` | risks, rule findings |
| POST / GET | `/projects/{id}/report` | build / download PDF |
| GET | `/facilities` | static facility directory |
| GET/POST/PATCH | `/admin/components`, `/admin/rules` | admin only |

Also: OpenAPI docs enabled at `/docs`; rate limiting on auth and generate endpoints (`slowapi`); request size limits; strict input validation; CORS driven by env (Section 9).

---

## 8. DATABASE CONFIGURATION: LOCAL AND PRODUCTION

**Local:** `docker-compose.yml` runs Postgres. `backend/.env.example` contains a local `DATABASE_URL`. Provide `make`/script commands: `db-up`, `migrate`, `seed`, `test`.

**Driver and URL format:** use SQLAlchemy with `psycopg` (v3). Normalise URLs so both `postgres://` and `postgresql://` from providers work (convert to `postgresql+psycopg://`). For cloud Postgres, require SSL (`sslmode=require`).

**Production database: ask me which option I want, and explain the trade-off:**

- **Option A (recommended): Neon free Postgres.** Persistent. Pass its connection string as `DATABASE_URL` in Render. Prefer the *pooled* connection string if offered.
- **Option B: Render Postgres (free).** Convenient with `render.yaml`, but according to Render's current docs a free Postgres database **expires 30 days after creation**, is limited to 1 GB, has no backups, and only one free database is allowed per workspace. Re-verify this in Render's docs before choosing it. If I pick this, tell me the expiry date and how to export a dump.
- Option C: Supabase Postgres (use only the Postgres connection string, not its other services).

**Migrations in production:** run `alembic upgrade head` as part of the start command (free Render services may not support pre-deploy commands; check current docs). Migrations must be idempotent and safe to run on every start. **Seeding** is a separate, explicit, idempotent command (`python -m app.seed.seed`) that I run once; do not auto-reseed on every start.

**Seed data:**
- `components.csv`: about 120 components for one narrow demo domain (a low-cost autonomous weeding/spraying rover for small farms): motors, motor drivers, microcontrollers/SBCs, GPS, IMU, camera, ultrasonic/LiDAR-class sensors, batteries and chargers, BMS, wiring, connectors, frame materials, wheels, enclosure parts, fasteners, solar option, pump/nozzle parts. Include category, key specs, typical use, and INR price ranges.
- **All prices are illustrative placeholders** you cannot verify. Set `price_verified = false`, `checked_on = NULL`, `source_note = "placeholder, verify before use"`. Never present them as real quotes.
- `facilities.csv`: a small static directory of publicly known prototyping and testing resources. Only include entries whose existence and official URL you have **verified by browsing**; include I-STEM (https://www.startupindia.gov.in/content/sih/en/i-stem.html) and T-Works (https://tworks.telangana.gov.in/). No endorsements, no invented details; each row has a `notes` field limited to what the official page says.

---

## 9. ENVIRONMENT VARIABLES AND CONFIGURATION

### Backend (`backend/.env.example`)

| Variable | Purpose |
|---|---|
| `ENV` | `local` / `production` |
| `DATABASE_URL` | Postgres connection string (secret) |
| `SECRET_KEY` | JWT signing key (secret; generate a long random value) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | token lifetime |
| `CORS_ORIGINS` | comma-separated allowed origins (local frontend + Netlify URL) |
| `LLM_PROVIDER` | `gemini` / `anthropic` / `fake` |
| `LLM_API_KEY` | provider key (secret) |
| `LLM_MODEL_STRONG`, `LLM_MODEL_FAST` | model names (verify against provider docs) |
| `MAX_TOKENS_PER_PROJECT` | spend cap |
| `ADMIN_EMAIL` | email that is granted admin on registration |
| `LOG_LEVEL` | logging level |

### Frontend (`frontend/.env.example`)

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | backend base URL (local: `http://localhost:8000`; prod: the Render URL) |

`NEXT_PUBLIC_*` variables are baked in at **build time**; after changing one on Netlify, trigger a new deploy. The app must fail loudly with a readable message if the variable is missing.

All config is read through `pydantic-settings`. The app must refuse to start in `production` if `SECRET_KEY` or `DATABASE_URL` is missing or still a placeholder.

---

## 10. FRONTEND (NEXT.JS + TAILWIND)

Screens:
1. **Landing / login / register.**
2. **New idea:** textarea with length limit and example prompt (the agricultural robot idea).
3. **Clarification:** show up to 5 questions, collect answers.
4. **Generation progress:** polls the job, shows stage names and a progress bar. Must handle the free-tier cold start (backend can take about a minute to wake): show a friendly "server is waking up" state with automatic retries and a timeout message. Do **not** add artificial keep-alive pinging to defeat the host's idle policy.
5. **Report page** with tabs: Requirements · Architecture (block diagram rendered from subsystem/interface JSON, SVG or Mermaid) · BOM and cost (ranges, source labels, "unverified placeholder price" badges, editable quantities and allowances with live recompute) · Roadmap · Risks (with "needs expert review" badges) · Readiness checklist · Facilities.
6. **Export:** download PDF.
7. **Admin** (admin role only): manage components and rules (simple tables).

Global: persistent banner with the Section 2 disclaimer; accessible colour contrast and keyboard navigation; responsive layout (works on a phone); loading and error states everywhere; no secrets in client code. Centralise API calls in one typed client module. Store the token safely (prefer in-memory plus refresh on reload via a short-lived token; if you use localStorage, tell me the trade-off).

---

## 11. GITHUB SETUP

1. `git init`, add `.gitignore` (Python, Node, `.env*` except `.env.example`, IDE files, build output).
2. Check whether the GitHub CLI is installed and authenticated (`gh auth status`). If not authenticated, **tell me to run `gh auth login`** and wait. Never ask me to paste a token into chat.
3. Ask me for: GitHub username/organisation, repo visibility (public/private), and the licence.
4. Create the repository `idea2market`, push `main`.
5. Branching: work on `feat/*` branches, merge via pull requests, keep `main` deployable. Enable (or tell me how to enable) branch protection requiring CI to pass.
6. **GitHub Actions `ci.yml`:** on push and PR: install backend deps, run lint (`ruff`) and `pytest` with `LLM_PROVIDER=fake` and a service Postgres container; install frontend deps, run lint, type-check and build. CI must not need any secret.
7. Add issue/PR templates and a `CONTRIBUTING.md` (short).

---

## 12. DEPLOYMENT

### 12.1 Backend on Render

- Create `render.yaml` (Blueprint) with a single **web service**: `runtime: python`, `rootDir: backend`, `plan: free`, build `pip install -r requirements.txt`, start `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`, `healthCheckPath: /health`, and env vars declared with `sync: false` for every secret (so values are entered in the dashboard, never stored in Git). Pin the Python version via the environment variable Render documents for this purpose.
- **Verify the Blueprint syntax and current free-tier behaviour in Render's official docs before finalising.** Known free-tier facts to design around (re-verify): the service spins down after about 15 minutes idle and takes roughly a minute to wake; the filesystem is ephemeral; outbound SMTP ports are blocked; instance hours are limited per month.
- Tell me exactly how to connect the repo: Render dashboard → New → Blueprint → select the GitHub repo → fill the secret env vars (`DATABASE_URL`, `SECRET_KEY`, `LLM_API_KEY`, `CORS_ORIGINS`, etc.) → Apply. Then wait for the deploy and report the service URL.
- After first deploy, run migrations (already in the start command) and tell me the one-time seed step (via Render Shell if available on the plan, or by running the seed script locally against the production `DATABASE_URL` that I provide through my own terminal, never pasted into chat).

### 12.2 Frontend on Netlify

- Create `frontend/netlify.toml` with the base directory and build command. Use Netlify's current Next.js support (it auto-detects Next.js); **check Netlify's docs** for the recommended configuration and any required plugin or adapter, and do not hard-code a publish directory unless the docs say to.
- Tell me exactly how to connect: Netlify → Add new site → Import from Git → GitHub → select `idea2market` → set base directory `frontend` → add `NEXT_PUBLIC_API_BASE_URL` pointing to the Render URL → deploy.
- After Netlify gives the site URL, **add it to the backend `CORS_ORIGINS`** in Render and redeploy the backend. Also allow `http://localhost:3000` for local development. (Optional: allow Netlify deploy-preview origins via a documented pattern; explain the security trade-off if you do.)

### 12.3 Order of operations

1. Local everything works.
2. Push to GitHub, CI green.
3. Provision the database (Section 8), get `DATABASE_URL` from me.
4. Deploy backend to Render; verify `/health` and `/docs`.
5. Run migrations and seed.
6. Deploy frontend to Netlify with the backend URL.
7. Update CORS with the Netlify URL; redeploy backend.
8. Run `scripts/smoke_test.py` against the live URLs.
9. Write `docs/DEPLOYMENT.md` documenting every step, every env var (names only), and rollback instructions.

---

## 13. TESTING, EVALUATION AND VERIFICATION

**Backend tests (pytest):** auth flow; project ownership isolation (user A cannot read user B's project); BOM validator drops unknown IDs; cost engine arithmetic with fixed fixtures; rule engine for at least 10 rules; safety blocklist forces the "not assessed" status; schema-validation retry logic; job stale-recovery; PDF contains the disclaimer text. Use `FakeLLMClient`.

**Evaluation (`eval/`):**
- Build `gold_set.jsonl` with 10 to 20 example product ideas in the rover domain plus 2 to 3 deliberately out-of-domain or safety-critical ideas. For each, record reference expectations (expected component categories, expected risks, expected flags) in a format a human mentor can review. **Mark clearly in the file that references were written by the AI agent and must be reviewed and corrected by a human mentor before being used for claims.**
- `run_eval.py` scores: schema validity rate, BOM resolvability (should be 100%), category coverage, risk coverage, safety-flag correctness, and cost-range sanity. Output `eval/results.md`. Do not claim accuracy numbers anywhere in the README unless they come from this script.

**Smoke test (`scripts/smoke_test.py <base_url>`):** register a user, create a project with the demo idea, answer clarifications, run generation, poll until done, fetch BOM/risks/readiness, download the PDF, assert the disclaimer is present. Exit non-zero on failure. Run it against local, then against production (using a throwaway test account).

**Browser verification:** drive the deployed Netlify site in the browser, complete the demo flow, and attach screenshots to your final artifact.

---

## 14. PHASES AND CHECKPOINTS

- **Phase 0, planning 🛑:** implementation plan, task list, risk list, questions for me (GitHub details, LLM provider and key availability, DB option, licence, demo domain confirmation). Wait for approval.
- **Phase 1, scaffolding:** repo, tooling, Docker Postgres, FastAPI skeleton with `/health`, Next.js skeleton, CI. Commit.
- **Phase 2, data layer:** models, Alembic migrations, seed data and scripts.
- **Phase 3, core backend:** auth, projects, LLM wrapper with fake client, pipeline stages 1 to 9, cost engine, rules engine, jobs, PDF. Tests green.
- **Phase 4, frontend:** all screens wired to the API, cold-start handling, report tabs, PDF download, admin screens.
- **Phase 5, evaluation:** gold set, eval script, results file. 🛑 Show me results and wait.
- **Phase 6, GitHub:** create repo, push, CI green. 🛑 Confirm before making the repo public.
- **Phase 7, deployment:** database, Render, Netlify, CORS, seed, smoke test. 🛑 Pause at each point where I must authorise or paste something.
- **Phase 8, documentation and handover:** README (what it is, honest limits, setup, deploy, architecture diagram, demo script, evaluation summary), `docs/*`, final report.

---

## 15. DEFINITION OF DONE (CHECK EVERY ITEM AND REPORT ON EACH)

- [ ] Local stack starts with one script; tests pass; CI passes on GitHub.
- [ ] Demo idea ("an affordable autonomous agricultural robot for small Indian farmers") produces all outputs: requirements, architecture diagram, BOM with ranges and placeholder-price badges, budget, roadmap, risks, readiness checklist, PDF.
- [ ] Every BOM row resolves to a catalogue row; no LLM arithmetic anywhere.
- [ ] Disclaimer appears in UI and PDF; safety-critical test idea triggers the warning.
- [ ] No secrets in Git history (run a secrets scan, for example `gitleaks`, and report the result).
- [ ] Backend live on Render, `/health` OK, `/docs` reachable.
- [ ] Frontend live on Netlify and talking to the Render backend with no CORS errors.
- [ ] Production database migrated and seeded.
- [ ] `scripts/smoke_test.py` passes against production.
- [ ] README and `docs/DEPLOYMENT.md` let a new developer reproduce the deployment.
- [ ] A final report listing: live URLs, repo URL, what is implemented, what is **not** implemented, known issues, free-tier limitations I should know about (cold start, database expiry if Render Postgres was chosen), and the exact manual steps still required from me.

---

## 16. OUT OF SCOPE (DO NOT BUILD)

Crowdfunding, pre-orders or any payment handling; manufacturer or investor marketplaces; lab-testing coordination; CAD file analysis or text-to-CAD; "verified" or "certified" badges; any claim that Idea2market guarantees safety, manufacturability or accuracy. Mention these only as "future scope" in the README.

---

## 17. START NOW

Begin with **Phase 0**. Produce the implementation plan and task list as artifacts, list your questions to me (GitHub username and visibility, licence, LLM provider and whether I have an API key, database option A/B/C, and any change to the demo domain), and **wait for my approval before writing code**.
