# src/routes/servico_execucao.py - VERSÃO CORRIGIDA SEM ERROS DE SINTAXE
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
        # CORRIGIDO: Buscar TODOS os status, não só em_andamento
        status_filter = request.args.get('status')
        if status_filter:
            servicos = ServicoExecucao.query.filter_by(status=status_filter).all()
        else:
            # Por padrão, buscar em andamento e pausados
            servicos = ServicoExecucao.query.filter(
                ServicoExecucao.status.in_(['em_andamento', 'pausado'])
            ).all()
        
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/todos', methods=['GET'])
def get_todos_servicos():
    """Busca todos os serviços independente do status"""
    try:
        servicos = ServicoExecucao.query.order_by(ServicoExecucao.criado_em.desc()).all()
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/concluidos', methods=['GET'])
def get_servicos_concluidos():
    """Lista serviços concluídos"""
    try:
        servicos = ServicoExecucao.query.filter_by(
            status='concluido'
        ).order_by(ServicoExecucao.fim_real.desc()).all()
        
        return jsonify([servico.to_dict() for servico in servicos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao', methods=['POST'])
def create_servico_execucao():
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['box_id', 'mecanico_id', 'tipo_servico_id', 'nome_cliente', 'marca_carro', 'modelo_carro']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'error': f'Campo obrigatório: {campo}'}), 400
        
        # Buscar o tipo de serviço para calcular o fim previsto
        tipo_servico = TipoServico.query.get(data['tipo_servico_id'])
        if not tipo_servico:
            return jsonify({'error': 'Tipo de serviço não encontrado'}), 404
        
        # Verificar se box está disponível
        box = Box.query.get(data['box_id'])
        if not box:
            return jsonify({'error': 'Box não encontrado'}), 404
        
        if box.status != 'livre':
            return jsonify({'error': 'Box não está disponível'}), 400
        
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
            observacoes=data.get('observacoes'),
            status='em_andamento'
        )
        
        db.session.add(servico)
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço iniciado com sucesso',
            'servico': servico.to_dict()
        }), 201
        
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
        data = request.get_json() or {}
        motivo = data.get('motivo', 'Motivo não informado')
        
        if servico.status != 'em_andamento':
            return jsonify({'error': 'Serviço não está em andamento'}), 400
        
        # Usar o método da model se existir, senão fazer manualmente
        agora = datetime.utcnow()
        servico.status = 'pausado'
        servico.pausado_em = agora
        
        # Atualizar status do box para livre
        box = Box.query.get(servico.box_id)
        if box:
            box.status = 'livre'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço pausado com sucesso',
            'pausado_em': agora.isoformat(),
            'motivo': motivo,
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
        tempo_pausado_minutos = 0
        if servico.pausado_em:
            tempo_pausado = agora - servico.pausado_em
            tempo_pausado_minutos = int(tempo_pausado.total_seconds() / 60)
            
            # Adicionar tempo pausado ao total
            if not servico.tempo_pausado_total:
                servico.tempo_pausado_total = 0
            servico.tempo_pausado_total += tempo_pausado_minutos
            
            # Ajustar o fim previsto adicionando o tempo que ficou pausado
            if servico.fim_previsto:
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
            'novo_fim_previsto': servico.fim_previsto.isoformat() if servico.fim_previsto else None,
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
        data = request.get_json() or {}
        observacoes_finais = data.get('observacoes_finais')
        
        if servico.status not in ['em_andamento', 'pausado']:
            return jsonify({'error': 'Serviço não pode ser finalizado'}), 400
        
        box_id = servico.box_id
        agora = datetime.utcnow()
        
        # Adicionar observações finais se fornecidas
        if observacoes_finais:
            observacoes_atuais = servico.observacoes or ''
            servico.observacoes = f"{observacoes_atuais}\n\nObservações finais: {observacoes_finais}".strip()
        
        # Se estava pausado, calcular último tempo de pausa
        if servico.status == 'pausado' and servico.pausado_em:
            tempo_pausado = int((agora - servico.pausado_em).total_seconds() / 60)
            if not servico.tempo_pausado_total:
                servico.tempo_pausado_total = 0
            servico.tempo_pausado_total += tempo_pausado
        
        # Finalizar serviço
        servico.fim_real = agora
        servico.status = 'concluido'
        servico.pausado_em = None
        
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
            'finalizado_em': agora.isoformat(),
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
                response_data['message'] += ' (erro ao iniciar próximo automaticamente)'
        else:
            response_data['message'] += ' (nenhum serviço na fila)'
        
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
        tempo_total_minutos = tipo_servico.tempo_estimado + (proximo_servico.tempo_extra_minutos or 0)
        fim_previsto = inicio + timedelta(minutes=tempo_total_minutos)
        
        # Criar novo serviço em execução
        novo_servico = ServicoExecucao(
            box_id=proximo_servico.box_id,
            mecanico_id=proximo_servico.mecanico_id,
            tipo_servico_id=proximo_servico.tipo_servico_id,
            inicio=inicio,
            fim_previsto=fim_previsto,
            tempo_extra_minutos=proximo_servico.tempo_extra_minutos or 0,
            motivo_tempo_extra=proximo_servico.motivo_tempo_extra,
            nome_cliente=proximo_servico.nome_cliente,
            telefone_cliente=proximo_servico.telefone_cliente,
            marca_carro=proximo_servico.marca_carro,
            modelo_carro=proximo_servico.modelo_carro,
            cor_carro=proximo_servico.cor_carro,
            placa_carro=proximo_servico.placa_carro,
            observacoes=proximo_servico.observacoes,
            status='em_andamento'
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
        
        db.session.add(novo_servico)
        db.session.commit()
        
        return novo_servico.to_dict()
        
    except Exception as e:
        db.session.rollback()
        raise e

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['PUT'])
def update_servico_execucao(id):
    """Atualiza informações de um serviço"""
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        data = request.get_json()
        
        # Campos editáveis
        campos_editaveis = [
            'observacoes', 'tempo_extra_minutos', 'motivo_tempo_extra',
            'telefone_cliente', 'cor_carro', 'placa_carro'
        ]
        
        alterou_tempo = False
        for campo in campos_editaveis:
            if campo in data:
                valor_anterior = getattr(servico, campo)
                setattr(servico, campo, data[campo])
                
                if campo == 'tempo_extra_minutos' and valor_anterior != data[campo]:
                    alterou_tempo = True
        
        # Se alterou tempo extra, recalcular fim previsto
        if alterou_tempo and servico.status in ['em_andamento', 'pausado'] and servico.tipo_servico:
            tempo_ja_decorrido = 0
            if servico.inicio:
                agora = datetime.utcnow()
                tempo_ja_decorrido = (agora - servico.inicio).total_seconds() / 60
                
                # Subtrair tempo pausado
                if servico.tempo_pausado_total:
                    tempo_ja_decorrido -= servico.tempo_pausado_total
                
                # Se está pausado, subtrair tempo da pausa atual
                if servico.status == 'pausado' and servico.pausado_em:
                    tempo_pausa_atual = (agora - servico.pausado_em).total_seconds() / 60
                    tempo_ja_decorrido -= tempo_pausa_atual
            
            # Calcular novo fim previsto
            tempo_total_necessario = servico.tipo_servico.tempo_estimado + (servico.tempo_extra_minutos or 0)
            tempo_restante = max(0, tempo_total_necessario - tempo_ja_decorrido)
            
            if servico.status == 'em_andamento':
                servico.fim_previsto = datetime.utcnow() + timedelta(minutes=tempo_restante)
        
        db.session.commit()
        
        response_data = {
            'message': 'Serviço atualizado com sucesso',
            'servico': servico.to_dict()
        }
        
        if alterou_tempo:
            response_data['message'] += ' e tempo recalculado'
            response_data['novo_fim_previsto'] = servico.fim_previsto.isoformat() if servico.fim_previsto else None
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/<int:id>', methods=['DELETE'])
def delete_servico_execucao(id):
    try:
        servico = ServicoExecucao.query.get_or_404(id)
        
        # Liberar o box se o serviço estava em andamento ou pausado
        if servico.status in ['em_andamento', 'pausado']:
            box = Box.query.get(servico.box_id)
            if box:
                box.status = 'livre'
        
        db.session.delete(servico)
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço deletado com sucesso',
            'id': id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servico_execucao_bp.route('/servicos-execucao/box/<int:box_id>', methods=['GET'])
