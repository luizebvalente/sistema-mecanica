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
        
        # Calcular fim previsto baseado no tempo estimado + tempo extra
        inicio = datetime.utcnow()
        tempo_total_minutos = tipo_servico.tempo_estimado + data.get('tempo_extra_minutos', 0)
        fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
        
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
            tempo_extra_minutos=data.get('tempo_extra_minutos', 0),
            motivo_tempo_extra=data.get('motivo_tempo_extra'),
            nome_cliente=data['nome_cliente'],
            telefone_cliente=data.get('telefone_cliente'),
            marca_carro=data['marca_carro'],
            modelo_carro=data['modelo_carro'],
            cor_carro=data.get('cor_carro'),
            placa_carro=data.get('placa_carro'),
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
        
        box_id = servico.box_id
        
        # Verificar se há próximo serviço na fila
        from src.models.fila_servico import FilaServico
        proximo_servico = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado',
            posicao_fila=1
        ).first()
        
        if proximo_servico:
            # Há serviço na fila - iniciar automaticamente
            inicio = datetime.utcnow()
            tipo_servico = TipoServico.query.get(proximo_servico.tipo_servico_id)
            tempo_total_minutos = tipo_servico.tempo_estimado + proximo_servico.tempo_extra_minutos
            fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
            
            # Criar novo serviço em execução
            novo_servico = ServicoExecucao(
                box_id=proximo_servico.box_id,
                mecanico_id=proximo_servico.mecanico_id,
                tipo_servico_id=proximo_servico.tipo_servico_id,
                inicio=inicio,
                fim_previsto=fim_previsto,
                tempo_extra_minutos=proximo_servico.tempo_extra_minutos,
                motivo_tempo_extra=proximo_servico.motivo_tempo_extra,
                nome_cliente=proximo_servico.nome_cliente,
                telefone_cliente=proximo_servico.telefone_cliente,
                marca_carro=proximo_servico.marca_carro,
                modelo_carro=proximo_servico.modelo_carro,
                cor_carro=proximo_servico.cor_carro,
                placa_carro=proximo_servico.placa_carro,
                observacoes=proximo_servico.observacoes
            )
            
            # Remover da fila
            db.session.delete(proximo_servico)
            
            # Reorganizar fila
            servicos_restantes = FilaServico.query.filter_by(
                box_id=box_id,
                status='agendado'
            ).filter(FilaServico.posicao_fila > 1).all()
            
            for servico_restante in servicos_restantes:
                servico_restante.posicao_fila -= 1
            
            db.session.add(novo_servico)
            # Box continua ocupado
        else:
            # Não há fila - liberar o box
            box = Box.query.get(box_id)
            if box:
                box.status = 'livre'
        
        db.session.commit()
        return jsonify(servico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['PUT'])
def update_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar campos editáveis
        if 'tempo_extra_minutos' in data:
            # Recalcular fim previsto se tempo extra mudou
            tipo_servico = TipoServico.query.get(servico.tipo_servico_id)
            tempo_total_minutos = tipo_servico.tempo_estimado + data['tempo_extra_minutos']
            servico.fim_previsto = servico.inicio + timedelta(minutes=tempo_total_minutos)
            servico.tempo_extra_minutos = data['tempo_extra_minutos']
        
        if 'motivo_tempo_extra' in data:
            servico.motivo_tempo_extra = data['motivo_tempo_extra']
        if 'observacoes' in data:
            servico.observacoes = data['observacoes']
        if 'telefone_cliente' in data:
            servico.telefone_cliente = data['telefone_cliente']
        if 'cor_carro' in data:
            servico.cor_carro = data['cor_carro']
        if 'placa_carro' in data:
            servico.placa_carro = data['placa_carro']
        
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

@servico_execucao_bp.route('/servicos-execucao/historico', methods=['GET'])
def get_historico_servicos():
    try:
        # Buscar serviços concluídos dos últimos 30 dias
        data_limite = datetime.utcnow() - timedelta(days=30)
        servicos = ServicoExecucao.query.filter(
            ServicoExecucao.status == 'concluido',
            ServicoExecucao.fim_real >= data_limite
        ).order_by(ServicoExecucao.fim_real.desc()).all()
        
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

