from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.models.box import Box
from src.models.mecanico import Mecanico
from src.models.tipo_servico import TipoServico
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_

relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios/servicos-concluidos', methods=['GET'])
def relatorio_servicos_concluidos():
    """Relatório de serviços concluídos com filtros por período"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        box_id = request.args.get('box_id')
        mecanico_id = request.args.get('mecanico_id')
        
        # Query base
        query = ServicoExecucao.query.filter_by(status='concluido')
        
        # Aplicar filtros de data
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(ServicoExecucao.fim_real >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(ServicoExecucao.fim_real <= data_fim_dt)
        
        # Aplicar filtros de box e mecânico
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        if mecanico_id:
            query = query.filter_by(mecanico_id=mecanico_id)
        
        # Executar query
        servicos = query.order_by(ServicoExecucao.fim_real.desc()).all()
        
        # Calcular estatísticas
        total_servicos = len(servicos)
        tempo_total_minutos = 0
        servicos_atrasados = 0
        
        for servico in servicos:
            if servico.inicio and servico.fim_real:
                tempo_execucao = (servico.fim_real - servico.inicio).total_seconds() / 60
                tempo_total_minutos += tempo_execucao
                
                # Verificar se houve atraso
                if servico.fim_real > servico.fim_previsto:
                    servicos_atrasados += 1
        
        tempo_medio_minutos = tempo_total_minutos / total_servicos if total_servicos > 0 else 0
        percentual_atraso = (servicos_atrasados / total_servicos * 100) if total_servicos > 0 else 0
        
        return jsonify({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'filtros': {
                'box_id': box_id,
                'mecanico_id': mecanico_id
            },
            'estatisticas': {
                'total_servicos': total_servicos,
                'tempo_total_horas': round(tempo_total_minutos / 60, 2),
                'tempo_medio_minutos': round(tempo_medio_minutos, 2),
                'servicos_atrasados': servicos_atrasados,
                'percentual_atraso': round(percentual_atraso, 2)
            },
            'servicos': [servico.to_dict() for servico in servicos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/filas-futuras', methods=['GET'])
def relatorio_filas_futuras():
    """Relatório de serviços agendados para datas futuras"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        box_id = request.args.get('box_id')
        
        # Query base - serviços agendados
        query = FilaServico.query.filter_by(status='agendado')
        
        # Filtrar apenas datas futuras se não especificado data_inicio
        if not data_inicio:
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(FilaServico.agendado_para >= hoje)
        else:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(FilaServico.agendado_para >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(FilaServico.agendado_para <= data_fim_dt)
        
        if box_id:
            query = query.filter_by(box_id=box_id)
        
        # Executar query
        servicos_agendados = query.order_by(FilaServico.agendado_para).all()
        
        # Agrupar por data
        servicos_por_data = {}
        total_servicos = len(servicos_agendados)
        
        for servico in servicos_agendados:
            if servico.agendado_para:
                data_str = servico.agendado_para.strftime('%Y-%m-%d')
                if data_str not in servicos_por_data:
                    servicos_por_data[data_str] = {
                        'data': data_str,
                        'data_formatada': servico.agendado_para.strftime('%d/%m/%Y'),
                        'servicos': [],
                        'total_servicos': 0
                    }
                
                servicos_por_data[data_str]['servicos'].append(servico.to_dict())
                servicos_por_data[data_str]['total_servicos'] += 1
        
        # Converter para lista ordenada
        lista_datas = sorted(servicos_por_data.values(), key=lambda x: x['data'])
        
        return jsonify({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'filtros': {
                'box_id': box_id
            },
            'estatisticas': {
                'total_servicos_agendados': total_servicos,
                'total_datas': len(lista_datas)
            },
            'servicos_por_data': lista_datas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/produtividade-mecanicos', methods=['GET'])
def relatorio_produtividade_mecanicos():
    """Relatório de produtividade por mecânico"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Definir período padrão (últimos 30 dias)
        if not data_inicio:
            data_inicio_dt = datetime.now() - timedelta(days=30)
        else:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
        
        if not data_fim:
            data_fim_dt = datetime.now()
        else:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
        
        # Query para serviços concluídos no período
        servicos = ServicoExecucao.query.filter(
            ServicoExecucao.status == 'concluido',
            ServicoExecucao.fim_real >= data_inicio_dt,
            ServicoExecucao.fim_real <= data_fim_dt
        ).all()
        
        # Agrupar por mecânico
        produtividade_por_mecanico = {}
        
        for servico in servicos:
            mecanico_id = servico.mecanico_id
            
            if mecanico_id not in produtividade_por_mecanico:
                produtividade_por_mecanico[mecanico_id] = {
                    'mecanico': servico.mecanico.to_dict() if servico.mecanico else None,
                    'total_servicos': 0,
                    'tempo_total_minutos': 0,
                    'servicos_atrasados': 0,
                    'tipos_servico': {}
                }
            
            # Calcular tempo de execução
            if servico.inicio and servico.fim_real:
                tempo_execucao = (servico.fim_real - servico.inicio).total_seconds() / 60
                produtividade_por_mecanico[mecanico_id]['tempo_total_minutos'] += tempo_execucao
            
            # Contar serviços
            produtividade_por_mecanico[mecanico_id]['total_servicos'] += 1
            
            # Verificar atraso
            if servico.fim_real > servico.fim_previsto:
                produtividade_por_mecanico[mecanico_id]['servicos_atrasados'] += 1
            
            # Contar tipos de serviço
            tipo_nome = servico.tipo_servico.nome if servico.tipo_servico else 'Não especificado'
            if tipo_nome not in produtividade_por_mecanico[mecanico_id]['tipos_servico']:
                produtividade_por_mecanico[mecanico_id]['tipos_servico'][tipo_nome] = 0
            produtividade_por_mecanico[mecanico_id]['tipos_servico'][tipo_nome] += 1
        
        # Calcular métricas finais
        for mecanico_id, dados in produtividade_por_mecanico.items():
            total_servicos = dados['total_servicos']
            if total_servicos > 0:
                dados['tempo_medio_minutos'] = round(dados['tempo_total_minutos'] / total_servicos, 2)
                dados['percentual_atraso'] = round((dados['servicos_atrasados'] / total_servicos) * 100, 2)
                dados['tempo_total_horas'] = round(dados['tempo_total_minutos'] / 60, 2)
            else:
                dados['tempo_medio_minutos'] = 0
                dados['percentual_atraso'] = 0
                dados['tempo_total_horas'] = 0
        
        # Converter para lista ordenada por total de serviços
        lista_mecanicos = sorted(
            produtividade_por_mecanico.values(),
            key=lambda x: x['total_servicos'],
            reverse=True
        )
        
        return jsonify({
            'periodo': {
                'data_inicio': data_inicio_dt.strftime('%Y-%m-%d'),
                'data_fim': data_fim_dt.strftime('%Y-%m-%d')
            },
            'total_mecanicos': len(lista_mecanicos),
            'mecanicos': lista_mecanicos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/ocupacao-boxes', methods=['GET'])
def relatorio_ocupacao_boxes():
    """Relatório de ocupação dos boxes"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Definir período padrão (últimos 30 dias)
        if not data_inicio:
            data_inicio_dt = datetime.now() - timedelta(days=30)
        else:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
        
        if not data_fim:
            data_fim_dt = datetime.now()
        else:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
        
        # Buscar todos os boxes
        boxes = Box.query.all()
        
        ocupacao_por_box = {}
        
        for box in boxes:
            # Serviços concluídos no período
            servicos_concluidos = ServicoExecucao.query.filter(
                ServicoExecucao.box_id == box.id,
                ServicoExecucao.status == 'concluido',
                ServicoExecucao.fim_real >= data_inicio_dt,
                ServicoExecucao.fim_real <= data_fim_dt
            ).all()
            
            # Serviços agendados futuros
            servicos_agendados = FilaServico.query.filter(
                FilaServico.box_id == box.id,
                FilaServico.status == 'agendado',
                FilaServico.agendado_para >= datetime.now()
            ).count()
            
            # Calcular tempo total de ocupação
            tempo_total_ocupacao = 0
            for servico in servicos_concluidos:
                if servico.inicio and servico.fim_real:
                    tempo_ocupacao = (servico.fim_real - servico.inicio).total_seconds() / 3600  # em horas
                    tempo_total_ocupacao += tempo_ocupacao
            
            ocupacao_por_box[box.id] = {
                'box': box.to_dict(),
                'servicos_concluidos': len(servicos_concluidos),
                'servicos_agendados': servicos_agendados,
                'tempo_total_ocupacao_horas': round(tempo_total_ocupacao, 2),
                'tempo_medio_por_servico_minutos': round((tempo_total_ocupacao * 60) / len(servicos_concluidos), 2) if servicos_concluidos else 0
            }
        
        # Converter para lista ordenada por ocupação
        lista_boxes = sorted(
            ocupacao_por_box.values(),
            key=lambda x: x['tempo_total_ocupacao_horas'],
            reverse=True
        )
        
        return jsonify({
            'periodo': {
                'data_inicio': data_inicio_dt.strftime('%Y-%m-%d'),
                'data_fim': data_fim_dt.strftime('%Y-%m-%d')
            },
            'total_boxes': len(lista_boxes),
            'boxes': lista_boxes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/dashboard', methods=['GET'])
def relatorio_dashboard():
    """Dashboard com métricas gerais do sistema"""
    try:
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Serviços de hoje
        servicos_hoje = ServicoExecucao.query.filter(
            func.date(ServicoExecucao.inicio) == hoje
        ).count()
        
        # Serviços do mês
        servicos_mes = ServicoExecucao.query.filter(
            ServicoExecucao.inicio >= inicio_mes
        ).count()
        
        # Serviços em andamento
        servicos_andamento = ServicoExecucao.query.filter_by(status='em_andamento').count()
        
        # Serviços agendados para hoje
        inicio_hoje = datetime.combine(hoje, datetime.min.time())
        fim_hoje = datetime.combine(hoje, datetime.max.time())
        
        servicos_agendados_hoje = FilaServico.query.filter(
            FilaServico.status == 'agendado',
            FilaServico.agendado_para >= inicio_hoje,
            FilaServico.agendado_para <= fim_hoje
        ).count()
        
        # Boxes livres
        boxes_livres = Box.query.filter_by(status='livre').count()
        boxes_ocupados = Box.query.filter_by(status='ocupado').count()
        
        # Serviços atrasados hoje
        agora = datetime.now()
        servicos_atrasados = ServicoExecucao.query.filter(
            ServicoExecucao.status == 'em_andamento',
            ServicoExecucao.fim_previsto < agora
        ).count()
        
        return jsonify({
            'data_atualizacao': datetime.now().isoformat(),
            'metricas_hoje': {
                'servicos_realizados': servicos_hoje,
                'servicos_agendados': servicos_agendados_hoje,
                'servicos_em_andamento': servicos_andamento,
                'servicos_atrasados': servicos_atrasados
            },
            'metricas_mes': {
                'total_servicos': servicos_mes
            },
            'status_boxes': {
                'livres': boxes_livres,
                'ocupados': boxes_ocupados,
                'total': boxes_livres + boxes_ocupados
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

