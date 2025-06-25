from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from datetime import datetime, timedelta

servico_execucao_bp = Blueprint('servico_execucao', __name__)

@servico_execucao_bp.route('/servicos-execucao', methods=['GET'])
def get_servicos_execucao():
    try:
        servicos = ServicoExecucao.query.filter_by(status='em_andamento').all()
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao', methods=['POST'])
def create_servico_execucao():
    try:
        data = request.get_json()
        
        # Buscar o tipo de serviço para calcular o fim previsto
        tipo_servico = TipoServico.query.get(data['tipo_servico_id'])
        if not tipo_servico:
            return jsonify({'error': 'Tipo de serviço não encontrado'}), 404
        
        # Calcular fim previsto baseado no tempo estimado
        inicio = datetime.utcnow()
        fim_previsto = inicio + timedelta(minutes=tipo_servico.tempo_estimado)
        
        # Atualizar status do box para ocupado
        box = Box.query.get(data['box_id'])
        if box:
            box.status = 'ocupado'
        
        servico = ServicoExecucao(
            box_id=data['box_id'],
            mecanico_id=data['mecanico_id'],
            tipo_servico_id=data['tipo_servico_id'],
            inicio=inicio,
            fim_previsto=fim_previsto,
            observacoes=data.get('observacoes')
        )
        
        db.session.add(servico)
        db.session.commit()
        return jsonify(servico.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['GET'])
def get_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        return jsonify(servico.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/finalizar', methods=['PUT'])
def finalizar_servico(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        servico.fim_real = datetime.utcnow()
        servico.status = 'concluido'
        
        # Liberar o box
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        return jsonify(servico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['DELETE'])
def delete_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        # Liberar o box se o serviço estava em andamento
        if servico.status == 'em_andamento':
            box = Box.query.get(servico.box_id)
            if box:
                box.status = 'livre'
        
        db.session.delete(servico)
        db.session.commit()
        return jsonify({'message': 'Serviço deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/box/<int:box_id>', methods=['GET'])
def get_servico_por_box(box_id):
    try:
        servico = ServicoExecucao.query.filter_by(
            box_id=box_id, 
            status='em_andamento'
        ).first()
        
        if servico:
            return jsonify(servico.to_dict())
        else:
            return jsonify(None)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

