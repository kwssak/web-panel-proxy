# web/tariffs_api.py
from flask import Blueprint, request, jsonify
from core.db_manager import add_tariff, get_active_tariffs

tariffs_bp = Blueprint('tariffs', __name__, url_prefix='/api/tariffs')

@tariffs_bp.route('/', methods=['GET'])
def api_get_tariffs():
    return jsonify(get_active_tariffs())

@tariffs_bp.route('/', methods=['POST'])
def api_add_tariff():
    data = request.json
    try:
        tariff_id = add_tariff(
            name=data['name'],
            price=float(data['price']),
            duration_days=int(data['duration_days']),
            traffic_limit_gb=float(data['traffic_limit_gb'])
        )
        return jsonify({"success": True, "id": tariff_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
