# OPÇÃO 1: Se você quer manter o diagnóstico, crie o arquivo src/routes/diagnostico.py

# src/routes/diagnostico.py (VERSÃO MÍNIMA PARA NÃO DAR ERRO)
from flask import Blueprint, jsonify
from datetime import datetime

diagnostico_bp = Blueprint('diagnostico', __name__)

@diagnostico_bp.route('/diagnostico/health', methods=['GET'])
def health_check():
    """Verificação simples de saúde do sistema"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Sistema funcionando'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
