# src/routes/diagnostico_simples.py - VERSÃO CORRIGIDA COM CONTEXTO
from flask import Blueprint, jsonify, request, current_app
from src.models.user import db
from src.models.servico_execucao import ServicoExecucao
from src.models.box import Box
from datetime import datetime, timedelta
import traceback

diag_bp = Blueprint('diag', __name__)

@diag_bp.route('/debug/info', methods=['GET'])
def debug_info():
    """Informações básicas do sistema - sem autenticação"""
    try:
        # Teste básico de banco
        total_servicos = ServicoExecucao.query.count()
        total_boxes = Box.query.count()
        
        # Teste de um serviço
        primeiro_servico = ServicoExecucao.query.first()
        servico_info = None
        erro_to_dict = None
        
        if primeiro_servico:
            try:
                servico_info = primeiro_servico.to_dict()
            except Exception as e:
                erro_to_dict = str(e)
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'banco': {
                'total_servicos': total_servicos,
                'total_boxes': total_boxes,
                'primeiro_servico_id': primeiro_servico.id if primeiro_servico else None
            },
            'model': {
                'to_dict_funciona': erro_to_dict is None,
                'erro_to_dict': erro_to_dict,
                'tem_primeiro_servico': primeiro_servico is not None
            },
            'servico_exemplo': servico_info if servico_info else 'Nenhum serviço ou erro no to_dict()'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@diag_bp.route('/debug/fix-database', methods=['POST'])
