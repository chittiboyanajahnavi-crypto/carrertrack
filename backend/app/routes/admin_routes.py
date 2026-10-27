from flask import Blueprint
from app.services.metrics_service import MetricsService
from app.utils.responses import success_response
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/metrics', methods=['GET'])
@role_required(['admin'])
def get_metrics():
    """Retrieve full executive KPI metrics, distributions, and trends."""
    data = MetricsService.get_admin_metrics()
    return success_response(data=data)
