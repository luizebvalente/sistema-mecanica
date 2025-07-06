from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from datetime import datetime, timedelta

servico_execucao_bp = Blueprint('servico_execucao', __name__)

@servico_execucao_bp.route('/servicos-execucao/tempo-real', methods=['GET'])
def get_tempo_real_servicos():
    """Retorna o tempo real de execução de todos os serviços ativos"""
    try:
        box_id = request.args.get('box_id')
        
        # Buscar serviços em andamento e pausados
        query = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        )
        
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        servicos = query.all()
        
        resultado = []
        for servico in servicos:
            tempo_real = servico.calcular_tempo_real_atual()
            resultado.append({
                'id': servico.id,
                'box_id': servico.box_id,
                'nome_cliente': servico.nome_cliente,
                'tipo_servico': servico.tipo_servico.nome if servico.tipo_servico else 'N/A',
                'inicio': servico.inicio.isoformat() if servico.inicio else None,
                'fim_previsto': servico.fim_previsto.isoformat() if servico.fim_previsto else None,
                'tempo_real': tempo_real
            })
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/tempo-real', methods=['GET'])
def get_tempo_real_servico(id):
    """Retorna o tempo real de execução de um serviço específico"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        tempo_real = servico.calcular_tempo_real_atual()
        
        return jsonify({
            'id': servico.id,
            'box_id': servico.box_id,
            'nome_cliente': servico.nome_cliente,
            'tipo_servico': servico.tipo_servico.nome if servico.tipo_servico else 'N/A',
            'inicio': servico.inicio.isoformat() if servico.inicio else None,
            'fim_previsto': servico.fim_previsto.isoformat() if servico.fim_previsto else None,
            'tempo_real': tempo_real
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao', methods=['GET'])
def get_servicos_execucao():
    try:
        status = request.args.get('status', 'em_andamento')
        box_id = request.args.get('box_id')
        
        query = ServicoExecucao.query
        
        if status:
            query = query.filter_by(status=status)
        
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        servicos = query.all()
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao', methods=['POST'])
def create_servico_execucao():
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['box_id', 'mecanico_id', 'tipo_servico_id', 'nome_cliente', 'marca_carro', 'modelo_carro']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'error': f'Campo obrigatório: {campo}'}), 400
        
        # Buscar o tipo de serviço para calcular o fim previsto
        tipo_servico = TipoServico.query.get(data['tipo_servico_id'])
        if not tipo_servico:
            return jsonify({'error': 'Tipo de serviço não encontrado'}), 404
        
        # Verificar se o box está livre
        box = Box.query.get(data['box_id'])
        if not box:
            return jsonify({'error': 'Box não encontrado'}), 404
        
        if box.status != 'livre':
            return jsonify({'error': 'Box não está livre'}), 400
        
        # Calcular fim previsto baseado no tempo estimado + tempo extra
        inicio = datetime.utcnow()
        tempo_total_minutos = tipo_servico.tempo_estimado + data.get('tempo_extra_minutos', 0)
        fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
        
        # Atualizar status do box para ocupado
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

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['PUT'])
def update_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar campos editáveis
        campos_editaveis = [
            'observacoes', 'tempo_extra_minutos', 'motivo_tempo_extra',
            'nome_cliente', 'telefone_cliente', 'marca_carro', 'modelo_carro', 
            'cor_carro', 'placa_carro'
        ]
        
        for campo in campos_editaveis:
            if campo in data:
                setattr(servico, campo, data[campo])
        
        # Se mudou tempo extra, recalcular fim previsto
        if 'tempo_extra_minutos' in data and servico.tipo_servico:
            tempo_total = servico.tipo_servico.tempo_estimado + servico.tempo_extra_minutos
            servico.fim_previsto = servico.inicio + timedelta(minutes=tempo_total)
        
        db.session.commit()
        return jsonify(servico.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/pausar', methods=['PUT'])
def pausar_servico(id):
    """Pausa um serviço em andamento"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        motivo = data.get('motivo') if data else None
        
        if not servico.pausar(motivo):
            return jsonify({'error': 'Não é possível pausar este serviço'}), 400
        
        # Atualizar status do box para pausado
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'pausado'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço pausado com sucesso',
            'servico': servico.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/retomar', methods=['PUT'])
