from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.mecanico import Mecanico

mecanico_bp = Blueprint('mecanico', __name__)

@mecanico_bp.route('/mecanicos', methods=['GET'])
def get_mecanicos():
    try:
        mecanicos = Mecanico.query.all()
        return jsonify([mecanico.to_dict() for mecanico in mecanicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mecanico_bp.route('/mecanicos', methods=['POST'])
def create_mecanico():
    try:
        data = request.get_json()
        mecanico = Mecanico(
            nome=data['nome'],
            especialidade=data.get('especialidade'),
            status=data.get('status', 'ativo')
        )
        db.session.add(mecanico)
        db.session.commit()
        return jsonify(mecanico.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mecanico_bp.route('/mecanicos/<int:id>', methods=['GET'])
def get_mecanico(id):
    try:
        mecanico = Mecanico.query.get_or_404(id)
        return jsonify(mecanico.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mecanico_bp.route('/mecanicos/<int:id>', methods=['PUT'])
def update_mecanico(id):
    try:
        mecanico = Mecanico.query.get_or_404(id)
        data = request.get_json()
        
        mecanico.nome = data.get('nome', mecanico.nome)
        mecanico.especialidade = data.get('especialidade', mecanico.especialidade)
        mecanico.status = data.get('status', mecanico.status)
        
        db.session.commit()
        return jsonify(mecanico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mecanico_bp.route('/mecanicos/<int:id>', methods=['DELETE'])
def delete_mecanico(id):
    try:
        mecanico = Mecanico.query.get_or_404(id)
        db.session.delete(mecanico)
        db.session.commit()
        return jsonify({'message': 'Mecânico deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

