# CareerTrack

## Student Placement and Internship Management System

CareerTrack is a college DBMS project for managing student placement activities. Students can maintain basic profile details, review openings, apply, and follow application updates. Recruiters can post openings and review applications. Placement staff can view summary metrics and export a CSV report.

The application uses a Flask API, a React and TypeScript frontend, and a MySQL database.

## Features

| Role | Main actions |
| --- | --- |
| Student | Register or sign in, view the dashboard, update phone and resume URL, browse openings, check academic eligibility, apply, track status, and view interviews. |
| Recruiter | Post openings, review applicants for the recruiter's company, change application status, and schedule interviews. |
| Placement admin | View placement metrics, student and company information, database status, and download the CSV report. |

Eligibility checks use the opening status and deadline, CGPA, graduation year, department restrictions, and whether the student has already applied. Listed skills are shown with the opening; the current eligibility service reports skill matches but does not use them to block applications.

The MySQL schema contains 13 tables for users, students, recruiters, companies, departments, skills, opportunities, applications, application history, and interviews.

## Technology

- Frontend: React, TypeScript, Vite
- Backend: Python, Flask, Flask-SQLAlchemy
- Database: MySQL 8
- Backend tests: pytest with an in-memory SQLite database

## Free hosted college demo

Use Render for the React frontend and Flask API, with Aiven Free for MySQL. Render runs the frontend and API on free plans; Aiven Free currently provides a 1 GB MySQL service with no card required. Aiven may power a free database off after extended inactivity, and free Render web services sleep while idle, so allow time for both to wake before presenting.

The root `render.yaml` deploys the two Render services and prompts for the Aiven connection settings. Create an Aiven MySQL service, then create an empty database named `careertrack_db`. Download its project CA certificate. In MySQL Workbench, connect to Aiven using its host, port, user, password, and CA certificate with TLS verification enabled. Run `database/02_schema.sql`, then `database/03_seed_data.sql` against the new `careertrack_db`. Do not run `database/01_init_db_and_user.sql` on Aiven; it is for creating a local MySQL user.

In Render, choose **New → Blueprint**, connect `chittiboyanajahnavi-crypto/carrertrack` on `main`, and deploy the root `render.yaml`. Enter the Aiven host, port, username, password, and CA certificate for `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_SSL_CA` when prompted. Render generates the Flask session secret. Keep all credentials in Render, not in GitHub. The backend uses the CA certificate to verify encrypted MySQL connections.

This initializes Aiven from the repository's schema and demo seed scripts; it does not copy changes that exist only in your local database. Your local MySQL remains unchanged. After both services deploy, check the API at `/api/health` and open the frontend.
## Run locally on Windows

You will need Python 3.11 or later, Node.js with npm, and MySQL 8.

### 1. Set up the database

If `careertrack_db` already exists and contains data you need, **skip the SQL initialization scripts**.

For a new local database, open the scripts in MySQL Workbench and run them in order:

1. `database/01_init_db_and_user.sql`
2. `database/02_schema.sql`
3. `database/03_seed_data.sql`

Before running the first script, set a local database-user password in it. Use the same password in `backend/.env`. The schema script drops and recreates the project tables, so do not run it against a database you need to keep.

### 2. Configure and start Flask

Open PowerShell at the project folder:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

If `backend/.env` already exists, keep it and edit it instead of copying over it. Set `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME` to match your MySQL setup. Set `SECRET_KEY` to a random local value. Keep `.env` private; Git ignores it.

Start the API in this PowerShell window:

```powershell
python run.py
```

The API runs on `http://127.0.0.1:5000` by default.

### 3. Configure and start React

Open a second PowerShell window at the project folder:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Vite forwards `/api` requests to the Flask server on port 5000.

For the seeded demo roles, use the role buttons in the top banner, then enter the corresponding demo password documented in `database/03_seed_data.sql`. Selecting a role does not sign in automatically. Student registration is also available from the sign-in dialog.

## Run checks

From `frontend`:

```powershell
npm run build
npm run lint
```

From `backend` with its virtual environment activated:

```powershell
python -m pytest -q
```

The tests use SQLite in memory. They do not check connectivity to your local MySQL server; an admin can check the configured connection and table counts on the **Database Health** page after signing in.

## Project layout

```text
backend/    Flask routes, models, services, and tests
database/  MySQL setup, schema, and sample data
frontend/   React application and Vite configuration
```
