# web/tariffs_api.py
from flask import Blueprint, request, jsonify
from core.db_manager import add_tariff, get_active_tariffs, get_tariff_by_id

tariffs_bp = Blueprint('tariffs', __name__, url_prefix='/api/tariffs')

@tariffs_bp.route('/', methods=['GET'])
def api_get_tariffs():
    """Получить все активные тарифы"""
    tariffs = get_active_tariffs()
    return jsonify({"success": True, "tariffs": tariffs})

@tariffs_bp.route('/', methods=['POST'])
def api_add_tariff():
    """Добавить новый тариф"""
    try:
        data = request.json
        if not all(k in data for k in ['name', 'price', 'duration_days', 'traffic_limit_gb']):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        tariff_id = add_tariff(
            name=data['name'],
            price=float(data['price']),
            duration_days=int(data['duration_days']),
            traffic_limit_gb=float(data['traffic_limit_gb'])
        )
        return jsonify({"success": True, "id": tariff_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@tariffs_bp.route('/<int:tariff_id>', methods=['GET'])
def api_get_tariff(tariff_id):
    """Получить тариф по ID"""
    tariff = get_tariff_by_id(tariff_id)
    if tariff:
        return jsonify({"success": True, "tariff": tariff})
    return jsonify({"success": False, "error": "Tariff not found"}), 404