def fix_database_via_api():
    """Corrige banco via API - VERSÃO COM CONTEXTO CORRIGIDO"""
    try:
        data = request.get_json() or {}
        senha = data.get('senha', '')
        
        # Senha simples para evitar execução acidental
        if senha != 'fix123':
            return jsonify({'erro': 'Senha necessária. Use {"senha": "fix123"}'}), 401
        
        correcoes = []
        
        # CORREÇÃO: Usar o contexto atual da aplicação
        with current_app.app_context():
            from sqlalchemy import text
            
            # 1. Verificar e adicionar campos faltantes
            campos_para_verificar = [
                'historico_pausas',
                'criado_em', 
                'atualizado_em',
                'tempo_pausado_total',
                'tempo_extra_minutos'
            ]
            
            for campo in campos_para_verificar:
                try:
                    # Testar se campo existe
                    db.session.execute(text(f'SELECT {campo} FROM servico_execucao LIMIT 1'))
                    correcoes.append(f'✅ Campo {campo} já existe')
                except Exception as e:
                    if 'column' in str(e).lower() and 'does not exist' in str(e).lower():
                        # Campo não existe, tentar adicionar
                        try:
                            if campo == 'historico_pausas':
                                db.session.execute(text(f'ALTER TABLE servico_execucao ADD COLUMN {campo} TEXT'))
                            elif campo in ['criado_em', 'atualizado_em']:
                                db.session.execute(text(f'ALTER TABLE servico_execucao ADD COLUMN {campo} TIMESTAMP'))
                            else:
                                db.session.execute(text(f'ALTER TABLE servico_execucao ADD COLUMN {campo} INTEGER DEFAULT 0'))
                            
                            correcoes.append(f'✅ Campo {campo} adicionado')
                        except Exception as add_error:
                            correcoes.append(f'❌ Erro ao adicionar {campo}: {str(add_error)}')
                    else:
                        correcoes.append(f'❌ Erro ao verificar {campo}: {str(e)}')
            
            # 2. Corrigir valores NULL - usando UPDATE direto sem IF EXISTS
            updates_sql = [
                "UPDATE servico_execucao SET tempo_pausado_total = 0 WHERE tempo_pausado_total IS NULL",
                "UPDATE servico_execucao SET tempo_extra_minutos = 0 WHERE tempo_extra_minutos IS NULL"
            ]
            
            # Tentar atualizar criado_em apenas se o campo existir
            try:
                db.session.execute(text("UPDATE servico_execucao SET criado_em = inicio WHERE criado_em IS NULL AND inicio IS NOT NULL"))
                correcoes.append("✅ Campo criado_em atualizado")
            except:
                correcoes.append("⚠️ Campo criado_em não pôde ser atualizado (pode não existir)")
            
            for update_sql in updates_sql:
                try:
                    result = db.session.execute(text(update_sql))
                    correcoes.append(f'✅ {update_sql} - {result.rowcount} linhas afetadas')
                except Exception as e:
                    correcoes.append(f'❌ {update_sql} - Erro: {str(e)}')
            
            # 3. Corrigir inconsistências de status sem usar métodos complexos
            try:
                # Buscar serviços pausados sem data usando SQL direto
                servicos_problema = db.session.execute(text(
                    "SELECT id FROM servico_execucao WHERE status = 'pausado' AND pausado_em IS NULL"
                )).fetchall()
                
                if servicos_problema:
                    # Corrigir usando UPDATE SQL direto
                    db.session.execute(text(
                        "UPDATE servico_execucao SET status = 'em_andamento', pausado_em = NULL WHERE status = 'pausado' AND pausado_em IS NULL"
                    ))
                    correcoes.append(f'✅ Corrigidos {len(servicos_problema)} serviços pausados sem data')
                else:
                    correcoes.append('✅ Nenhum serviço pausado sem data encontrado')
                    
            except Exception as e:
                correcoes.append(f'❌ Erro ao corrigir status: {str(e)}')
            
            # 4. Sincronizar boxes usando SQL direto
            try:
                # Liberar boxes que não têm serviço ativo
                db.session.execute(text("""
                    UPDATE box SET status = 'livre' 
                    WHERE status = 'ocupado' 
                    AND id NOT IN (
                        SELECT DISTINCT box_id FROM servico_execucao 
                        WHERE status IN ('em_andamento', 'pausado')
                    )
                """))
                
                # Ocupar boxes que têm serviço em andamento
                db.session.execute(text("""
                    UPDATE box SET status = 'ocupado' 
                    WHERE status = 'livre' 
                    AND id IN (
                        SELECT DISTINCT box_id FROM servico_execucao 
                        WHERE status = 'em_andamento'
                    )
                """))
                
                correcoes.append('✅ Status dos boxes sincronizado')
                
            except Exception as e:
                correcoes.append(f'❌ Erro ao sincronizar boxes: {str(e)}')
            
            # Commit das alterações
            db.session.commit()
        
        return jsonify({
            'status': 'sucesso',
            'correcoes_aplicadas': len([c for c in correcoes if c.startswith('✅')]),
            'detalhes': correcoes,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'erro',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@diag_bp.route('/debug/test-servico/<int:servico_id>', methods=['GET'])
def test_servico(servico_id):
    """Testa um serviço específico"""
    try:
        servico = ServicoExecucao.query.get(servico_id)
        if not servico:
            return jsonify({'erro': f'Serviço {servico_id} não encontrado'}), 404
        
        # Testar to_dict()
        try:
            servico_dict = servico.to_dict()
            to_dict_ok = True
            to_dict_erro = None
        except Exception as e:
            to_dict_ok = False
            to_dict_erro = str(e)
            servico_dict = None
        
        # Informações básicas usando getattr para campos que podem não existir
        info_basica = {
            'id': servico.id,
            'status': servico.status,
            'inicio': servico.inicio.isoformat() if servico.inicio else None,
            'pausado_em': servico.pausado_em.isoformat() if servico.pausado_em else None,
            'fim_previsto': servico.fim_previsto.isoformat() if servico.fim_previsto else None,
            'tempo_pausado_total': getattr(servico, 'tempo_pausado_total', 'Campo não existe'),
            'tempo_extra_minutos': getattr(servico, 'tempo_extra_minutos', 'Campo não existe'),
            'criado_em': getattr(servico, 'criado_em', 'Campo não existe'),
            'historico_pausas': getattr(servico, 'historico_pausas', 'Campo não existe')
        }
        
        return jsonify({
            'servico_id': servico_id,
            'to_dict_funciona': to_dict_ok,
            'to_dict_erro': to_dict_erro,
            'info_basica': info_basica,
            'servico_completo': servico_dict,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@diag_bp.route('/debug/create-test-servico', methods=['POST'])
def create_test_servico():
    """Cria um serviço de teste"""
    try:
        # Buscar primeiro box livre
        box = Box.query.filter_by(status='livre').first()
        if not box:
            return jsonify({'erro': 'Nenhum box livre disponível'}), 400
        
        # Buscar mecânico e tipo de serviço
        try:
            from src.models.mecanico import Mecanico
            from src.models.tipo_servico import TipoServico
            
            mecanico = Mecanico.query.first()
            tipo_servico = TipoServico.query.first()
        except ImportError:
            # Se não conseguir importar, usar IDs fixos
            mecanico = None
            tipo_servico = None
        
        if not mecanico or not tipo_servico:
            return jsonify({'erro': 'Mecânico ou tipo de serviço não encontrado'}), 400
        
        # Criar serviço básico
        inicio = datetime.utcnow()
        fim_previsto = inicio + timedelta(minutes=60)  # 1 hora padrão
        
        servico = ServicoExecucao(
            box_id=box.id,
            mecanico_id=mecanico.id,
            tipo_servico_id=tipo_servico.id,
            inicio=inicio,
            fim_previsto=fim_previsto,
            nome_cliente='Cliente Teste Debug',
            marca_carro='VW',
            modelo_carro='Gol',
            status='em_andamento'
        )
        
        # Definir campos extras se existirem
        if hasattr(servico, 'tempo_pausado_total'):
            servico.tempo_pausado_total = 0
        if hasattr(servico, 'tempo_extra_minutos'):
            servico.tempo_extra_minutos = 0
        
        box.status = 'ocupado'
        
        db.session.add(servico)
        db.session.commit()
        
        return jsonify({
            'status': 'sucesso',
            'servico_criado': servico.id,
            'box_ocupado': box.id,
            'pode_testar_pause': True,
            'url_teste': f'/api/debug/test-servico/{servico.id}',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@diag_bp.route('/debug/fix-simple', methods=['POST'])
def fix_simple():
    """Correção mais simples, sem verificar se campos existem"""
    try:
        data = request.get_json() or {}
        senha = data.get('senha', '')
        
        if senha != 'fix123':
            return jsonify({'erro': 'Senha necessária. Use {"senha": "fix123"}'}), 401
        
        correcoes = []
        from sqlalchemy import text
        
        # Apenas corrigir valores NULL em campos que sabemos que existem
        updates_basicos = [
            "UPDATE servico_execucao SET tempo_pausado_total = 0 WHERE tempo_pausado_total IS NULL",
            "UPDATE servico_execucao SET tempo_extra_minutos = 0 WHERE tempo_extra_minutos IS NULL",
            "UPDATE servico_execucao SET status = 'em_andamento' WHERE status = 'pausado' AND pausado_em IS NULL"
        ]
        
        for update_sql in updates_basicos:
            try:
                result = db.session.execute(text(update_sql))
                correcoes.append(f'✅ {update_sql} - {result.rowcount} linhas afetadas')
            except Exception as e:
                correcoes.append(f'❌ {update_sql} - Erro: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'status': 'sucesso',
            'correcoes_aplicadas': len([c for c in correcoes if c.startswith('✅')]),
            'detalhes': correcoes,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'erro',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
