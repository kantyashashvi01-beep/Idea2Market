# Contributing to Idea2market

Thank you for contributing to Idea2market!

## Development Guidelines

1. **Architecture & Product Rules**:
   - Every user-facing document, report, and UI must display the preliminary AI-generated disclaimer.
   - Closed-world BOM: only catalogue components are allowed in BOM rows.
   - Deterministic arithmetic: all cost computations must occur in Python code.
   - Safety-critical categories must trigger the safety warning and disable "ready" status.

2. **Branching & Commits**:
   - Use feature branches (`feat/name`, `fix/issue`).
   - Follow Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`.
   - Ensure all backend unit tests (`pytest`) and frontend linting/typechecking pass before submitting PRs.

3. **Running Locally**:
   - Start database: `docker compose up -d`
   - Start backend: `cd backend && uvicorn app.main:app --reload`
   - Start frontend: `cd frontend && npm run dev`
