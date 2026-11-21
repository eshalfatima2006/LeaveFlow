# LeaveFlow — Baseline Verification Report

## 1. Project Information

**Course:** SE3002 — Software Quality Engineering  
**Project:** Automated Testing of LeaveFlow Management Information System  
**Upstream Repository:** https://github.com/cmdr-chara/LeaveFlow  
**Team Repository:** https://github.com/eshalfatima2006/LeaveFlow  
**Baseline Commit:** `bada9a03ecec53ef6945827230e3594d825da87a`  
**Baseline Date:** 21 November 2026  
**Environment:** Windows with WSL Ubuntu

## 2. Objective

The purpose of baseline verification is to confirm that the original LeaveFlow application can be installed, initialized and executed locally before the team begins implementing its independent software quality engineering tests.

This baseline provides a reproducible reference for later testing, defect identification, code changes and regression analysis.

## 3. Development Environment

| Component | Version / Configuration |
|---|---|
| Python | 3.12.7 |
| Git | 2.53.0 |
| Node.js | 22.23.3 |
| npm | 10.9.9 |
| Django | 6.0.7 |
| Django REST Framework | 3.17.1 |
| Database | SQLite, local development |
| Python environment | `.venv` |
| Backend address | `http://127.0.0.1:8000` |

## 4. Repository and Version Control

The original LeaveFlow repository was cloned into WSL Ubuntu.

A team-owned GitHub fork was configured as `origin`, while the developer's repository was configured as `upstream`.

The exact audited baseline commit was verified using `git rev-parse HEAD`.

The project uses feature branches for changes and a protected `main` branch for reviewed work.

## 5. Backend Installation and Initialization

The following commands were executed successfully:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python backend/manage.py check
python backend/manage.py migrate
python backend/manage.py seed_demo
```

**Observed results:**

- Python dependencies installed successfully.
- Django system check completed with zero reported issues.
- Database migrations completed successfully.
- Demo data was initialized.
- Local demonstration accounts were created.

## 6. Original Test Suite

**Command:**

```bash
python backend/manage.py test leave
```

**Observed result:**

- Tests discovered: 9
- Tests executed: 9
- Failures: 0
- Errors: 0
- Final status: PASS

The original test suite was executed successfully more than once.

These are upstream tests and are not claimed as the team's independently developed tests.

## 7. Backend and API Verification

The Django development server started successfully at `http://127.0.0.1:8000`.

The observed server logs included:

| Operation | HTTP result | Observation |
|---|---|---|
| Login | 200 | Successful authentication response |
| Retrieve dashboard | 200 | Dashboard endpoint returned successfully |
| Retrieve leave requests | 200 | Leave request data returned |
| Retrieve team | 200 | Team data returned |
| Create leave request | 201 | Request creation accepted |
| Process leave decision | 200 | Decision endpoint accepted the request |
| Invalid leave request | 400 | Request rejected by server |
| Current-user lookup before authentication | 401 | Unauthorized request rejected |

The server logs demonstrate successful API interactions. Detailed database assertions and full browser-flow verification will be captured separately during team-owned integration and E2E testing.

## 8. Selected Workflows

**Workflow 1 — Employee Leave Request**

An authenticated employee submits a leave application, subject to the application's validation and eligibility rules.

**Workflow 2 — Manager Leave Decision**

An authorized manager approves or rejects a pending leave application. Both workflows operate on the same persisted `LeaveRequest` record.

## 9. Known Baseline Risks

The repository feasibility audit previously identified:

1. A potential approval-time leave-balance integrity defect.
2. Incomplete OpenAPI request/response schemas.
3. A need to verify full deterministic database reset.
4. A need to verify the complete frontend browser workflow.

These findings remain subject to independent reproduction and verification by the project team.

## 10. Baseline Conclusion

The initial local backend setup was successful. Dependency installation, Django checks, database migrations, demo data initialization and all nine upstream backend tests completed without reported failures.

The API logs also confirm successful authentication, leave-request creation and leave-decision operations.

The frontend production build, complete browser-flow assertions and database reset procedure require additional documented verification before the full baseline is considered complete.

**Baseline status: BACKEND VERIFIED — FULL BASELINE IN PROGRESS.**

## 11. Evidence References

- `evidence/baseline/environment.txt`
- `evidence/baseline/django-check.log`
- `evidence/baseline/migrations.log`
- `evidence/baseline/upstream-tests.log`

Additional frontend and E2E evidence will be added after execution.
 ## 12. Browser Screenshots

The following screenshots document the locally running LeaveFlow application using synthetic demonstration accounts.

| Evidence | Description | File |
|---|---|---|
| BL-UI-01 | Employee dashboard displaying leave information | `evidence/baseline/screenshots/01-employee-dashboard.png` |
| BL-UI-02 | Employee leave request form | `evidence/baseline/screenshots/02-leave-request-form.png` |
| BL-UI-03 | Manager dashboard showing pending requests | `evidence/baseline/screenshots/03-manager-dashboard.png` |
| BL-UI-04 | Manager's decision result for a leave request | `evidence/baseline/screenshots/04-manager-decision.png` |

These screenshots provide preliminary browser evidence. Full automated assertions and persisted database verification will be performed separately during the team's Playwright and integration testing phases.