def get_servico_por_box(box_id):
    """Busca serviço ativo (em andamento ou pausado) de um box específico"""
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
    """Lista todos os serviços pausados com informações detalhadas"""
    try:
        box_id = request.args.get('box_id')
        
        query = ServicoExecucao.query.filter_by(status='pausado')
        if box_id:
            query = query.filter_by(box_id=int(box_id))
        
        servicos_pausados = query.order_by(ServicoExecucao.pausado_em.desc()).all()
        
        resultado = []
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
                elif tempo_pausa_atual > 60:  # Mais de 1 hora
                    servico_dict['urgencia_pausa'] = 'alta'
                elif tempo_pausa_atual > 30:  # Mais de 30 minutos
                    servico_dict['urgencia_pausa'] = 'media'
                else:
                    servico_dict['urgencia_pausa'] = 'baixa'
            
            resultado.append(servico_dict)
        
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

@servico_execucao_bp.route('/servicos-execucao/estatisticas', methods=['GET'])
def get_estatisticas_gerais():
    """Retorna estatísticas gerais dos serviços"""
    try:
        hoje = datetime.now().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        fim_dia = datetime.combine(hoje, datetime.max.time())
        
        # Contar serviços por status
        em_andamento = ServicoExecucao.query.filter_by(status='em_andamento').count()
        pausados = ServicoExecucao.query.filter_by(status='pausado').count()
        concluidos_hoje = ServicoExecucao.query.filter_by(status='concluido').filter(
            ServicoExecucao.fim_real >= inicio_dia,
            ServicoExecucao.fim_real <= fim_dia
        ).count()
        
        # Tempo médio dos serviços concluídos hoje
        servicos_concluidos = ServicoExecucao.query.filter_by(status='concluido').filter(
            ServicoExecucao.fim_real >= inicio_dia,
            ServicoExecucao.fim_real <= fim_dia
        ).all()
        
        tempo_medio_execucao = 0
        if servicos_concluidos:
            tempos = []
            for servico in servicos_concluidos:
                if servico.inicio and servico.fim_real:
                    tempo_total = (servico.fim_real - servico.inicio).total_seconds() / 60
                    tempo_efetivo = tempo_total - (servico.tempo_pausado_total or 0)
                    tempos.append(max(0, tempo_efetivo))
            
            if tempos:
                tempo_medio_execucao = int(sum(tempos) / len(tempos))
        
        # Boxes ocupados
        boxes_ocupados = ServicoExecucao.query.filter(
            ServicoExecucao.status.in_(['em_andamento', 'pausado'])
        ).with_entities(ServicoExecucao.box_id).distinct().count()
        
        return jsonify({
            'em_andamento': em_andamento,
            'pausados': pausados,
            'concluidos_hoje': concluidos_hoje,
            'boxes_ocupados': boxes_ocupados,
            'tempo_medio_execucao_minutos': tempo_medio_execucao,
            'tempo_medio_execucao_formatado': formatar_tempo_minutos(tempo_medio_execucao),
            'data_referencia': hoje.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Adicione esta rota temporária em src/routes/servico_execucao.py

@servico_execucao_bp.route('/corrigir-banco-dados', methods=['POST'])
def corrigir_banco_dados():
    """ENDPOINT TEMPORÁRIO - Corrige problemas no banco de dados"""
    try:
        data = request.get_json() or {}
        senha = data.get('senha', '')
        
        # Senha de segurança
        if senha != 'corrigir2025':
            return jsonify({'erro': 'Senha necessária para correção'}), 401
        
        from sqlalchemy import text
        correcoes = []
        
        # 1. Verificar e adicionar campos faltantes na tabela servico_execucao
        try:
            db.session.execute(text('ALTER TABLE servico_execucao ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
            correcoes.append('✅ Campo criado_em verificado/adicionado')
        except Exception as e:
            correcoes.append(f'ℹ️ Campo criado_em: {str(e)}')
        
        try:
            db.session.execute(text('ALTER TABLE servico_execucao ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
            correcoes.append('✅ Campo atualizado_em verificado/adicionado')
        except Exception as e:
            correcoes.append(f'ℹ️ Campo atualizado_em: {str(e)}')
        
        try:
            db.session.execute(text('ALTER TABLE servico_execucao ADD COLUMN IF NOT EXISTS historico_pausas TEXT'))
            correcoes.append('✅ Campo historico_pausas verificado/adicionado')
        except Exception as e:
            correcoes.append(f'ℹ️ Campo historico_pausas: {str(e)}')
        
        # 2. Corrigir valores NULL que causam NaN
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao 
                SET tempo_pausado_total = 0 
                WHERE tempo_pausado_total IS NULL
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} registros tempo_pausado_total NULL')
        except Exception as e:
            correcoes.append(f'❌ Erro tempo_pausado_total: {e}')
        
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao 
                SET tempo_extra_minutos = 0 
                WHERE tempo_extra_minutos IS NULL
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} registros tempo_extra_minutos NULL')
        except Exception as e:
            correcoes.append(f'❌ Erro tempo_extra_minutos: {e}')
        
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao 
                SET criado_em = inicio 
                WHERE criado_em IS NULL AND inicio IS NOT NULL
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} registros criado_em NULL')
        except Exception as e:
            correcoes.append(f'❌ Erro criado_em: {e}')
        
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao 
                SET atualizado_em = COALESCE(fim_real, pausado_em, inicio, CURRENT_TIMESTAMP) 
                WHERE atualizado_em IS NULL
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} registros atualizado_em NULL')
        except Exception as e:
            correcoes.append(f'❌ Erro atualizado_em: {e}')
        
        # 3. Corrigir inconsistências de status que causam problemas
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao 
                SET status = 'em_andamento', pausado_em = NULL 
                WHERE status = 'pausado' AND pausado_em IS NULL
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} serviços pausados sem data de pausa')
        except Exception as e:
            correcoes.append(f'❌ Erro status pausado: {e}')
        
        # 4. Sincronizar status dos boxes
        try:
            # Liberar boxes que não têm serviço ativo
            result = db.session.execute(text('''
                UPDATE box 
                SET status = 'livre' 
                WHERE status = 'ocupado' 
                AND id NOT IN (
                    SELECT DISTINCT box_id 
                    FROM servico_execucao 
                    WHERE status IN ('em_andamento', 'pausado')
                )
            '''))
            correcoes.append(f'✅ Liberados {result.rowcount} boxes sem serviço ativo')
        except Exception as e:
            correcoes.append(f'❌ Erro sincronização boxes: {e}')
        
        try:
            # Ocupar boxes que têm serviço ativo
            result = db.session.execute(text('''
                UPDATE box 
                SET status = 'ocupado' 
                WHERE status = 'livre' 
                AND id IN (
                    SELECT DISTINCT box_id 
                    FROM servico_execucao 
                    WHERE status IN ('em_andamento', 'pausado')
                )
            '''))
            correcoes.append(f'✅ Ocupados {result.rowcount} boxes com serviço ativo')
        except Exception as e:
            correcoes.append(f'❌ Erro ocupação boxes: {e}')
        
        # 5. Corrigir fim_previsto para serviços sem essa informação
        try:
            result = db.session.execute(text('''
                UPDATE servico_execucao se
                SET fim_previsto = se.inicio + INTERVAL '1 hour' * (
                    COALESCE(ts.tempo_estimado, 60) + COALESCE(se.tempo_extra_minutos, 0)
                ) / 60
                FROM tipo_servico ts
                WHERE se.tipo_servico_id = ts.id 
                AND se.fim_previsto IS NULL 
                AND se.inicio IS NOT NULL
                AND se.status IN ('em_andamento', 'pausado')
            '''))
            correcoes.append(f'✅ Corrigidos {result.rowcount} registros fim_previsto NULL')
        except Exception as e:
            # Fallback para bancos que não suportam INTERVAL
            try:
                result = db.session.execute(text('''
                    UPDATE servico_execucao 
                    SET fim_previsto = datetime(inicio, '+60 minutes')
                    WHERE fim_previsto IS NULL 
                    AND inicio IS NOT NULL
                    AND status IN ('em_andamento', 'pausado')
                '''))
                correcoes.append(f'✅ Corrigidos {result.rowcount} registros fim_previsto NULL (fallback)')
            except Exception as e2:
                correcoes.append(f'❌ Erro fim_previsto: {e} / {e2}')
        
        # 6. Commit das alterações
        db.session.commit()
        
        # 7. Verificar resultado final
        try:
            result = db.session.execute(text('SELECT COUNT(*) FROM servico_execucao')).fetchone()
            total_servicos = result[0] if result else 0
            
            result = db.session.execute(text('''
                SELECT COUNT(*) FROM servico_execucao 
                WHERE tempo_pausado_total IS NOT NULL 
                AND tempo_extra_minutos IS NOT NULL
            ''')).fetchone()
            registros_validos = result[0] if result else 0
            
            result = db.session.execute(text('''
                SELECT COUNT(*) FROM servico_execucao 
                WHERE status IN ('em_andamento', 'pausado')
            ''')).fetchone()
            servicos_ativos = result[0] if result else 0
            
            correcoes.append(f'📊 Total de serviços: {total_servicos}')
            correcoes.append(f'📊 Registros com dados válidos: {registros_validos}')
            correcoes.append(f'📊 Serviços ativos: {servicos_ativos}')
            
        except Exception as e:
            correcoes.append(f'❌ Erro na verificação final: {e}')
        
        return jsonify({
            'status': 'sucesso',
            'correcoes': correcoes,
            'timestamp': datetime.utcnow().isoformat(),
            'instrucoes': [
                '1. Substitua o arquivo src/models/servico_execucao.py pelo código corrigido',
                '2. Reinicie a aplicação',
                '3. Teste o dashboard novamente',
                '4. Este endpoint pode ser removido após a correção'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'erro_critico',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'correcoes': correcoes if 'correcoes' in locals() else []
        }), 500
