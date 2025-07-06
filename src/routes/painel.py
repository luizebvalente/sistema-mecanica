# src/routes/painel.py - VERSÃO CORRIGIDA
from flask import Blueprint, jsonify, request
from src.models.box import Box
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from datetime import datetime, date

painel_bp = Blueprint('painel', __name__)

@painel_bp.route('/painel', methods=['GET'])
def get_painel_data():
    """Retorna dados do painel principal com informações em tempo real"""
    try:
        incluir_historico = request.args.get('incluir_historico', 'false').lower() == 'true'
        
        boxes = Box.query.all()
        painel_data = []
        
        for box in boxes:
            # Buscar serviço atual em execução ou pausado
            servico_atual = ServicoExecucao.query.filter_by(
                box_id=box.id
            ).filter(
                ServicoExecucao.status.in_(['em_andamento', 'pausado'])
            ).first()
            
            # Buscar fila de serviços para hoje apenas
            hoje = date.today()
            fila_servicos = FilaServico.query.filter_by(
                box_id=box.id,
                status='agendado'
            ).filter(
                FilaServico.agendado_para >= datetime.combine(hoje, datetime.min.time()),
                FilaServico.agendado_para < datetime.combine(hoje, datetime.max.time())
            ).order_by(FilaServico.posicao_fila).all()
            
            # Calcular informações de tempo em tempo real
            tempo_info = calcular_informacoes_tempo(servico_atual)
            
            # Calcular tempo total estimado da fila
            tempo_total_fila = 0
            if fila_servicos:
                tempo_total_fila = sum(s.calcular_tempo_total_estimado() for s in fila_servicos)
            
            # Informações básicas do box
            box_data = {
                'box': box.to_dict(),
                'servico_atual': servico_atual.to_dict() if servico_atual else None,
                'fila_servicos': [servico.to_dict() for servico in fila_servicos],
                'total_fila': len(fila_servicos),
                'tempo_total_fila_minutos': tempo_total_fila,
                'tempo_total_fila_formatado': formatar_tempo_minutos(tempo_total_fila),
                
                # Informações de tempo (compatibilidade com frontend existente)
                'tempo_restante_segundos': tempo_info['tempo_restante_segundos'],
                'em_atraso': tempo_info['em_atraso'],
                'tempo_atraso_segundos': tempo_info['tempo_atraso_segundos'],
                'pausado': tempo_info['pausado'],
                'horario_inicio': tempo_info['horario_inicio'],
                'horario_fim_previsto': tempo_info['horario_fim_previsto'],
                
                # Informações detalhadas de tempo
                'tempo_detalhado': tempo_info
            }
            
            # Incluir histórico se solicitado
            if incluir_historico:
                historico = ServicoExecucao.query.filter_by(
                    box_id=box.id,
                    status='concluido'
                ).order_by(ServicoExecucao.fim_real.desc()).limit(5).all()
                box_data['historico'] = [servico.to_dict() for servico in historico]
            
            painel_data.append(box_data)
        
        # Estatísticas gerais do painel
        estatisticas_gerais = {
            'total_boxes': len(boxes),
            'boxes_ocupados': len([b for b in painel_data if b['servico_atual']]),
            'boxes_livres': len([b for b in painel_data if not b['servico_atual']]),
            'servicos_em_andamento': len([b for b in painel_data if b['servico_atual'] and not b['pausado']]),
            'servicos_pausados': len([b for b in painel_data if b['pausado']]),
            'total_servicos_fila': sum(b['total_fila'] for b in painel_data),
            'boxes_com_atraso': len([b for b in painel_data if b['em_atraso']])
        }
        
        return jsonify({
            'boxes': painel_data,
            'estatisticas': estatisticas_gerais,
            'timestamp': datetime.utcnow().isoformat(),
            'data_referencia': hoje.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/box/<int:box_id>', methods=['GET'])
def get_box_detalhes(box_id):
    """Retorna detalhes completos de um box específico"""
    try:
        box = Box.query.get_or_404(box_id)
        
        # Buscar serviço atual (em andamento ou pausado)
        servico_atual = ServicoExecucao.query.filter_by(
            box_id=box_id
        ).filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).first()
        
        # Buscar fila completa para hoje
        hoje = date.today()
        fila_servicos = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(
            FilaServico.agendado_para >= datetime.combine(hoje, datetime.min.time()),
            FilaServico.agendado_para < datetime.combine(hoje, datetime.max.time())
        ).order_by(FilaServico.posicao_fila).all()
        
        # Buscar histórico recente (últimos 10 serviços)
        historico = ServicoExecucao.query.filter_by(
            box_id=box_id,
            status='concluido'
        ).order_by(ServicoExecucao.fim_real.desc()).limit(10).all()
        
        # Calcular informações de tempo
        tempo_info = calcular_informacoes_tempo(servico_atual)
        
        # Calcular previsões da fila
        previsoes_fila = []
        if fila_servicos:
            horario_base = datetime.utcnow()
            if servico_atual and servico_atual.fim_previsto and not tempo_info['pausado']:
                horario_base = servico_atual.fim_previsto
            
            for servico in fila_servicos:
                tempo_estimado = servico.calcular_tempo_total_estimado()
                inicio_previsto = horario_base
                fim_previsto = horario_base + datetime.timedelta(minutes=tempo_estimado)
                
                previsoes_fila.append({
                    'servico_id': servico.id,
                    'posicao': servico.posicao_fila,
                    'inicio_previsto': inicio_previsto.isoformat(),
                    'fim_previsto': fim_previsto.isoformat(),
                    'horario_inicio_previsto': inicio_previsto.strftime('%H:%M'),
                    'horario_fim_previsto': fim_previsto.strftime('%H:%M'),
                    'tempo_estimado_minutos': tempo_estimado,
                    'tempo_estimado_formatado': formatar_tempo_minutos(tempo_estimado)
                })
                
                horario_base = fim_previsto
        
        # Estatísticas do box
        estatisticas_box = calcular_estatisticas_box(box_id)
        
        return jsonify({
            'box': box.to_dict(),
            'servico_atual': servico_atual.to_dict() if servico_atual else None,
            'fila_servicos': [servico.to_dict() for servico in fila_servicos],
            'previsoes_fila': previsoes_fila,
            'historico': [servico.to_dict() for servico in historico],
            'estatisticas': estatisticas_box,
            
            # Informações de tempo (compatibilidade)
            'tempo_restante_segundos': tempo_info['tempo_restante_segundos'],
            'em_atraso': tempo_info['em_atraso'],
            'tempo_atraso_segundos': tempo_info['tempo_atraso_segundos'],
            'pausado': tempo_info['pausado'],
            'horario_inicio': tempo_info['horario_inicio'],
            'horario_fim_previsto': tempo_info['horario_fim_previsto'],
            'total_fila': len(fila_servicos),
            
            # Informações detalhadas
            'tempo_detalhado': tempo_info,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/servicos-pausados', methods=['GET'])
def get_servicos_pausados():
    """Retorna todos os serviços pausados do sistema com informações detalhadas"""
    try:
        servicos_pausados = ServicoExecucao.query.filter_by(
            status='pausado'
        ).order_by(ServicoExecucao.pausado_em.desc()).all()
        
        servicos_data = []
        for servico in servicos_pausados:
            servico_dict = servico.to_dict()
            
            # Calcular tempo de pausa atual
            if servico.pausado_em:
                agora = datetime.utcnow()
                tempo_pausa_atual = int((agora - servico.pausado_em).total_seconds() / 60)
                servico_dict['tempo_pausa_atual_minutos'] = tempo_pausa_atual
                servico_dict['tempo_pausa_atual_formatado'] = formatar_tempo_minutos(tempo_pausa_atual)
                
                # Classificar urgência da pausa
                if tempo_pausa_atual > 120:  # Mais de 2 horas
                    servico_dict['urgencia_pausa'] = 'critica'
                    servico_dict['cor_urgencia'] = '#dc2626'  # vermelho
                elif tempo_pausa_atual > 60:  # Mais de 1 hora
                    servico_dict['urgencia_pausa'] = 'alta'
                    servico_dict['cor_urgencia'] = '#ea580c'  # laranja
                elif tempo_pausa_atual > 30:  # Mais de 30 minutos
                    servico_dict['urgencia_pausa'] = 'media'
                    servico_dict['cor_urgencia'] = '#ca8a04'  # amarelo
                else:
                    servico_dict['urgencia_pausa'] = 'baixa'
                    servico_dict['cor_urgencia'] = '#16a34a'  # verde
                
                # Calcular tempo desde o início considerando pausas
                tempo_execucao_real = servico_dict['tempo_execucao_efetivo_minutos']
                if servico.tipo_servico:
                    tempo_estimado = servico.tipo_servico.tempo_estimado + (servico.tempo_extra_minutos or 0)
                    if tempo_estimado > 0:
                        percentual = min(100, int((tempo_execucao_real / tempo_estimado) * 100))
                        servico_dict['percentual_conclusao_pausado'] = percentual
            
            servicos_data.append(servico_dict)
        
        # Estatísticas dos serviços pausados
        estatisticas = {
            'total_pausados': len(servicos_pausados),
            'pausas_criticas': len([s for s in servicos_data if s.get('urgencia_pausa') == 'critica']),
            'pausas_altas': len([s for s in servicos_data if s.get('urgencia_pausa') == 'alta']),
            'pausas_medias': len([s for s in servicos_data if s.get('urgencia_pausa') == 'media']),
            'pausas_baixas': len([s for s in servicos_data if s.get('urgencia_pausa') == 'baixa']),
            'boxes_afetados': len(set(s['box_id'] for s in servicos_data)),
            'tempo_total_pausado': sum(s.get('tempo_pausa_atual_minutos', 0) for s in servicos_data)
        }
        
        return jsonify({
            'servicos_pausados': servicos_data,
            'estatisticas': estatisticas,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/estatisticas-tempo-real', methods=['GET'])
def get_estatisticas_tempo_real():
    """Retorna estatísticas em tempo real para dashboards"""
    try:
        agora = datetime.utcnow()
        hoje = date.today()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        
        # Contar serviços por status
        em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').count()
        pausados = ServicoExecucao.query.filter_by(status='pausado').count()
        concluidos_hoje = ServicoExecucao.query.filter_by(status='concluido').filter(
            ServicoExecucao.fim_real >= inicio_dia
        ).count()
        
        # Serviços em atraso
        servicos_atraso = ServicoExecucao.query.filter_by(status='em_andamento').filter(
            ServicoExecucao.fim_previsto < agora
        ).count()
        
        # Boxes
        total_boxes = Box.query.count()
        boxes_ocupados = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).with_entities(ServicoExecucao.box_id).distinct().count()
        
        # Fila total
        total_fila = FilaServico.query.filter_by(status='agendado').filter(
            FilaServico.agendado_para >= inicio_dia,
            FilaServico.agendado_para < datetime.combine(hoje, datetime.max.time())
        ).count()
        
        # Tempo médio de execução hoje
        servicos_concluidos = ServicoExecucao.query.filter_by(status='concluido').filter(
            ServicoExecucao.fim_real >= inicio_dia
        ).all()
        
        tempo_medio = 0
        if servicos_concluidos:
            tempos = []
            for servico in servicos_concluidos:
                if servico.inicio and servico.fim_real:
                    tempo_total = (servico.fim_real - servico.inicio).total_seconds() / 60
                    tempo_efetivo = tempo_total - (servico.tempo_pausado_total or 0)
                    tempos.append(max(0, tempo_efetivo))
            
            if tempos:
                tempo_medio = int(sum(tempos) / len(tempos))
        
        return jsonify({
            'contadores': {
                'em_andamento': em_andamento,
                'pausados': pausados,
                'concluidos_hoje': concluidos_hoje,
                'em_atraso': servicos_atraso,
                'total_fila': total_fila
            },
            'boxes': {
                'total': total_boxes,
                'ocupados': boxes_ocupados,
                'livres': total_boxes - boxes_ocupados,
                'percentual_ocupacao': int((boxes_ocupados / total_boxes * 100)) if total_boxes > 0 else 0
            },
            'tempos': {
                'tempo_medio_execucao_minutos': tempo_medio,
                'tempo_medio_execucao_formatado': formatar_tempo_minutos(tempo_medio)
            },
            'alertas': {
                'servicos_em_atraso': servicos_atraso > 0,
                'servicos_pausados': pausados > 0,
                'boxes_livres_baixo': (total_boxes - boxes_ocupados) <= 1
            },
            'timestamp': agora.isoformat(),
            'data_referencia': hoje.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calcular_informacoes_tempo(servico_atual):
    """Calcula informações detalhadas de tempo para um serviço"""
    if not servico_atual:
        return {
            'tempo_restante_segundos': 0,
            'em_atraso': False,
            'tempo_atraso_segundos': 0,
            'pausado': False,
            'horario_inicio': None,
            'horario_fim_previsto': None,
            'tempo_decorrido_minutos': 0,
            'tempo_execucao_efetivo_minutos': 0,
            'percentual_conclusao': 0
        }
    
    agora = datetime.utcnow()
    pausado = servico_atual.status == 'pausado'
    
    # Calcular tempos básicos
    tempo_restante_segundos = 0
    em_atraso = False
    tempo_atraso_segundos = 0
    
    if servico_atual.fim_previsto and not pausado:
        delta = servico_atual.fim_previsto - agora
        tempo_restante_segundos = int(delta.total_seconds())
        
        if tempo_restante_segundos < 0:
            em_atraso = True
            tempo_atraso_segundos = abs(tempo_restante_segundos)
            tempo_restante_segundos = 0
    
    # Usar dados já calculados no to_dict do serviço
    servico_dict = servico_atual.to_dict()
    
    return {
        'tempo_restante_segundos': tempo_restante_segundos,
        'em_atraso': em_atraso,
        'tempo_atraso_segundos': tempo_atraso_segundos,
        'pausado': pausado,
        'horario_inicio': servico_dict['horario_inicio'],
        'horario_fim_previsto': servico_dict['horario_fim_previsto'],
        'tempo_decorrido_minutos': servico_dict['tempo_decorrido_total_minutos'],
        'tempo_execucao_efetivo_minutos': servico_dict['tempo_execucao_efetivo_minutos'],
        'percentual_conclusao': servico_dict['percentual_conclusao'],
        'tempo_pausado_total_minutos': servico_dict['tempo_pausado_total'],
        
        # Formatações
        'tempo_restante_formatado': formatar_tempo_segundos(tempo_restante_segundos),
        'tempo_atraso_formatado': formatar_tempo_segundos(tempo_atraso_segundos) if em_atraso else None,
        'tempo_decorrido_formatado': servico_dict['tempo_decorrido_formatado'],
        'tempo_execucao_formatado': servico_dict['tempo_execucao_formatado']
    }

def calcular_estatisticas_box(box_id):
    """Calcula estatísticas específicas de um box"""
    hoje = date.today()
    inicio_dia = datetime.combine(hoje, datetime.min.time())
    
    # Serviços concluídos hoje neste box
    concluidos_hoje = ServicoExecucao.query.filter_by(
        box_id=box_id,
        status='concluido'
    ).filter(ServicoExecucao.fim_real >= inicio_dia).count()
    
    # Tempo médio de execução hoje
    servicos_hoje = ServicoExecucao.query.filter_by(
        box_id=box_id,
        status='concluido'
    ).filter(ServicoExecucao.fim_real >= inicio_dia).all()
    
    tempo_medio = 0
    if servicos_hoje:
        tempos = []
        for servico in servicos_hoje:
            if servico.inicio and servico.fim_real:
                tempo_total = (servico.fim_real - servico.inicio).total_seconds() / 60
                tempo_efetivo = tempo_total - (servico.tempo_pausado_total or 0)
                tempos.append(max(0, tempo_efetivo))
        
        if tempos:
            tempo_medio = int(sum(tempos) / len(tempos))
    
    # Total na fila
    total_fila = FilaServico.query.filter_by(
        box_id=box_id,
        status='agendado'
    ).filter(
        FilaServico.agendado_para >= inicio_dia,
        FilaServico.agendado_para < datetime.combine(hoje, datetime.max.time())
    ).count()
    
    return {
        'concluidos_hoje': concluidos_hoje,
        'tempo_medio_execucao_minutos': tempo_medio,
        'tempo_medio_execucao_formatado': formatar_tempo_minutos(tempo_medio),
        'total_fila': total_fila,
        'produtividade_hoje': f"{concluidos_hoje} serviços"
    }

def formatar_tempo_minutos(minutos):
    """Formata tempo em minutos para formato legível"""
    if minutos == 0:
        return "0min"
    elif minutos < 60:
        return f"{minutos}min"
    else:
        horas = minutos // 60
        mins = minutos % 60
        if mins == 0:
            return f"{horas}h"
        else:
            return f"{horas}h {mins}min"

def formatar_tempo_segundos(segundos):
    """Formata tempo em segundos para formato legível"""
    if segundos == 0:
        return "0s"
    elif segundos < 60:
        return f"{segundos}s"
    else:
        minutos = segundos // 60
        segs = segundos % 60
        if segs == 0:
            return f"{minutos}min"
        else:
            return f"{minutos}min {segs}s"
