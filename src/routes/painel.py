from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.box import Box
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from datetime import datetime

painel_bp = Blueprint('painel', __name__)

@painel_bp.route('/painel', methods=['GET'])
def get_painel():
    try:
        # Buscar todos os boxes
        boxes = Box.query.all()
        painel_data = []
        
        for box in boxes:
            # Buscar serviço em execução no box
            servico_atual = ServicoExecucao.query.filter_by(
                box_id=box.id, 
                status='em_andamento'
            ).first()
            
            # Buscar fila de serviços do box
            fila_servicos = FilaServico.query.filter_by(
                box_id=box.id, 
                status='agendado'
            ).order_by(
                FilaServico.prioridade.desc(), 
                FilaServico.criado_em.asc()
            ).all()
            
            # Calcular tempo restante se houver serviço em execução
            tempo_restante = None
            if servico_atual:
                agora = datetime.utcnow()
                if servico_atual.fim_previsto > agora:
                    tempo_restante = int((servico_atual.fim_previsto - agora).total_seconds())
                else:
                    tempo_restante = 0
            
            box_data = {
                'box': box.to_dict(),
                'servico_atual': servico_atual.to_dict() if servico_atual else None,
                'tempo_restante_segundos': tempo_restante,
                'fila_servicos': [servico.to_dict() for servico in fila_servicos]
            }
            
            painel_data.append(box_data)
        
        return jsonify(painel_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/box/<int:box_id>', methods=['GET'])
def get_detalhes_box(box_id):
    try:
        # Buscar o box
        box = Box.query.get_or_404(box_id)
        
        # Buscar serviço em execução
        servico_atual = ServicoExecucao.query.filter_by(
            box_id=box_id, 
            status='em_andamento'
        ).first()
        
        # Buscar fila de serviços
        fila_servicos = FilaServico.query.filter_by(
            box_id=box_id, 
            status='agendado'
        ).order_by(
            FilaServico.prioridade.desc(), 
            FilaServico.criado_em.asc()
        ).all()
        
        # Calcular tempo restante
        tempo_restante = None
        if servico_atual:
            agora = datetime.utcnow()
            if servico_atual.fim_previsto > agora:
                tempo_restante = int((servico_atual.fim_previsto - agora).total_seconds())
            else:
                tempo_restante = 0
        
        detalhes = {
            'box': box.to_dict(),
            'servico_atual': servico_atual.to_dict() if servico_atual else None,
            'tempo_restante_segundos': tempo_restante,
            'fila_servicos': [servico.to_dict() for servico in fila_servicos]
        }
        
        return jsonify(detalhes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_bp.route('/painel/tempo-restante', methods=['GET'])
def get_tempos_restantes():
    try:
        servicos_em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').all()
        tempos = {}
        
        agora = datetime.utcnow()
        for servico in servicos_em_andamento:
            if servico.fim_previsto > agora:
                tempo_restante = int((servico.fim_previsto - agora).total_seconds())
            else:
                tempo_restante = 0
            
            tempos[servico.box_id] = {
                'servico_id': servico.id,
                'tempo_restante_segundos': tempo_restante
            }
        
        return jsonify(tempos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

