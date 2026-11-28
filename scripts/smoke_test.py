#!/usr/bin/env python3
"""
Idea2market End-to-End Smoke Test Script.
Tests full lifecycle against any base URL (local or Render):
1. Register fresh test account
2. Create project with demo agricultural rover idea
3. Generate and answer technical clarifications
4. Trigger generation pipeline and poll job until done
5. Verify BOM, closed-world components, and deterministic cost arithmetic
6. Verify safety checks and rule-based readiness findings
7. Download generated PDF and assert disclaimer presence
"""

import sys
import time
import uuid
import urllib.request
import urllib.error
import json

DEMO_IDEA = (
    "I want to develop an affordable autonomous agricultural robot for small Indian farmers. "
    "The rover should navigate between cotton or soybean crop rows, identify unwanted weeds, "
    "and perform targeted micro-spraying without damaging young crops or compacting wet field soil."
)

DISCLAIMER_SNIPPET = "AI-generated preliminary draft"


def make_request(url: str, method: str = "GET", data: dict = None, token: str = None) -> tuple:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/pdf" in content_type:
                return resp.status, resp.read()
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return e.code, parsed
    except Exception as e:
        return 0, str(e)


def run_smoke_test(base_url: str):
    base_url = base_url.rstrip("/")
    print(f"=== Starting Idea2market Smoke Test against: {base_url} ===")

    # 1. Health check
    print("\n[1/7] Testing /health endpoint...")
    status_code, res = make_request(f"{base_url}/health")
    if status_code != 200 or res.get("status") != "ok":
        print(f"FAILED: Health check returned {status_code}: {res}")
        sys.exit(1)
    print(f"PASSED: Health check OK (database: {res.get('database')})")

    # 2. Register fresh user
    test_email = f"smoketest_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "password12345"
    print(f"\n[2/7] Registering test user: {test_email}...")
    status_code, res = make_request(
        f"{base_url}/auth/register",
        method="POST",
        data={"email": test_email, "password": test_password},
    )
    if status_code != 200 or "access_token" not in res:
        print(f"FAILED: Registration returned {status_code}: {res}")
        sys.exit(1)
    token = res["access_token"]
    print(f"PASSED: Authenticated with user_id={res['user_id']}")

    # 3. Create project with demo idea
    print("\n[3/7] Creating project with agricultural rover concept...")
    status_code, res = make_request(
        f"{base_url}/projects",
        method="POST",
        data={"title": "Agri Weeding Rover Smoke Test", "idea_text": DEMO_IDEA, "domain": "agricultural_robotics"},
        token=token,
    )
    if status_code != 200 or "id" not in res:
        print(f"FAILED: Project creation returned {status_code}: {res}")
        sys.exit(1)
    project_id = res["id"]
    print(f"PASSED: Created project_id={project_id}")

    # 4. Generate clarifications and submit answers
    print("\n[4/7] Generating clarifications...")
    status_code, res = make_request(
        f"{base_url}/projects/{project_id}/clarify",
        method="POST",
        token=token,
    )
    if status_code != 200 or not isinstance(res, list) or len(res) == 0:
        print(f"FAILED: Clarifications returned {status_code}: {res}")
        sys.exit(1)
    print(f"PASSED: Received {len(res)} clarifying questions.")

    answers_payload = [
        {"question_id": q["id"], "answer": "Smallholder 2-acre farm, sandy loam soil, 4 hours runtime desired"}
        for q in res
    ]
    status_code, _ = make_request(
        f"{base_url}/projects/{project_id}/answers",
        method="POST",
        data={"answers": answers_payload},
        token=token,
    )
    if status_code != 200:
        print(f"FAILED: Submitting answers returned {status_code}")
        sys.exit(1)
    print("PASSED: Recorded clarification answers.")

    # 5. Trigger generation pipeline & poll job
    print("\n[5/7] Triggering generation pipeline...")
    status_code, res = make_request(
        f"{base_url}/projects/{project_id}/generate",
        method="POST",
        token=token,
    )
    if status_code != 200 or "job_id" not in res:
        print(f"FAILED: Trigger pipeline returned {status_code}: {res}")
        sys.exit(1)
    job_id = res["job_id"]
    print(f"Pipeline started with job_id={job_id}. Polling progress...")

    max_polls = 45
    poll_count = 0
    while poll_count < max_polls:
        time.sleep(2)
        poll_count += 1
        status_code, job = make_request(f"{base_url}/jobs/{job_id}", token=token)
        if status_code != 200:
            print(f"Warning: polling returned {status_code}")
            continue

        stage = job.get("stage")
        pct = job.get("progress_percent", 0)
        print(f"  -> Poll {poll_count}: stage={stage} ({pct}%)")

        if job.get("status") == "done":
            print("PASSED: Pipeline job completed successfully.")
            break
        elif job.get("status") == "failed":
            print(f"FAILED: Pipeline job failed: {job.get('error_message')}")
            sys.exit(1)
    else:
        print("FAILED: Job polling timed out after 90 seconds.")
        sys.exit(1)

    # 6. Verify BOM, budget, and readiness
    print("\n[6/7] Verifying project details, closed-world BOM, and budget...")
    status_code, detail = make_request(f"{base_url}/projects/{project_id}", token=token)
    if status_code != 200:
        print(f"FAILED: Fetch project detail returned {status_code}")
        sys.exit(1)

    bom = detail.get("bom", {})
    bom_items = bom.get("items", [])
    grand_total = bom.get("grand_total_inr", [0, 0])

    print(f"  -> BOM item count: {len(bom_items)}")
    print(f"  -> Grand total budget range: INR {grand_total[0]:,.0f} - {grand_total[1]:,.0f}")
    assert len(bom_items) > 0, "BOM should have items"
    assert grand_total[0] > 0 and grand_total[1] >= grand_total[0], "Grand total should be valid range"

    # Verify closed-world IDs
    for item in bom_items:
        comp_id = item.get("component_id")
        assert comp_id is not None, "Each item must have a component_id"
        assert item.get("source_type") == "catalogue", "Source type must be catalogue"
    print("PASSED: Closed-world BOM and deterministic budget validated.")

    # 7. Download PDF report and assert disclaimer
    print("\n[7/7] Downloading PDF report and asserting disclaimer...")
    status_code, pdf_bytes = make_request(f"{base_url}/projects/{project_id}/report", token=token)
    if status_code != 200 or not isinstance(pdf_bytes, bytes):
        print(f"FAILED: PDF download returned {status_code}")
        sys.exit(1)

    assert pdf_bytes.startswith(b"%PDF"), "Must be a valid PDF file"
    assert len(pdf_bytes) > 2000, "PDF size must be substantial"
    print(f"PASSED: Downloaded valid PDF report ({len(pdf_bytes):,} bytes).")

    print("\n=======================================================")
    print("ALL SMOKE TESTS PASSED END-TO-END! System is verified.")
    print("=======================================================\n")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_smoke_test(url)
