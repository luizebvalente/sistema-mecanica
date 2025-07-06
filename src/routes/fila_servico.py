from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.fila_servico import FilaServico
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from src.models.tipo_servico import TipoServico
from datetime import datetime, timedelta
import json

fila_servico_bp = Blueprint('fila_servico', __name__)

@fila_servico_bp.route('/fila-servicos', methods=['GET'])
def get_fila_servicos():
    try:
        box_id = request.args.get('box_id')
        status = request.args.get('status', 'agendado')
        
        if box_id:
            servicos = FilaServico.query.filter_by(
                box_id=box_id, 
                status=status
            ).order_by(FilaServico.posicao_fila).all()
        else:
            servicos = FilaServico.query.filter_by(
                status=status
            ).order_by(FilaServico.box_id, FilaServico.posicao_fila).all()
        
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/gestao', methods=['GET'])
def get_fila_gestao():
    """Retorna todos os serviços que precisam de gestão: agendados + pausados"""
    try:
        box_id = request.args.get('box_id')
        incluir_detalhes = request.args.get('incluir_detalhes', 'true').lower() == 'true'
        
        # Buscar serviços agendados na fila
        query_fila = FilaServico.query.filter_by(status='agendado')
        if box_id:
            query_fila = query_fila.filter_by(box_id=box_id)
        
        servicos_fila = query_fila.order_by(FilaServico.box_id, FilaServico.posicao_fila).all()
        
        # Buscar serviços pausados
        query_pausados = ServicoExecucao.query.filter_by(status='pausado')
        if box_id:
            query_pausados = query_pausados.filter_by(box_id=box_id)
        
        servicos_pausados = query_pausados.order_by(ServicoExecucao.pausado_em.desc()).all()
        
        # Combinar resultados
        resultado = []
        
        # Adicionar serviços pausados primeiro (prioridade)
        for servico in servicos_pausados:
            item = servico.to_dict()
            item['tipo_item'] = 'pausado'
            item['pode_retomar'] = True
            item['pode_finalizar'] = True
            item['prioridade_visual'] = 'alta'  # Para destacar na interface
            
            # Calcular tempo de pausa atual
            if servico.pausado_em:
                tempo_pausa_atual = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
                item['tempo_pausa_atual_minutos'] = int(tempo_pausa_atual)
                item['tempo_pausa_atual_formatado'] = formatar_tempo_minutos(int(tempo_pausa_atual))
            
            # Calcular tempo total de execução
            if servico.inicio:
                tempo_total_execucao = (datetime.utcnow() - servico.inicio).total_seconds() / 60
                tempo_efetivo = tempo_total_execucao - servico.tempo_pausado_total
                if servico.pausado_em:
                    tempo_pausa_atual = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
                    tempo_efetivo -= tempo_pausa_atual
                item['tempo_execucao_efetivo_minutos'] = max(0, int(tempo_efetivo))
                item['tempo_execucao_efetivo_formatado'] = formatar_tempo_minutos(max(0, int(tempo_efetivo)))
            
            # Adicionar informações do histórico de pausas
            if incluir_detalhes and servico.historico_pausas:
                import json
                try:
                    historico = json.loads(servico.historico_pausas)
                    item['total_pausas'] = len(historico)
                    item['tempo_total_pausado_minutos'] = servico.tempo_pausado_total
                    item['tempo_total_pausado_formatado'] = formatar_tempo_minutos(servico.tempo_pausado_total)
                except:
                    item['total_pausas'] = 0
            
            resultado.append(item)
        
        # Adicionar serviços da fila
        for servico in servicos_fila:
            item = servico.to_dict()
            item['tipo_item'] = 'fila'
            item['pode_iniciar'] = True
            item['prioridade_visual'] = 'normal'
            
            # Calcular tempo estimado total
            tempo_estimado = servico.calcular_tempo_total_estimado()
            item['tempo_estimado_total_minutos'] = tempo_estimado
            item['tempo_estimado_total_formatado'] = formatar_tempo_minutos(tempo_estimado)
            
            resultado.append(item)
        
        # Estatísticas gerais
        estatisticas = {
            'total_servicos_pausados': len(servicos_pausados),
            'total_servicos_fila': len(servicos_fila),
            'total_geral': len(servicos_pausados) + len(servicos_fila),
            'boxes_com_pausados': len(set(s.box_id for s in servicos_pausados)),
            'boxes_com_fila': len(set(s.box_id for s in servicos_fila))
        }
        
        return jsonify({
            'servicos': resultado,
            'estatisticas': estatisticas,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def formatar_tempo_minutos(minutos):
    """Formata tempo em minutos para formato legível"""
    if minutos < 60:
        return f"{minutos}min"
    else:
        horas = minutos // 60
        mins = minutos % 60
        if mins == 0:
            return f"{horas}h"
        else:
            return f"{horas}h {mins}min"

@fila_servico_bp.route('/fila-servicos/pausados', methods=['GET'])
def get_servicos_pausados():
    """Retorna apenas os serviços pausados com informações detalhadas"""
    try:
        box_id = request.args.get('box_id')
        
        # Buscar serviços pausados
        query = ServicoExecucao.query.filter_by(status='pausado')
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        servicos_pausados = query.order_by(ServicoExecucao.pausado_em.desc()).all()
        
        resultado = []
        for servico in servicos_pausados:
            item = servico.to_dict()
            
            # Calcular tempo de pausa atual
            if servico.pausado_em:
                tempo_pausa_atual = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
                item['tempo_pausa_atual_minutos'] = int(tempo_pausa_atual)
                item['tempo_pausa_atual_formatado'] = formatar_tempo_minutos(int(tempo_pausa_atual))
                
                # Classificar urgência da pausa
                if tempo_pausa_atual > 120:  # Mais de 2 horas
                    item['urgencia_pausa'] = 'critica'
                elif tempo_pausa_atual > 60:  # Mais de 1 hora
                    item['urgencia_pausa'] = 'alta'
                elif tempo_pausa_atual > 30:  # Mais de 30 minutos
                    item['urgencia_pausa'] = 'media'
                else:
                    item['urgencia_pausa'] = 'baixa'
            
            # Calcular tempo total de execução efetivo
            if servico.inicio:
                tempo_total_execucao = (datetime.utcnow() - servico.inicio).total_seconds() / 60
                tempo_efetivo = tempo_total_execucao - servico.tempo_pausado_total
                if servico.pausado_em:
                    tempo_pausa_atual = (datetime.utcnow() - servico.pausado_em).total_seconds() / 60
                    tempo_efetivo -= tempo_pausa_atual
                item['tempo_execucao_efetivo_minutos'] = max(0, int(tempo_efetivo))
                item['tempo_execucao_efetivo_formatado'] = formatar_tempo_minutos(max(0, int(tempo_efetivo)))
            
            # Informações do histórico de pausas
            if servico.historico_pausas:
                import json
                try:
                    historico = json.loads(servico.historico_pausas)
                    item['total_pausas_anteriores'] = len(historico)
                    item['tempo_total_pausado_minutos'] = servico.tempo_pausado_total
                    item['tempo_total_pausado_formatado'] = formatar_tempo_minutos(servico.tempo_pausado_total)
                    
                    # Última pausa antes da atual
                    if historico:
                        ultima_pausa = historico[-1]
                        item['ultima_pausa_anterior'] = {
                            'duracao_minutos': ultima_pausa.get('duracao_minutos', 0),
                            'motivo': ultima_pausa.get('motivo', 'Não informado')
                        }
                except:
                    item['total_pausas_anteriores'] = 0
            else:
                item['total_pausas_anteriores'] = 0
            
            # Calcular percentual de conclusão estimado
            if servico.tipo_servico:
                tempo_estimado = servico.tipo_servico.tempo_estimado
                tempo_efetivo = item.get('tempo_execucao_efetivo_minutos', 0)
                if tempo_estimado > 0:
                    percentual = min(100, (tempo_efetivo / tempo_estimado) * 100)
                    item['percentual_conclusao_estimado'] = int(percentual)
                else:
                    item['percentual_conclusao_estimado'] = 0
            
            resultado.append(item)
        
        # Estatísticas dos serviços pausados
        estatisticas = {
            'total_pausados': len(servicos_pausados),
            'pausas_criticas': len([s for s in resultado if s.get('urgencia_pausa') == 'critica']),
            'pausas_altas': len([s for s in resultado if s.get('urgencia_pausa') == 'alta']),
            'pausas_medias': len([s for s in resultado if s.get('urgencia_pausa') == 'media']),
            'pausas_baixas': len([s for s in resultado if s.get('urgencia_pausa') == 'baixa']),
            'boxes_afetados': len(set(s['box_id'] for s in resultado))
        }
        
        return jsonify({
            'servicos_pausados': resultado,
            'estatisticas': estatisticas,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos', methods=['POST'])
def create_fila_servico():
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['box_id', 'mecanico_id', 'tipo_servico_id', 'nome_cliente', 'marca_carro', 'modelo_carro']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'error': f'Campo obrigatório: {campo}'}), 400
        
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
            observacoes=data.get('observacoes'),
            prioridade=data.get('prioridade', 1)
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
            observacoes=data.get('observacoes'),
            prioridade=data.get('prioridade', 1)
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
            tempo_total = servico_anterior.calcular_tempo_total_estimado()
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
        campos_editaveis = [
            'prioridade', 'observacoes', 'tempo_extra_minutos', 'motivo_tempo_extra',
            'nome_cliente', 'telefone_cliente', 'marca_carro', 'modelo_carro', 
            'cor_carro', 'placa_carro'
        ]
        
        for campo in campos_editaveis:
            if campo in data:
                setattr(servico, campo, data[campo])
        
        # Se mudou tempo extra, recalcular horário agendado
        if 'tempo_extra_minutos' in data:
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

@fila_servico_bp.route('/fila-servicos/<int:id>/iniciar', methods=['POST'])
def iniciar_servico_da_fila(id):
    """Inicia um serviço específico da fila"""
    try:
        servico_fila = FilaServico.query.get_or_404(id)
        
        if servico_fila.status != 'agendado':
            return jsonify({'error': 'Serviço não está agendado'}), 400
        
        # Verificar se o box está livre
        box = Box.query.get(servico_fila.box_id)
        if box.status != 'livre':
            return jsonify({'error': 'Box não está livre'}), 400
        
        # Converter para serviço em execução
        inicio = datetime.utcnow()
        tipo_servico = TipoServico.query.get(servico_fila.tipo_servico_id)
        tempo_total_minutos = servico_fila.calcular_tempo_total_estimado()
        fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
        
        # Criar serviço em execução
        servico_execucao = ServicoExecucao(
            box_id=servico_fila.box_id,
            mecanico_id=servico_fila.mecanico_id,
            tipo_servico_id=servico_fila.tipo_servico_id,
            inicio=inicio,
            fim_previsto=fim_previsto,
            tempo_extra_minutos=servico_fila.tempo_extra_minutos,
            motivo_tempo_extra=servico_fila.motivo_tempo_extra,
            nome_cliente=servico_fila.nome_cliente,
            telefone_cliente=servico_fila.telefone_cliente,
            marca_carro=servico_fila.marca_carro,
            modelo_carro=servico_fila.modelo_carro,
            cor_carro=servico_fila.cor_carro,
            placa_carro=servico_fila.placa_carro,
            observacoes=servico_fila.observacoes
        )
        
        # Atualizar status do box
        box.status = 'ocupado'
        
        # Remover da fila
        posicao_removida = servico_fila.posicao_fila
        box_id = servico_fila.box_id
        db.session.delete(servico_fila)
        
        # Reorganizar fila
        servicos_restantes = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(FilaServico.posicao_fila > posicao_removida).all()
        
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
            'message': 'Serviço iniciado com sucesso',
            'servico': servico_execucao.to_dict()
        }), 201
        
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
        
        # Usar a função de iniciar serviço específico
        return iniciar_servico_da_fila(proximo_servico.id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/reordenar', methods=['PUT'])
def reordenar_fila():
    """Reordena os itens da fila"""
    try:
        data = request.get_json()
        box_id = data.get('box_id')
        nova_ordem = data.get('nova_ordem')  # Lista de IDs na nova ordem
        
        if not box_id or not nova_ordem:
            return jsonify({'error': 'box_id e nova_ordem são obrigatórios'}), 400
        
        # Buscar todos os serviços da fila
        servicos = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).all()
        
        # Criar mapa de serviços por ID
        servicos_map = {s.id: s for s in servicos}
        
        # Atualizar posições conforme nova ordem
        for nova_posicao, servico_id in enumerate(nova_ordem, 1):
            if servico_id in servicos_map:
                servico = servicos_map[servico_id]
                servico.posicao_fila = nova_posicao
                # Recalcular horário agendado
                servico.agendado_para = calcular_horario_agendamento(
                    box_id,
                    nova_posicao,
                    servico.tempo_extra_minutos
                )
        
        db.session.commit()
        
        # Retornar fila atualizada
        servicos_atualizados = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).order_by(FilaServico.posicao_fila).all()
        
        return jsonify({
            'message': 'Fila reordenada com sucesso',
            'fila': [s.to_dict() for s in servicos_atualizados]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fila_servico_bp.route('/fila-servicos/estatisticas/<int:box_id>', methods=['GET'])
def get_estatisticas_fila(box_id):
    """Retorna estatísticas da fila de um box"""
    try:
        # Contar serviços na fila
        total_fila = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).count()
        
        # Calcular tempo total estimado da fila
        servicos_fila = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).all()
        
        tempo_total_estimado = sum(s.calcular_tempo_total_estimado() for s in servicos_fila)
        
        # Buscar serviço em andamento
        servico_atual = ServicoExecucao.query.filter_by(
            box_id=box_id,
            status='em_andamento'
        ).first()
        
        # Calcular horário previsto de conclusão
        horario_conclusao = None
        if servico_atual:
            horario_conclusao = servico_atual.fim_previsto
            if tempo_total_estimado > 0:
                horario_conclusao += timedelta(minutes=tempo_total_estimado)
        
        return jsonify({
            'box_id': box_id,
            'total_servicos_fila': total_fila,
            'tempo_total_estimado_minutos': tempo_total_estimado,
            'horario_conclusao_previsto': horario_conclusao.isoformat() if horario_conclusao else None,
            'servico_atual': servico_atual.to_dict() if servico_atual else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

