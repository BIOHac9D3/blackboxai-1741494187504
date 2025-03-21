from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def status():
    return jsonify({'status': 'ok'})

@api_bp.route('/products')
def products():
    return jsonify({'products': []})

@api_bp.route('/categories')
def categories():
    return jsonify({'categories': []})
