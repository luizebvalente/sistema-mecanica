# src/routes/diagnostico.py - Rotas para diagnóstico e teste
from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.fila_servico import FilaServico
from src.models.box import Box
from datetime import datetime, date

diagnostico_bp = Blueprint('diagnostico', __name__)

@diagnostico_bp.route('/diagnostico/sistema', methods=['GET'])
def diagnostico_sistema():
    """Diagnóstico completo do sistema"""
    try:
        agora = datetime.utcnow()
        hoje = date.today()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        
        # Contadores básicos
        contadores = {
            'servicos_em_andamento': ServicoExecucao.query.filter_by(status='em_andamento').count(),
            'servicos_pausados': ServicoExecucao.query.filter_by(status='pausado').count(),
            'servicos_concluidos_hoje': ServicoExecucao.query.filter_by(status='concluido').filter(
                ServicoExecucao.fim_real >= inicio_dia
            ).count(),
            'total_boxes': Box.query.count(),
            'boxes_ocupados': Box.query.filter_by(status='ocupado').count(),
            'boxes_livres': Box.query.filter_by(status='livre').count(),
            'servicos_na_fila': FilaServico.query.filter_by(status='agendado').count()
        }
        
        # Verificações de integridade
        verificacoes = []
        
        # 1. Boxes ocupados devem ter serviço ativo
        boxes_ocupados = Box.query.filter_by(status='ocupado').all()
        boxes_sem_servico = []
        for box in boxes_ocupados:
            servico_ativo = ServicoExecucao.query.filter_by(box_id=box.id).filter(
                ServicoExecucao.status.in_(['em_andamento', 'pausado'])
            ).first()
            if not servico_ativo:
                boxes_sem_servico.append(box.id)
        
        if boxes_sem_servico:
            verificacoes.append({
                'tipo': 'erro',
                'titulo': 'Boxes ocupados sem serviço',
                'descricao': f'Boxes {boxes_sem_servico} estão marcados como ocupados mas não têm serviço ativo',
                'acao': 'Marcar boxes como livres ou verificar serviços'
            })
        
        # 2. Serviços em andamento devem ter box ocupado
        servicos_em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').all()
        servicos_sem_box_ocupado = []
        for servico in servicos_em_andamento:
            box = Box.query.get(servico.box_id)
            if box and box.status != 'ocupado':
                servicos_sem_box_ocupado.append(servico.id)
        
        if servicos_sem_box_ocupado:
            verificacoes.append({
                'tipo': 'erro',
                'titulo': 'Serviços em andamento sem box ocupado',
                'descricao': f'Serviços {servicos_sem_box_ocupado} estão em andamento mas seus boxes não estão ocupados',
                'acao': 'Ocupar boxes ou pausar serviços'
            })
        
        # 3. Serviços pausados sem data de pausa
        servicos_pausados_invalidos = ServicoExecucao.query.filter_by(status='pausado').filter(
            ServicoExecucao.pausado_em.is_(None)
        ).all()
        
        if servicos_pausados_invalidos:
            verificacoes.append({
                'tipo': 'erro',
                'titulo': 'Serviços pausados sem data',
                'descricao': f'{len(servicos_pausados_invalidos)} serviços pausados sem data de pausa',
                'acao': 'Definir data de pausa ou alterar status'
            })
        
        # 4. Verificar serviços em atraso
        servicos_em_atraso = ServicoExecucao.query.filter_by(status='em_andamento').filter(
            ServicoExecucao.fim_previsto < agora
        ).all()
        
        if servicos_em_atraso:
            verificacoes.append({
                'tipo': 'aviso',
                'titulo': 'Serviços em atraso',
                'descricao': f'{len(servicos_em_atraso)} serviços estão atrasados',
                'acao': 'Verificar progresso e ajustar previsões'
            })
        
        # 5. Serviços pausados há muito tempo
        servicos_pausados_longos = ServicoExecucao.query.filter_by(status='pausado').filter(
            ServicoExecucao.pausado_em < agora - datetime.timedelta(hours=2)
        ).all()
        
        if servicos_pausados_longos:
            verificacoes.append({
                'tipo': 'aviso',
                'titulo': 'Serviços pausados há muito tempo',
                'descricao': f'{len(servicos_pausados_longos)} serviços pausados há mais de 2 horas',
                'acao': 'Retomar ou cancelar serviços'
            })
        
        # Status geral
        status_geral = 'ok'
        if any(v['tipo'] == 'erro' for v in verificacoes):
            status_geral = 'erro'
        elif any(v['tipo'] == 'aviso' for v in verificacoes):
            status_geral = 'aviso'
        
        # Estatísticas de performance
        performance = calcular_performance_hoje()
        
        return jsonify({
            'timestamp': agora.isoformat(),
            'data_referencia': hoje.isoformat(),
            'status_geral': status_geral,
            'contadores': contadores,
            'verificacoes': verificacoes,
            'performance': performance,
            'sistema': {
                'versao': '1.0.0',
                'uptime': 'N/A',
                'memoria_db': 'N/A'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diagnostico_bp.route('/diagnostico/corrigir-inconsistencias', methods=['POST'])
def corrigir_inconsistencias():
    """Corrige inconsistências automáticas do sistema"""
    try:
        data = request.get_json() or {}
        modo_simulacao = data.get('simulacao', True)
        
        correcoes = []
        
        if not modo_simulacao:
            # 1. Corrigir boxes ocupados sem serviço
            boxes_ocupados = Box.query.filter_by(status='ocupado').all()
            for box in boxes_ocupados:
                servico_ativo = ServicoExecucao.query.filter_by(box_id=box.id).filter(
                    ServicoExecucao.status.in_(['em_andamento', 'pausado'])
                ).first()
                if not servico_ativo:
                    box.status = 'livre'
                    correcoes.append(f"Box {box.id}: ocupado → livre")
            
            # 2. Corrigir serviços em andamento sem box ocupado
            servicos_em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').all()
            for servico in servicos_em_andamento:
                box = Box.query.get(servico.box_id)
                if box and box.status == 'livre':
                    box.status = 'ocupado'
                    correcoes.append(f"Box {box.id}: livre → ocupado (serviço {servico.id})")
            
            # 3. Corrigir campos NULL
            servicos_null = ServicoExecucao.query.filter(
                db.or_(
                    ServicoExecucao.tempo_pausado_total.is_(None),
                    ServicoExecucao.tempo_extra_minutos.is_(None)
                )
            ).all()
            
            for servico in servicos_null:
                if servico.tempo_pausado_total is None:
                    servico.tempo_pausado_total = 0
                    correcoes.append(f"Serviço {servico.id}: tempo_pausado_total → 0")
                if servico.tempo_extra_minutos is None:
                    servico.tempo_extra_minutos = 0
                    correcoes.append(f"Serviço {servico.id}: tempo_extra_minutos → 0")
            
            # 4. Corrigir serviços pausados sem data
            servicos_pausados_invalidos = ServicoExecucao.query.filter_by(status='pausado').filter(
                ServicoExecucao.pausado_em.is_(None)
            ).all()
            
            for servico in servicos_pausados_invalidos:
                servico.status = 'em_andamento'
                servico.pausado_em = None
                correcoes.append(f"Serviço {servico.id}: pausado sem data → em_andamento")
            
            db.session.commit()
        else:
            # Modo simulação - apenas reportar o que seria feito
            correcoes.append("MODO SIMULAÇÃO - nenhuma alteração foi feita")
            correcoes.append("Para aplicar correções, envie { \"simulacao\": false }")
        
        return jsonify({
            'modo_simulacao': modo_simulacao,
            'correcoes_aplicadas': len([c for c in correcoes if not c.startswith('MODO')]),
            'detalhes': correcoes,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        if not modo_simulacao:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diagnostico_bp.route('/diagnostico/teste-tempo-real', methods=['GET'])
def teste_tempo_real():
    """Testa se os cálculos de tempo estão funcionando"""
    try:
        servicos_ativos = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).all()
        
        resultado = []
        
        for servico in servicos_ativos:
            servico_dict = servico.to_dict()
            
            # Extrair informações relevantes para teste
            teste_servico = {
                'id': servico.id,
                'box_id': servico.box_id,
                'status': servico.status,
                'inicio': servico_dict['horario_inicio'],
                'fim_previsto': servico_dict['horario_fim_previsto'],
                'tempo_decorrido': servico_dict['tempo_decorrido_formatado'],
                'tempo_execucao_efetivo': servico_dict['tempo_execucao_formatado'],
                'tempo_restante': servico_dict['tempo_restante_formatado'],
                'percentual_conclusao': servico_dict['percentual_conclusao'],
                'em_atraso': servico_dict['em_atraso'],
                'pausado': servico.status == 'pausado'
            }
            
            if servico.status == 'pausado':
                teste_servico['tempo_pausa_atual'] = servico_dict.get('tempo_pausa_atual_formatado', 'N/A')
            
            if servico_dict['em_atraso']:
                teste_servico['tempo_atraso'] = servico_dict['tempo_atraso_formatado']
            
            resultado.append(teste_servico)
        
        return jsonify({
            'total_servicos_testados': len(resultado),
            'servicos': resultado,
            'timestamp': datetime.utcnow().isoformat(),
            'observacao': 'Todos os tempos são calculados em tempo real'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calcular_performance_hoje():
    """Calcula métricas de performance do dia"""
    hoje = date.today()
    inicio_dia = datetime.combine(hoje, datetime.min.time())
    
    servicos_concluidos = ServicoExecucao.query.filter_by(status='concluido').filter(
        ServicoExecucao.fim_real >= inicio_dia
    ).all()
    
    if not servicos_concluidos:
        return {
            'servicos_concluidos': 0,
            'tempo_medio_execucao_minutos': 0,
            'tempo_total_produtivo_minutos': 0,
            'eficiencia_media_percentual': 0
        }
    
    tempos_execucao = []
    tempo_total_produtivo = 0
    eficiencias = []
    
    for servico in servicos_concluidos:
        if servico.inicio and servico.fim_real:
            # Tempo total de execução
            tempo_total = (servico.fim_real - servico.inicio).total_seconds() / 60
            
            # Tempo efetivo (excluindo pausas)
            tempo_efetivo = tempo_total - (servico.tempo_pausado_total or 0)
            tempo_efetivo = max(0, tempo_efetivo)
            
            tempos_execucao.append(tempo_efetivo)
            tempo_total_produtivo += tempo_efetivo
            
            # Calcular eficiência em relação ao tempo estimado
            if servico.tipo_servico:
                tempo_estimado = servico.tipo_servico.tempo_estimado + (servico.tempo_extra_minutos or 0)
                if tempo_estimado > 0:
                    eficiencia = min(100, (tempo_estimado / tempo_efetivo) * 100)
                    eficiencias.append(eficiencia)
    
    tempo_medio = int(sum(tempos_execucao) / len(tempos_execucao)) if tempos_execucao else 0
    eficiencia_media = int(sum(eficiencias) / len(eficiencias)) if eficiencias else 0
    
    return {
        'servicos_concluidos': len(servicos_concluidos),
        'tempo_medio_execucao_minutos': tempo_medio,
        'tempo_total_produtivo_minutos': int(tempo_total_produtivo),
        'eficiencia_media_percentual': eficiencia_media,
        'tempo_medio_formatado': formatar_tempo_minutos(tempo_medio),
        'tempo_total_formatado': formatar_tempo_minutos(int(tempo_total_produtivo))
    }

def formatar_tempo_minutos(minutos):
    """Formata tempo em minutos"""
    if minutos < 60:
        return f"{minutos}min"
    else:
        horas = minutos // 60
        mins = minutos % 60
        if mins == 0:
            return f"{horas}h"
        else:
            return f"{horas}h {mins}min"

@diagnostico_bp.route('/diagnostico/reset-box/<int:box_id>', methods=['POST'])
def reset_box(box_id):
    """Reset de emergência de um box específico"""
    try:
        box = Box.query.get_or_404(box_id)
        data = request.get_json() or {}
        forcar = data.get('forcar', False)
        
        # Verificar se há serviços ativos
        servicos_ativos = ServicoExecucao.query.filter_by(box_id=box_id).filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).all()
        
        if servicos_ativos and not forcar:
            return jsonify({
                'erro': 'Box possui serviços ativos',
                'servicos_ativos': [s.to_dict() for s in servicos_ativos],
                'acao_necessaria': 'Finalize ou cancele os serviços ativos, ou use { "forcar": true }'
            }), 400
        
        acoes_realizadas = []
        
        # Cancelar serviços ativos se forçado
        if forcar and servicos_ativos:
            for servico in servicos_ativos:
                servico.status = 'cancelado'
                servico.fim_real = datetime.utcnow()
                servico.observacoes = (servico.observacoes or '') + f'\n[RESET FORÇADO em {datetime.utcnow().strftime("%d/%m/%Y %H:%M")}]'
                acoes_realizadas.append(f'Serviço {servico.id} cancelado')
        
        # Limpar fila do box
        servicos_fila = FilaServico.query.filter_by(box_id=box_id, status='agendado').all()
        if servicos_fila:
            for servico in servicos_fila:
                db.session.delete(servico)
                acoes_realizadas.append(f'Serviço da fila {servico.id} removido')
        
        # Liberar box
        box.status = 'livre'
        acoes_realizadas.append(f'Box {box_id} liberado')
        
        db.session.commit()
        
        return jsonify({
            'message': f'Box {box_id} resetado com sucesso',
            'acoes_realizadas': acoes_realizadas,
            'box_status': box.status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diagnostico_bp.route('/diagnostico/limpar-dados-teste', methods=['POST'])
def limpar_dados_teste():
    """Remove dados de teste do sistema (CUIDADO!)"""
    try:
        data = request.get_json() or {}
        confirmacao = data.get('confirmacao')
        
        if confirmacao != 'CONFIRMO_EXCLUSAO_DADOS_TESTE':
            return jsonify({
                'erro': 'Confirmação necessária',
                'instrucao': 'Envie { "confirmacao": "CONFIRMO_EXCLUSAO_DADOS_TESTE" }'
            }), 400
        
        # Contar dados antes
        count_execucao = ServicoExecucao.query.count()
        count_fila = FilaServico.query.count()
        
        # Remover apenas dados de teste (pode ajustar critérios)
        # Por exemplo: serviços criados hoje ou com nomes de teste
        hoje = date.today()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        
        # Remover serviços de execução criados hoje
        servicos_teste = ServicoExecucao.query.filter(
            db.or_(
                ServicoExecucao.criado_em >= inicio_dia,
                ServicoExecucao.nome_cliente.like('%teste%'),
                ServicoExecucao.nome_cliente.like('%Test%')
            )
        ).all()
        
        for servico in servicos_teste:
            db.session.delete(servico)
        
        # Remover fila de teste
        fila_teste = FilaServico.query.filter(
            db.or_(
                FilaServico.criado_em >= inicio_dia,
                FilaServico.nome_cliente.like('%teste%'),
                FilaServico.nome_cliente.like('%Test%')
            )
        ).all()
        
        for servico in fila_teste:
            db.session.delete(servico)
        
        # Liberar todos os boxes
        boxes = Box.query.all()
        for box in boxes:
            box.status = 'livre'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Dados de teste removidos',
            'servicos_execucao_removidos': len(servicos_teste),
            'servicos_fila_removidos': len(fila_teste),
            'boxes_liberados': len(boxes),
            'dados_antes': {
                'execucao': count_execucao,
                'fila': count_fila
            },
            'dados_depois': {
                'execucao': ServicoExecucao.query.count(),
                'fila': FilaServico.query.count()
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diagnostico_bp.route('/diagnostico/criar-dados-teste', methods=['POST'])
def criar_dados_teste():
    """Cria dados de teste para desenvolvimento"""
    try:
        data = request.get_json() or {}
        quantidade = data.get('quantidade', 3)
        
        if quantidade > 10:
            return jsonify({'erro': 'Máximo 10 serviços de teste por vez'}), 400
        
        # Buscar boxes disponíveis
        boxes_livres = Box.query.filter_by(status='livre').all()
        if not boxes_livres:
            return jsonify({'erro': 'Nenhum box livre disponível'}), 400
        
        # Buscar mecânicos e tipos de serviço
        from src.models.mecanico import Mecanico
        from src.models.tipo_servico import TipoServico
        
        mecanicos = Mecanico.query.all()
        tipos_servico = TipoServico.query.all()
        
        if not mecanicos or not tipos_servico:
            return jsonify({'erro': 'É necessário ter mecânicos e tipos de serviço cadastrados'}), 400
        
        servicos_criados = []
        
        for i in range(min(quantidade, len(boxes_livres))):
            box = boxes_livres[i]
            mecanico = mecanicos[i % len(mecanicos)]
            tipo_servico = tipos_servico[i % len(tipos_servico)]
            
            # Criar serviço de teste
            inicio = datetime.utcnow()
            tempo_estimado = tipo_servico.tempo_estimado
            fim_previsto = inicio + datetime.timedelta(minutes=tempo_estimado)
            
            servico = ServicoExecucao(
                box_id=box.id,
                mecanico_id=mecanico.id,
                tipo_servico_id=tipo_servico.id,
                inicio=inicio,
                fim_previsto=fim_previsto,
                nome_cliente=f'Cliente Teste {i+1}',
                telefone_cliente=f'(11) 9999-{1000+i}',
                marca_carro='Volkswagen',
                modelo_carro='Gol',
                cor_carro='Branco',
                placa_carro=f'TST{i+1:04d}',
                observacoes=f'Serviço de teste criado em {datetime.utcnow().strftime("%d/%m/%Y %H:%M")}',
                status='em_andamento'
            )
            
            # Ocupar box
            box.status = 'ocupado'
            
            db.session.add(servico)
            servicos_criados.append({
                'box_id': box.id,
                'cliente': servico.nome_cliente,
                'tipo_servico': tipo_servico.nome,
                'mecanico': mecanico.nome
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(servicos_criados)} serviços de teste criados',
            'servicos': servicos_criados,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diagnostico_bp.route('/diagnostico/health', methods=['GET'])
def health_check():
    """Verificação simples de saúde do sistema"""
    try:
        # Teste de conexão com banco
        db.session.execute('SELECT 1')
        
        # Contadores básicos
        total_servicos = ServicoExecucao.query.count()
        servicos_ativos = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'servicos_total': total_servicos,
            'servicos_ativos': servicos_ativos,
            'uptime': 'N/A'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500