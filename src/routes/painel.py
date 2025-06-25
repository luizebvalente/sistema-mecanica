from flask import Blueprint, jsonify
from src.models.box import Box
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.models.user import db
from datetime import datetime, date

painel_bp = Blueprint('painel', __name__)

@painel_bp.route('/painel', methods=['GET'])
def get_painel_data():
    try:
        boxes = Box.query.all()
        painel_data = []
        
        for box in boxes:
            # Buscar serviço atual em execução
            servico_atual = ServicoExecucao.query.filter_by(
                box_id=box.id,
                status='em_andamento'
            ).first()
            
            # Buscar fila de serviços apenas do dia atual
            hoje = date.today()
            fila_servicos = FilaServico.query.filter_by(
                box_id=box.id,
                status='agendado'
            ).filter(
                db.or_(
                    FilaServico.data_agendamento == hoje,
                    FilaServico.data_agendamento.is_(None)  # Serviços sem data específica (para hoje)
                )
            ).order_by(FilaServico.posicao_fila).all()
            
            # Calcular tempo restante/atraso se há serviço em andamento
            tempo_restante_segundos = 0
            em_atraso = False
            if servico_atual and servico_atual.fim_previsto:
                agora = datetime.utcnow()
                delta = servico_atual.fim_previsto - agora
                tempo_restante_segundos = int(delta.total_seconds())
                em_atraso = tempo_restante_segundos < 0
            
            # Formatar horários para exibição
            horario_inicio = None
            horario_fim_previsto = None
            if servico_atual:
                horario_inicio = servico_atual.inicio.strftime('%H:%M') if servico_atual.inicio else None
                horario_fim_previsto = servico_atual.fim_previsto.strftime('%H:%M') if servico_atual.fim_previsto else None
            
            box_data = {
                'box': box.to_dict(),
                'servico_atual': servico_atual.to_dict() if servico_atual else None,
                'fila_servicos': [servico.to_dict() for servico in fila_servicos],
                'tempo_restante_segundos': tempo_restante_segundos,
                'em_atraso': em_atraso,
                'horario_inicio': horario_inicio,
                'horario_fim_previsto': horario_fim_previsto,
                'total_fila': len(fila_servicos)
            }
            
            painel_data.append(box_data)
        
        return jsonify(painel_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/box/<int:box_id>', methods=['GET'])
def get_box_detalhes(box_id):
    try:
        box = Box.query.get_or_404(box_id)
        
        # Buscar serviço atual
        servico_atual = ServicoExecucao.query.filter_by(
            box_id=box_id,
            status='em_andamento'
        ).first()
        
        # Buscar fila completa apenas do dia atual
        hoje = date.today()
        fila_servicos = FilaServico.query.filter_by(
            box_id=box_id,
            status='agendado'
        ).filter(
            db.or_(
                FilaServico.data_agendamento == hoje,
                FilaServico.data_agendamento.is_(None)  # Serviços sem data específica (para hoje)
            )
        ).order_by(FilaServico.posicao_fila).all()
        
        # Buscar histórico recente (últimos 5 serviços)
        historico = ServicoExecucao.query.filter_by(
            box_id=box_id,
            status='concluido'
        ).order_by(ServicoExecucao.fim_real.desc()).limit(5).all()
        
        # Calcular tempo restante/atraso
        tempo_restante_segundos = 0
        em_atraso = False
        if servico_atual and servico_atual.fim_previsto:
            agora = datetime.utcnow()
            delta = servico_atual.fim_previsto - agora
            tempo_restante_segundos = int(delta.total_seconds())
            em_atraso = tempo_restante_segundos < 0
        
        return jsonify({
            'box': box.to_dict(),
            'servico_atual': servico_atual.to_dict() if servico_atual else None,
            'fila_servicos': [servico.to_dict() for servico in fila_servicos],
            'historico': [servico.to_dict() for servico in historico],
            'tempo_restante_segundos': tempo_restante_segundos,
            'em_atraso': em_atraso,
            'horario_inicio': servico_atual.inicio.strftime('%H:%M') if servico_atual and servico_atual.inicio else None,
            'horario_fim_previsto': servico_atual.fim_previsto.strftime('%H:%M') if servico_atual and servico_atual.fim_previsto else None,
            'total_fila': len(fila_servicos)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

