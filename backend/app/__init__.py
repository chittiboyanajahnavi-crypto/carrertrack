import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, migrate, cors


def create_app(config_name=None):
    """Application factory for CareerTrack backend."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS for frontend origin with credentials enabled (for cookie sessions)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get('FRONTEND_URL', 'http://localhost:5173')}},
        supports_credentials=True,
    )

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.student_routes import student_bp
    from app.routes.company_routes import company_bp
    from app.routes.opportunity_routes import opportunity_bp
    from app.routes.application_routes import application_bp
    from app.routes.interview_routes import interview_bp
    from app.routes.report_routes import report_bp
    from app.routes.skill_routes import skill_bp
    from app.routes.department_routes import department_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(opportunity_bp)
    app.register_blueprint(application_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(department_bp)

    # Health check routes
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = "unknown"
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"disconnected: {str(e)}"

        return jsonify({
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'app': 'CareerTrack - Student Placement & Internship Management System',
            'version': '1.0.0',
            'database': db_status,
        }), (200 if db_status == 'connected' else 503)

    @app.route('/api/status', methods=['GET'])
    @app.route('/api/health/status', methods=['GET'])
    def system_status():
        """Detailed system and database connectivity status."""
        from datetime import datetime
        from sqlalchemy import inspect, text

        db_connected = False
        db_details = {
            'status': 'disconnected',
            'dialect': db.engine.name,
            'tables_count': 0,
            'table_counts': {},
        }

        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_connected = True
                db_details['status'] = 'connected'

                # Inspect tables if connected
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                db_details['tables_count'] = len(table_names)

                # Fetch counts for primary tables
                for tbl in ['users', 'students', 'companies', 'opportunities', 'applications']:
                    if tbl in table_names:
                        try:
                            cnt = conn.execute(text(f"SELECT COUNT(*) FROM `{tbl}`")).scalar()
                            db_details['table_counts'][tbl] = cnt
                        except Exception:
                            pass
        except Exception as e:
            db_details['error'] = str(e)

        overall_status = 'healthy' if db_connected else 'degraded'
        status_code = 200 if db_connected else 503

        return jsonify({
            'status': overall_status,
            'app': 'CareerTrack - Student Placement & Internship Management System',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_details,
        }), status_code

    return app
