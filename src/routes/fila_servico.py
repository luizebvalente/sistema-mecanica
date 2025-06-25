from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.fila_servico import FilaServico

fila_servico_bp = Blueprint('fila_servico', __name__)

@fila_servico_bp.route('/fila-servicos', methods=['GET'])
def get_fila_servicos():
    try:
        servicos = FilaServico.query.filter_by(status='agendado').order_by(
            FilaServico.prioridade.desc(), 
            FilaServico.criado_em.asc()
        ).all()
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos', methods=['POST'])
def create_fila_servico():
    try:
        data = request.get_json()
        servico = FilaServico(
            box_id=data['box_id'],
            mecanico_id=data['mecanico_id'],
            tipo_servico_id=data['tipo_servico_id'],
            agendado_para=data.get('agendado_para'),
            prioridade=data.get('prioridade', 1),
            observacoes=data.get('observacoes')
        )
        db.session.add(servico)
        db.session.commit()
        return jsonify(servico.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/<int:id>', methods=['GET'])
def get_fila_servico(id):
    try:
        servico = FilaServico.query.get_or_404(id)
        return jsonify(servico.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/<int:id>', methods=['PUT'])
def update_fila_servico(id):
    try:
        servico = FilaServico.query.get_or_404(id)
        data = request.get_json()
        
        servico.box_id = data.get('box_id', servico.box_id)
        servico.mecanico_id = data.get('mecanico_id', servico.mecanico_id)
        servico.tipo_servico_id = data.get('tipo_servico_id', servico.tipo_servico_id)
        servico.agendado_para = data.get('agendado_para', servico.agendado_para)
        servico.prioridade = data.get('prioridade', servico.prioridade)
        servico.status = data.get('status', servico.status)
        servico.observacoes = data.get('observacoes', servico.observacoes)
        
        db.session.commit()
        return jsonify(servico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/<int:id>', methods=['DELETE'])
def delete_fila_servico(id):
    try:
        servico = FilaServico.query.get_or_404(id)
        db.session.delete(servico)
        db.session.commit()
        return jsonify({'message': 'Serviço da fila deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/box/<int:box_id>', methods=['GET'])
def get_fila_por_box(box_id):
    try:
        servicos = FilaServico.query.filter_by(
            box_id=box_id, 
            status='agendado'
        ).order_by(
            FilaServico.prioridade.desc(), 
            FilaServico.criado_em.asc()
        ).all()
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

