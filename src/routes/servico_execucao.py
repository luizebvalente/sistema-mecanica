from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from src.models.fila_servico import FilaServico
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

@servico_execucao_bp.route('/servicos-execucao/<int:id>/pausar', methods=['PUT'])
def pausar_servico(id):
    """Pausa um serviço em execução"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        if servico.status != 'em_andamento':
            return jsonify({'error': 'Serviço não está em andamento'}), 400
        
        agora = datetime.utcnow()
        
        # Atualizar status para pausado
        servico.status = 'pausado'
        servico.pausado_em = agora
        
        # Calcular tempo já decorrido desde o início
        if not hasattr(servico, 'tempo_pausado_total'):
            servico.tempo_pausado_total = 0
        
        # Atualizar status do box para disponível
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço pausado com sucesso',
            'servico': servico.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/despausar', methods=['PUT'])
def despausar_servico(id):
    """Retoma um serviço pausado"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        if servico.status != 'pausado':
            return jsonify({'error': 'Serviço não está pausado'}), 400
        
        # Verificar se o box está livre
        box = Box.query.get(servico.box_id)
        if box.status != 'livre':
            return jsonify({'error': 'Box não está disponível para retomar o serviço'}), 400
        
        agora = datetime.utcnow()
        
        # Calcular tempo que ficou pausado
        tempo_pausado = agora - servico.pausado_em
        tempo_pausado_minutos = int(tempo_pausado.total_seconds() / 60)
        
        # Adicionar tempo pausado ao total
        if not hasattr(servico, 'tempo_pausado_total'):
            servico.tempo_pausado_total = 0
        servico.tempo_pausado_total += tempo_pausado_minutos
        
        # Ajustar o fim previsto adicionando o tempo que ficou pausado
        servico.fim_previsto += tempo_pausado
        
        # Atualizar status
        servico.status = 'em_andamento'
        servico.pausado_em = None
        
        # Ocupar o box novamente
        box.status = 'ocupado'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço retomado com sucesso',
            'tempo_pausado_minutos': tempo_pausado_minutos,
            'servico': servico.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/finalizar', methods=['PUT'])
def finalizar_servico(id):
    """Finaliza um serviço e inicia o próximo da fila automaticamente"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        if servico.status not in ['em_andamento', 'pausado']:
            return jsonify({'error': 'Serviço não pode ser finalizado'}), 400
        
        agora = datetime.utcnow()
        box_id = servico.box_id
        
        # Finalizar o serviço atual
        servico.fim_real = agora
        servico.status = 'concluido'
        
        # Liberar o box temporariamente
        box = Box.query.get(box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        
        # Tentar iniciar o próximo serviço da fila
        proximo_servico = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado',
            posicao_fila=1
        ).first()
        
        response_data = {
            'message': 'Serviço finalizado com sucesso',
            'servico_finalizado': servico.to_dict(),
            'proximo_servico': None
        }
        
        if proximo_servico:
            try:
                # Iniciar próximo serviço automaticamente
                resultado_proximo = iniciar_proximo_servico_interno(box_id, proximo_servico)
                response_data['proximo_servico'] = resultado_proximo
                response_data['message'] += ' e próximo serviço iniciado automaticamente'
            except Exception as e:
                # Se falhar ao iniciar o próximo, pelo menos o atual foi finalizado
                response_data['erro_proximo'] = f'Erro ao iniciar próximo serviço: {str(e)}'
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def iniciar_proximo_servico_interno(box_id, proximo_servico):
    """Função interna para iniciar o próximo serviço da fila"""
    try:
        # Buscar tipo de serviço
        tipo_servico = TipoServico.query.get(proximo_servico.tipo_servico_id)
        if not tipo_servico:
            raise Exception('Tipo de serviço não encontrado')
        
        # Calcular horários
        inicio = datetime.utcnow()
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
        
        # Atualizar status do box
        box = Box.query.get(box_id)
        box.status = 'ocupado'
        
        # Remover da fila
        db.session.delete(proximo_servico)
        
        # Reorganizar fila (diminuir posição de todos os outros)
        servicos_restantes = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(FilaServico.posicao_fila > 1).all()
        
        for servico in servicos_restantes:
            servico.posicao_fila -= 1
            # Recalcular horário agendado
            from src.routes.fila_servico import calcular_horario_agendamento
            servico.agendado_para = calcular_horario_agendamento(
                servico.box_id,
                servico.posicao_fila,
                servico.tempo_extra_minutos
            )
        
        db.session.add(novo_servico)
        db.session.commit()
        
        return novo_servico.to_dict()
        
    except Exception as e:
        db.session.rollback()
        raise e

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['DELETE'])
def delete_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        # Liberar o box se o serviço estava em andamento
        if servico.status in ['em_andamento', 'pausado']:
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
            box_id=box_id
        ).filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).first()
        
        if servico:
            return jsonify(servico.to_dict())
        else:
            return jsonify(None)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/pausados', methods=['GET'])
def get_servicos_pausados():
    """Lista todos os serviços pausados"""
    try:
        servicos_pausados = ServicoExecucao.query.filter_by(status='pausado').all()
        return jsonify([servico.to_dict() for servico in servicos_pausados])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        return jsonify({'error': str(e)}), 500