def retomar_servico(id):
    """Retoma um serviço pausado"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        if not servico.retomar():
            return jsonify({'error': 'Não é possível retomar este serviço'}), 400
        
        # Atualizar status do box para ocupado
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'ocupado'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço retomado com sucesso',
            'servico': servico.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/finalizar', methods=['PUT'])
def finalizar_servico(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        
        if servico.status not in ['em_andamento', 'pausado']:
            return jsonify({'error': 'Serviço não pode ser finalizado'}), 400
        
        # Se estava pausado, calcular tempo pausado final
        if servico.status == 'pausado' and servico.pausado_em:
            tempo_pausa = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
            servico.tempo_pausado_total += int(tempo_pausa)
        
        servico.fim_real = datetime.utcnow()
        servico.status = 'concluido'
        servico.pausado_em = None
        
        # Adicionar observações finais se fornecidas
        if data and data.get('observacoes_finais'):
            observacoes_atuais = servico.observacoes or ''
            servico.observacoes = f"{observacoes_atuais}\n\nObservações finais: {data['observacoes_finais']}"
        
        # Liberar o box
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        
        # Verificar se há próximo serviço na fila
        proximo_servico = FilaServico.query.filter_by(
            box_id=servico.box_id,
            status='agendado',
            posicao_fila=1
        ).first()
        
        response_data = {
            'message': 'Serviço finalizado com sucesso',
            'servico': servico.to_dict(),
            'proximo_na_fila': proximo_servico.to_dict() if proximo_servico else None
        }
        
        return jsonify(response_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/interromper', methods=['PUT'])
def interromper_servico(id):
    """Interrompe um serviço (cancelamento forçado)"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        motivo = data.get('motivo') if data else 'Serviço interrompido'
        
        if servico.status not in ['em_andamento', 'pausado']:
            return jsonify({'error': 'Serviço não pode ser interrompido'}), 400
        
        # Se estava pausado, calcular tempo pausado final
        if servico.status == 'pausado' and servico.pausado_em:
            tempo_pausa = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
            servico.tempo_pausado_total += int(tempo_pausa)
        
        servico.fim_real = datetime.utcnow()
        servico.status = 'interrompido'
        servico.pausado_em = None
        
        # Adicionar motivo da interrupção
        observacoes_atuais = servico.observacoes or ''
        servico.observacoes = f"{observacoes_atuais}\n\nServiço interrompido: {motivo}"
        
        # Liberar o box
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço interrompido',
            'servico': servico.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

@servico_execucao_bp.route('/servicos-execucao/estatisticas', methods=['GET'])
def get_estatisticas_gerais():
    """Retorna estatísticas gerais dos serviços em execução"""
    try:
        # Contar serviços por status
        em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').count()
        pausados = ServicoExecucao.query.filter_by(status='pausado').count()
        concluidos_hoje = ServicoExecucao.query.filter(
            ServicoExecucao.status == 'concluido',
            ServicoExecucao.fim_real >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Buscar serviços em andamento com detalhes
        servicos_ativos = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).all()
        
        # Calcular tempo médio de conclusão hoje
        servicos_concluidos_hoje = ServicoExecucao.query.filter(
            ServicoExecucao.status == 'concluido',
            ServicoExecucao.fim_real >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        
        tempo_medio_conclusao = 0
        if servicos_concluidos_hoje:
            tempos = []
            for s in servicos_concluidos_hoje:
                if s.inicio and s.fim_real:
                    tempo_total = (s.fim_real - s.inicio).total_seconds() / 60
                    tempo_efetivo = tempo_total - s.tempo_pausado_total
                    tempos.append(tempo_efetivo)
            
            if tempos:
                tempo_medio_conclusao = sum(tempos) / len(tempos)
        
        return jsonify({
            'servicos_em_andamento': em_andamento,
            'servicos_pausados': pausados,
            'servicos_concluidos_hoje': concluidos_hoje,
            'tempo_medio_conclusao_minutos': int(tempo_medio_conclusao),
            'servicos_ativos': [s.to_dict() for s in servicos_ativos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>/historico-pausas', methods=['GET'])
def get_historico_pausas(id):
    """Retorna o histórico de pausas de um serviço"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        import json
        historico = []
        if servico.historico_pausas:
            historico = json.loads(servico.historico_pausas)
        
        # Se está pausado atualmente, adicionar pausa atual
        if servico.status == 'pausado' and servico.pausado_em:
            tempo_pausa_atual = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
            historico.append({
                'pausado_em': servico.pausado_em.isoformat(),
                'retomado_em': None,
                'duracao_minutos': int(tempo_pausa_atual),
                'motivo': servico.motivo_pausa,
                'em_andamento': True
            })
        
        return jsonify({
            'servico_id': id,
            'tempo_pausado_total': servico.tempo_pausado_total,
            'historico_pausas': historico
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

