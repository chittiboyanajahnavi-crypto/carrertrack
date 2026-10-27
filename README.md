# CareerTrack

CareerTrack is a Flask + MySQL placement management API with a React, TypeScript, and Vite frontend. It supports student, recruiter, and placement-admin workflows.

## Windows setup

Requirements: Python 3.11+, Node.js, npm, and MySQL 8.

1. If `careertrack_db` already exists, keep it and skip database initialization. For a new installation only, review `database/01_init_db_and_user.sql`, then run it from the repository root in PowerShell:

   ```powershell
   mysql -u root -p < database/01_init_db_and_user.sql
   mysql -u careertrack_user -p careertrack_db < database/02_schema.sql
   mysql -u careertrack_user -p careertrack_db < database/03_seed_data.sql
   ```

   **Caution:** `02_schema.sql` drops and recreates the project tables. Back up first; never run it against an existing database whose data you need to preserve. `03_seed_data.sql` contains sample accounts and records.

2. Create `backend/.env` (it is ignored by Git) with your local MySQL settings. Do not commit it:

   ```dotenv
   SECRET_KEY=<long-random-session-key>
   DB_USER=careertrack_user
   DB_PASSWORD=<your-mysql-user-password>
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=careertrack_db
   ```

3. Start the backend in one PowerShell window:

   ```powershell
   cd backend
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python run.py
   ```

4. Start the frontend in a second PowerShell window:

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

   Open <http://localhost:5173>. Vite proxies `/api` requests to `http://127.0.0.1:5000`.

## Main features

- Student dashboard, profile contact/resume updates, eligibility-aware opportunities, applications, and interviews.
- Recruiter opportunity posting, applicant pipeline, status changes, and interview scheduling.
- Placement-admin metrics, student/company views, MySQL health, and CSV report export.
- Email/password login, student registration, and role selectors for the seeded demo accounts. Role selection does not authenticate by itself; enter the seeded account password from the seed-data instructions. Seeded demo sessions return to guest mode on reload so they are never silently reused.
- The seeded student account is presented in the UI as **Jahnavi Chittiboyana**. Existing database rows are not changed by code updates; the updated display name applies when seeding a new database, and the frontend aliases the existing seeded account for display.

## Checks

```powershell
cd frontend
npm run build
npm run lint
cd ..
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Backend tests use an in-memory SQLite database; the system status endpoint reports connectivity to the configured MySQL instance.
