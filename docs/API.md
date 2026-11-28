# Idea2market: REST API Documentation

The Idea2market API is built with FastAPI, using JSON payloads, OpenAPI schema documentation, and Bearer token authentication.

Base URL (Local): `http://localhost:8000`
Interactive Documentation: `http://localhost:8000/docs`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Register a new creator account.
- **Request Body**:
  ```json
  {
    "email": "creator@example.com",
    "password": "strongPassword123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user_id": "uuid",
    "email": "creator@example.com",
    "role": "user"
  }
  ```

### `POST /auth/login`
Authenticate with email and password.
- **Request Body**:
  ```json
  {
    "email": "creator@example.com",
    "password": "strongPassword123"
  }
  ```

### `GET /auth/me`
Retrieve profile of authenticated user. Requires `Authorization: Bearer <token>`.

---

## 2. Project Planning Endpoints

### `POST /projects`
Create a new hardware project draft.
- **Request Body**:
  ```json
  {
    "title": "Autonomous Agri Weeding Rover",
    "idea_text": "An autonomous agricultural robot for small Indian farmers...",
    "domain": "agricultural_robotics"
  }
  ```

### `GET /projects`
List projects owned by authenticated user.

### `GET /projects/{id}`
Retrieve full detail of a project including requirements, architecture subsystems, BOM, risks, roadmap, and rule findings.

### `POST /projects/{id}/clarify`
Generate up to 5 technical clarifying questions.

### `POST /projects/{id}/answers`
Record creator answers to clarifying questions.

### `POST /projects/{id}/generate`
Enqueue background generation pipeline. Returns `{"job_id": "uuid", "status": "queued"}`.

### `GET /jobs/{job_id}`
Poll pipeline execution progress (`stage`, `progress_percent`, `status`).

### `PATCH /projects/{id}/bom/{item_id}`
Update item quantity or replace component with another valid catalogue ID. Triggers automatic deterministic cost recalculation.

### `PATCH /projects/{id}/allowances`
Update percentage values for budget allowances (contingency, fabrication, shipping). Recomputes total budget.

### `GET /projects/{id}/report`
Download preliminary PDF engineering report. Returns `application/pdf`.

---

## 3. Public Directory

### `GET /facilities`
List verified Indian prototyping and testing infrastructure (I-STEM, T-Works).
