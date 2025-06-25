from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.fila_servico import FilaServico
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from datetime import datetime, timedelta

fila_servico_bp = Blueprint('fila_servico', __name__)

@fila_servico_bp.route('/fila-servicos', methods=['GET'])
def get_fila_servicos():
    try:
        box_id = request.args.get('box_id')
        if box_id:
            servicos = FilaServico.query.filter_by(
                box_id=box_id, 
                status='agendado'
            ).order_by(FilaServico.posicao_fila).all()
        else:
            servicos = FilaServico.query.filter_by(
                status='agendado'
            ).order_by(FilaServico.box_id, FilaServico.posicao_fila).all()
        
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos', methods=['POST'])
def create_fila_servico():
    try:
        data = request.get_json()
        
        # Verificar se foi especificada uma data/hora para agendamento
        agendado_para_str = data.get('agendado_para')
        if agendado_para_str:
            # Agendamento para data/hora específica
            return agendar_para_data_especifica(data)
        
        # Verificar se é para agendar na fila ou iniciar imediatamente
        box = Box.query.get(data['box_id'])
        if not box:
            return jsonify({'error': 'Box não encontrado'}), 404
        
        # Se o box está livre, iniciar serviço imediatamente
        if box.status == 'livre':
            return iniciar_servico_imediato(data)
        
        # Se o box está ocupado, adicionar na fila para hoje
        return adicionar_na_fila_hoje(data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def agendar_para_data_especifica(data):
    """Agenda um serviço para uma data e horário específicos"""
    try:
        from dateutil import parser
        
        # Converter string de data/hora para datetime
        agendado_para = parser.parse(data['agendado_para'])
        
        # Calcular posição na fila para aquela data
        data_inicio = agendado_para.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim = agendado_para.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        ultima_posicao = db.session.query(db.func.max(FilaServico.posicao_fila)).filter(
            FilaServico.box_id == data['box_id'],
            FilaServico.status == 'agendado',
            FilaServico.agendado_para >= data_inicio,
            FilaServico.agendado_para <= data_fim
        ).scalar() or 0
        
        nova_posicao = ultima_posicao + 1
        
        # Criar serviço na fila
        fila_servico = FilaServico(
            box_id=data['box_id'],
            mecanico_id=data['mecanico_id'],
            tipo_servico_id=data['tipo_servico_id'],
            agendado_para=agendado_para,
            posicao_fila=nova_posicao,
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
        
        db.session.add(fila_servico)
        db.session.commit()
        
        return jsonify({
            'tipo': 'agendado_para_data',
            'data': agendado_para.strftime('%d/%m/%Y'),
            'horario': agendado_para.strftime('%H:%M'),
            'posicao': nova_posicao,
            'fila_servico': fila_servico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        raise e

def iniciar_servico_imediato(data):
    """Inicia um serviço imediatamente em um box livre"""
    try:
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
        box.status = 'ocupado'
        
        # Criar serviço em execução
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
        
        return jsonify({
            'tipo': 'iniciado_imediatamente',
            'servico': servico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        raise e

def adicionar_na_fila_hoje(data):
    """Adiciona um serviço na fila de um box ocupado para hoje"""
    try:
        # Calcular próxima posição na fila para hoje
        hoje = datetime.now().date()
        data_inicio = datetime.combine(hoje, datetime.min.time())
        data_fim = datetime.combine(hoje, datetime.max.time())
        
        ultima_posicao = db.session.query(db.func.max(FilaServico.posicao_fila)).filter(
            FilaServico.box_id == data['box_id'],
            FilaServico.status == 'agendado',
            FilaServico.agendado_para >= data_inicio,
            FilaServico.agendado_para <= data_fim
        ).scalar() or 0
        
        nova_posicao = ultima_posicao + 1
        
        # Calcular horário previsto baseado nos serviços anteriores
        agendado_para = calcular_horario_agendamento(data['box_id'], nova_posicao, data.get('tempo_extra_minutos', 0))
        
        # Criar serviço na fila
        fila_servico = FilaServico(
            box_id=data['box_id'],
            mecanico_id=data['mecanico_id'],
            tipo_servico_id=data['tipo_servico_id'],
            agendado_para=agendado_para,
            posicao_fila=nova_posicao,
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
        
        db.session.add(fila_servico)
        db.session.commit()
        
        return jsonify({
            'tipo': 'adicionado_na_fila',
            'posicao': nova_posicao,
            'agendado_para': agendado_para.isoformat() if agendado_para else None,
            'fila_servico': fila_servico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        raise e

def calcular_horario_agendamento(box_id, posicao_fila, tempo_extra_minutos):
    """Calcula o horário previsto para um serviço na fila"""
    try:
        # Buscar serviço atual em execução
        servico_atual = ServicoExecucao.query.filter_by(
            box_id=box_id,
            status='em_andamento'
        ).first()
        
        if not servico_atual:
            return datetime.utcnow()
        
        # Começar do fim previsto do serviço atual
        horario_base = servico_atual.fim_previsto
        
        # Somar tempo de todos os serviços anteriores na fila
        servicos_anteriores = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(FilaServico.posicao_fila < posicao_fila).all()
        
        for servico_anterior in servicos_anteriores:
            tempo_total = servico_anterior.tipo_servico.tempo_estimado + servico_anterior.tempo_extra_minutos
            horario_base += timedelta(minutes=tempo_total)
        
        return horario_base
        
    except Exception as e:
        return datetime.utcnow()

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
        
        # Atualizar campos editáveis
        if 'prioridade' in data:
            servico.prioridade = data['prioridade']
        if 'observacoes' in data:
            servico.observacoes = data['observacoes']
        if 'tempo_extra_minutos' in data:
            servico.tempo_extra_minutos = data['tempo_extra_minutos']
            # Recalcular horário agendado
            servico.agendado_para = calcular_horario_agendamento(
                servico.box_id, 
                servico.posicao_fila, 
                servico.tempo_extra_minutos
            )
        
        db.session.commit()
        return jsonify(servico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/<int:id>', methods=['DELETE'])
def delete_fila_servico(id):
    try:
        servico = FilaServico.query.get_or_404(id)
        box_id = servico.box_id
        posicao_removida = servico.posicao_fila
        
        db.session.delete(servico)
        
        # Reorganizar posições na fila
        servicos_posteriores = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(FilaServico.posicao_fila > posicao_removida).all()
        
        for servico_posterior in servicos_posteriores:
            servico_posterior.posicao_fila -= 1
            # Recalcular horário
            servico_posterior.agendado_para = calcular_horario_agendamento(
                servico_posterior.box_id,
                servico_posterior.posicao_fila,
                servico_posterior.tempo_extra_minutos
            )
        
        db.session.commit()
        return jsonify({'message': 'Serviço removido da fila com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/proximo/<int:box_id>', methods=['POST'])
def iniciar_proximo_da_fila(box_id):
    """Inicia o próximo serviço da fila quando um serviço é finalizado"""
    try:
        # Buscar próximo serviço na fila
        proximo_servico = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado',
            posicao_fila=1
        ).first()
        
        if not proximo_servico:
            return jsonify({'message': 'Nenhum serviço na fila'}), 200
        
        # Converter para serviço em execução
        inicio = datetime.utcnow()
        tipo_servico = TipoServico.query.get(proximo_servico.tipo_servico_id)
        tempo_total_minutos = tipo_servico.tempo_estimado + proximo_servico.tempo_extra_minutos
        fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
        
        # Criar serviço em execução
        servico_execucao = ServicoExecucao(
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
        
        # Atualizar status do box
        box = Box.query.get(box_id)
        box.status = 'ocupado'
        
        # Remover da fila
        db.session.delete(proximo_servico)
        
        # Reorganizar fila
        servicos_restantes = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(FilaServico.posicao_fila > 1).all()
        
        for servico in servicos_restantes:
            servico.posicao_fila -= 1
            servico.agendado_para = calcular_horario_agendamento(
                servico.box_id,
                servico.posicao_fila,
                servico.tempo_extra_minutos
            )
        
        db.session.add(servico_execucao)
        db.session.commit()
        
        return jsonify({
            'message': 'Próximo serviço iniciado com sucesso',
            'servico': servico_execucao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

