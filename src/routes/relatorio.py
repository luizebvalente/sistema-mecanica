from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.models.box import Box
from src.models.mecanico import Mecanico
from src.models.tipo_servico import TipoServico
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_

relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios/servicos-concluidos', methods=['GET'])
def get_servicos_concluidos():
    """Relatório de serviços concluídos com filtros opcionais"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        box_id = request.args.get('box_id')
        mecanico_id = request.args.get('mecanico_id')
        
        # Query base
        query = ServicoExecucao.query.filter_by(status='concluido')
        
        # Aplicar filtros
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(ServicoExecucao.fim_real >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(ServicoExecucao.fim_real < data_fim_dt)
        
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        if mecanico_id:
            query = query.filter_by(mecanico_id=mecanico_id)
        
        # Ordenar por data de conclusão
        servicos = query.order_by(ServicoExecucao.fim_real.desc()).all()
        
        # Calcular estatísticas
        total_servicos = len(servicos)
        tempo_total_minutos = 0
        servicos_no_prazo = 0
        servicos_atrasados = 0
        
        for servico in servicos:
            if servico.fim_real and servico.inicio:
                tempo_execucao = (servico.fim_real - servico.inicio).total_seconds() / 60
                tempo_total_minutos += tempo_execucao
                
                # Verificar se foi no prazo
                tempo_previsto = servico.tipo_servico.tempo_estimado + servico.tempo_extra_minutos
                if tempo_execucao <= tempo_previsto:
                    servicos_no_prazo += 1
                else:
                    servicos_atrasados += 1
        
        tempo_medio_minutos = tempo_total_minutos / total_servicos if total_servicos > 0 else 0
        
        return jsonify({
            'servicos': [servico.to_dict() for servico in servicos],
            'estatisticas': {
                'total_servicos': total_servicos,
                'servicos_no_prazo': servicos_no_prazo,
                'servicos_atrasados': servicos_atrasados,
                'percentual_no_prazo': (servicos_no_prazo / total_servicos * 100) if total_servicos > 0 else 0,
                'tempo_medio_minutos': round(tempo_medio_minutos, 2),
                'tempo_total_horas': round(tempo_total_minutos / 60, 2)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/filas-futuras', methods=['GET'])
def get_filas_futuras():
    """Relatório de filas agendadas para datas futuras"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio', date.today().isoformat())
        data_fim = request.args.get('data_fim')
        box_id = request.args.get('box_id')
        
        # Query base
        query = FilaServico.query.filter_by(status='agendado')
        
        # Filtrar por data
        data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(FilaServico.data_agendamento >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(FilaServico.data_agendamento <= data_fim_dt)
        
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        # Ordenar por data e posição na fila
        filas = query.order_by(
            FilaServico.data_agendamento.asc(),
            FilaServico.box_id.asc(),
            FilaServico.posicao_fila.asc()
        ).all()
        
        # Agrupar por data
        filas_por_data = {}
        for fila in filas:
            data_str = fila.data_agendamento.isoformat() if fila.data_agendamento else 'sem_data'
            if data_str not in filas_por_data:
                filas_por_data[data_str] = []
            filas_por_data[data_str].append(fila.to_dict())
        
        # Calcular estatísticas
        total_agendamentos = len(filas)
        agendamentos_por_box = {}
        agendamentos_por_mecanico = {}
        
        for fila in filas:
            # Por box
            box_nome = fila.box.numero if fila.box else 'Desconhecido'
            agendamentos_por_box[box_nome] = agendamentos_por_box.get(box_nome, 0) + 1
            
            # Por mecânico
            mecanico_nome = fila.mecanico.nome if fila.mecanico else 'Desconhecido'
            agendamentos_por_mecanico[mecanico_nome] = agendamentos_por_mecanico.get(mecanico_nome, 0) + 1
        
        return jsonify({
            'filas_por_data': filas_por_data,
            'estatisticas': {
                'total_agendamentos': total_agendamentos,
                'agendamentos_por_box': agendamentos_por_box,
                'agendamentos_por_mecanico': agendamentos_por_mecanico,
                'datas_com_agendamentos': len(filas_por_data)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/produtividade-mecanicos', methods=['GET'])
def get_produtividade_mecanicos():
    """Relatório de produtividade dos mecânicos"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Query base
        query = ServicoExecucao.query.filter_by(status='concluido')
        
        # Aplicar filtros de data
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(ServicoExecucao.fim_real >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(ServicoExecucao.fim_real < data_fim_dt)
        
        servicos = query.all()
        
        # Agrupar por mecânico
        produtividade = {}
        
        for servico in servicos:
            mecanico_id = servico.mecanico_id
            mecanico_nome = servico.mecanico.nome if servico.mecanico else 'Desconhecido'
            
            if mecanico_id not in produtividade:
                produtividade[mecanico_id] = {
                    'nome': mecanico_nome,
                    'total_servicos': 0,
                    'tempo_total_minutos': 0,
                    'servicos_no_prazo': 0,
                    'servicos_atrasados': 0,
                    'tipos_servico': {}
                }
            
            produtividade[mecanico_id]['total_servicos'] += 1
            
            # Calcular tempo de execução
            if servico.fim_real and servico.inicio:
                tempo_execucao = (servico.fim_real - servico.inicio).total_seconds() / 60
                produtividade[mecanico_id]['tempo_total_minutos'] += tempo_execucao
                
                # Verificar se foi no prazo
                tempo_previsto = servico.tipo_servico.tempo_estimado + servico.tempo_extra_minutos
                if tempo_execucao <= tempo_previsto:
                    produtividade[mecanico_id]['servicos_no_prazo'] += 1
                else:
                    produtividade[mecanico_id]['servicos_atrasados'] += 1
            
            # Contar tipos de serviço
            tipo_nome = servico.tipo_servico.nome if servico.tipo_servico else 'Desconhecido'
            if tipo_nome not in produtividade[mecanico_id]['tipos_servico']:
                produtividade[mecanico_id]['tipos_servico'][tipo_nome] = 0
            produtividade[mecanico_id]['tipos_servico'][tipo_nome] += 1
        
        # Calcular métricas finais
        for mecanico_id, dados in produtividade.items():
            total = dados['total_servicos']
            if total > 0:
                dados['percentual_no_prazo'] = round((dados['servicos_no_prazo'] / total) * 100, 2)
                dados['tempo_medio_minutos'] = round(dados['tempo_total_minutos'] / total, 2)
                dados['tempo_total_horas'] = round(dados['tempo_total_minutos'] / 60, 2)
            else:
                dados['percentual_no_prazo'] = 0
                dados['tempo_medio_minutos'] = 0
                dados['tempo_total_horas'] = 0
        
        return jsonify({
            'produtividade_mecanicos': list(produtividade.values()),
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/dashboard', methods=['GET'])
def get_dashboard():
    """Dashboard com resumo geral do sistema"""
    try:
        hoje = date.today()
        
        # Serviços de hoje
        servicos_hoje = ServicoExecucao.query.filter(
            func.date(ServicoExecucao.inicio) == hoje
        ).all()
        
        # Filas para hoje
        filas_hoje = FilaServico.query.filter(
            db.or_(
                FilaServico.data_agendamento == hoje,
                FilaServico.data_agendamento.is_(None)
            )
        ).filter_by(status='agendado').all()
        
        # Serviços em andamento
        servicos_andamento = ServicoExecucao.query.filter_by(status='em_andamento').all()
        
        # Boxes ocupados
        boxes_ocupados = Box.query.filter_by(status='ocupado').count()
        boxes_total = Box.query.count()
        
        # Estatísticas dos últimos 7 dias
        data_7_dias = hoje - timedelta(days=7)
        servicos_7_dias = ServicoExecucao.query.filter(
            ServicoExecucao.fim_real >= data_7_dias,
            ServicoExecucao.status == 'concluido'
        ).all()
        
        return jsonify({
            'resumo_hoje': {
                'servicos_iniciados': len(servicos_hoje),
                'servicos_em_andamento': len(servicos_andamento),
                'filas_agendadas': len(filas_hoje),
                'boxes_ocupados': boxes_ocupados,
                'boxes_livres': boxes_total - boxes_ocupados
            },
            'ultimos_7_dias': {
                'total_servicos_concluidos': len(servicos_7_dias),
                'media_servicos_dia': round(len(servicos_7_dias) / 7, 1)
            },
            'servicos_em_andamento': [servico.to_dict() for servico in servicos_andamento],
            'proximas_filas': [fila.to_dict() for fila in filas_hoje[:5]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

