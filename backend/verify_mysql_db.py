"""
Verification script for CareerTrack MySQL Database connectivity.
Usage: backend/venv/Scripts/python.exe backend/verify_mysql_db.py
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from sqlalchemy import inspect, text


def verify_connection():
    app = create_app('development')
    with app.app_context():
        print("=" * 60)
        print("CareerTrack - MySQL Database Connectivity Verification")
        print("=" * 60)
        
        # Test basic connection
        try:
            result = db.session.execute(text("SELECT VERSION() AS ver, DATABASE() AS current_db")).fetchone()
            print(f"[OK] Connected to MySQL Server successfully!")
            print(f"     MySQL Version: {result[0]}")
            print(f"     Active Database: {result[1]}")
        except Exception as e:
            print(f"[FAILED] Could not connect to MySQL: {e}")
            print("\nPlease check that:")
            print("1. 'careertrack_db' and 'careertrack_user' have been created.")
            print("2. You copied backend/.env.example to backend/.env and filled in DB_PASSWORD.")
            return False

        # Inspect tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        expected_tables = [
            'departments', 'users', 'students', 'companies', 'recruiters',
            'skills', 'student_skills', 'opportunities', 'opportunity_skills',
            'opportunity_departments', 'applications', 'application_status_history', 'interviews'
        ]
        
        print("\nTable Verification:")
        all_present = True
        for t in expected_tables:
            if t in tables:
                print(f"  [FOUND] {t}")
            else:
                print(f"  [MISSING] {t}")
                all_present = False

        if all_present:
            print("\n[SUCCESS] All 13 relational tables are verified in MySQL!")
            
            # Count records and check constraints
            print("\nRecord Counts & Constraints:")
            for t in expected_tables:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
                fks = len(inspector.get_foreign_keys(t))
                indexes = len(inspector.get_indexes(t))
                uniques = len(inspector.get_unique_constraints(t))
                print(f"  - {t}: {count} records | FKs: {fks} | Indexes: {indexes} | Uniques: {uniques}")
        else:
            print("\n[WARNING] Some tables are missing. Run database/02_schema.sql and database/03_seed_data.sql.")
            
        print("=" * 60)
        return all_present


if __name__ == '__main__':
    verify_connection()
