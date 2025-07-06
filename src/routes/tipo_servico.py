from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.tipo_servico import TipoServico

tipo_servico_bp = Blueprint('tipo_servico', __name__)

@tipo_servico_bp.route('/tipos-servico', methods=['GET'])
def get_tipos_servico():
    try:
        tipos = TipoServico.query.all()
        return jsonify([tipo.to_dict() for tipo in tipos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tipo_servico_bp.route('/tipos-servico', methods=['POST'])
def create_tipo_servico():
    try:
        data = request.get_json()
        tipo = TipoServico(
            nome=data['nome'],
            tempo_estimado=data['tempo_estimado'],
            descricao=data.get('descricao')
        )
        db.session.add(tipo)
        db.session.commit()
        return jsonify(tipo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tipo_servico_bp.route('/tipos-servico/<int:id>', methods=['GET'])
def get_tipo_servico(id):
    try:
        tipo = TipoServico.query.get_or_404(id)
        return jsonify(tipo.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tipo_servico_bp.route('/tipos-servico/<int:id>', methods=['PUT'])
def update_tipo_servico(id):
    try:
        tipo = TipoServico.query.get_or_404(id)
        data = request.get_json()
        
        tipo.nome = data.get('nome', tipo.nome)
        tipo.tempo_estimado = data.get('tempo_estimado', tipo.tempo_estimado)
        tipo.descricao = data.get('descricao', tipo.descricao)
        
        db.session.commit()
        return jsonify(tipo.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tipo_servico_bp.route('/tipos-servico/<int:id>', methods=['DELETE'])
def delete_tipo_servico(id):
    try:
        tipo = TipoServico.query.get_or_404(id)
        db.session.delete(tipo)
        db.session.commit()
        return jsonify({'message': 'Tipo de serviço deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

