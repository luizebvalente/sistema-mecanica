# src/models/servico_execucao.py - VERSÃO CORRIGIDA COMPLETA
from src.models.user import db
from datetime import datetime
import json
import math


class ServicoExecucao(db.Model):
    __tablename__ = 'servico_execucao'
    
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanico.id'), nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)
    
    # Horários
    inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fim_previsto = db.Column(db.DateTime)
    fim_real = db.Column(db.DateTime)
    pausado_em = db.Column(db.DateTime)
    
    # Controle de tempo
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    tempo_pausado_total = db.Column(db.Integer, default=0)
    motivo_tempo_extra = db.Column(db.String(200))
    
    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Histórico de pausas
    historico_pausas = db.Column(db.Text)
    
    # Dados do cliente
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone_cliente = db.Column(db.String(20))
    
    # Dados do veículo
    marca_carro = db.Column(db.String(50), nullable=False)
    modelo_carro = db.Column(db.String(50), nullable=False)
    cor_carro = db.Column(db.String(30))
    placa_carro = db.Column(db.String(10))
    
    # Status e observações
    status = db.Column(db.String(20), default='em_andamento')
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    box = db.relationship('Box', backref=db.backref('servicos_execucao', lazy=True))
    mecanico = db.relationship('Mecanico', backref=db.backref('servicos_execucao', lazy=True))
    tipo_servico = db.relationship('TipoServico', backref=db.backref('servicos_execucao', lazy=True))
    

    # PATCH PARA CORREÇÃO DO BACKEND - Cálculos de Tempo Seguros
# Aplicar essas correções no arquivo src/models/servico_execucao.py
       def to_dict(self):
    """Converte para dict com cálculos ULTRA seguros - VERSÃO FINAL CORRIGIDA"""
          agora = datetime.utcnow()
    
    # Função auxiliar para garantir valores numéricos válidos
            def safe_number(value, default=0):
        """Converte qualquer valor para número válido"""
            try:
            if value is None:
                return default
            if isinstance(value, (int, float)):
                if math.isnan(value) or math.isinf(value):
                    return default
                return max(0, int(value))
            if isinstance(value, str):
                if value.lower() in ['nan', 'none', 'null', '', 'undefined']:
                    return default
                # Tentar extrair número da string
                import re
                numbers = re.findall(r'-?\d+\.?\d*', value)
                if numbers:
                    num = float(numbers[0])
                    if math.isnan(num) or math.isinf(num):
                        return default
                    return max(0, int(num))
                return default
              except (ValueError, TypeError, AttributeError):
            return default
    
    # Função auxiliar para diferença de tempo segura
    def safe_time_diff(start_time, end_time=None):
        """Calcula diferença de tempo de forma segura"""
        try:
            if not start_time:
                return 0
            if not isinstance(start_time, datetime):
                return 0
            
            end = end_time if end_time else agora
            if not isinstance(end, datetime):
                return 0
                
            delta = end - start_time
            minutes = delta.total_seconds() / 60
            return safe_number(minutes)
        except Exception:
            return 0
    
    # INICIALIZAR TODOS OS VALORES COM PADRÕES SEGUROS
    tempo_decorrido_total = 0
    tempo_execucao_efetivo = 0
    tempo_restante = 0
    percentual_conclusao = 0
    em_atraso = False
    tempo_atraso = 0
    tempo_estimado_total = 60  # Default mínimo
    
    try:
        # 1. Calcular tempo decorrido total desde o início
        if self.inicio:
            tempo_decorrido_total = safe_time_diff(self.inicio, agora)
        
        # 2. Obter tempo estimado do tipo de serviço de forma segura
        tempo_estimado_base = 60  # Default
        if self.tipo_servico:
            if hasattr(self.tipo_servico, 'tempo_estimado') and self.tipo_servico.tempo_estimado:
                tempo_estimado_base = safe_number(self.tipo_servico.tempo_estimado, 60)
        
        tempo_extra_safe = safe_number(self.tempo_extra_minutos)
        tempo_estimado_total = tempo_estimado_base + tempo_extra_safe
        
        # Garantir tempo mínimo
        if tempo_estimado_total <= 0:
            tempo_estimado_total = 60
        
        # 3. Calcular tempo pausado atual se estiver pausado
        tempo_pausado_atual = 0
        if self.status == 'pausado' and self.pausado_em:
            tempo_pausado_atual = safe_time_diff(self.pausado_em, agora)
        
        # 4. Calcular tempo efetivo de execução
        tempo_pausado_total_safe = safe_number(self.tempo_pausado_total)
        tempo_execucao_efetivo = tempo_decorrido_total - tempo_pausado_total_safe - tempo_pausado_atual
        tempo_execucao_efetivo = max(0, tempo_execucao_efetivo)
        
        # 5. Calcular tempo restante e percentual
        tempo_restante = max(0, tempo_estimado_total - tempo_execucao_efetivo)
        
        # Percentual com proteção contra divisão por zero
        if tempo_estimado_total > 0:
            percentual_bruto = (tempo_execucao_efetivo / tempo_estimado_total) * 100
            percentual_conclusao = max(0, min(100, safe_number(percentual_bruto)))
        
        # 6. Verificar atraso (apenas se não estiver pausado)
        if self.fim_previsto and self.status == 'em_andamento':
            if agora > self.fim_previsto:
                em_atraso = True
                tempo_atraso = safe_time_diff(self.fim_previsto, agora)
    
    except Exception as e:
        print(f"ERRO CRÍTICO no cálculo de tempo para serviço {self.id}: {e}")
        # Manter valores padrão seguros em caso de erro crítico
        import traceback
        traceback.print_exc()
    
    # VALIDAÇÃO FINAL DE TODOS OS VALORES
    tempo_decorrido_total = safe_number(tempo_decorrido_total)
    tempo_execucao_efetivo = safe_number(tempo_execucao_efetivo)
    tempo_restante = safe_number(tempo_restante)
    percentual_conclusao = safe_number(percentual_conclusao)
    tempo_atraso = safe_number(tempo_atraso)
    tempo_estimado_total = max(1, safe_number(tempo_estimado_total, 60))  # Mínimo 1 minuto
    
    # DADOS BÁSICOS SEGUROS
    basic_data = {
        'id': safe_number(self.id) if self.id else 0,
        'box_id': safe_number(self.box_id) if self.box_id else 0,
        'mecanico_id': safe_number(self.mecanico_id) if self.mecanico_id else 0,
        'tipo_servico_id': safe_number(self.tipo_servico_id) if self.tipo_servico_id else 0,
        'tempo_extra_minutos': safe_number(self.tempo_extra_minutos),
        'tempo_pausado_total': safe_number(self.tempo_pausado_total),
        'motivo_tempo_extra': str(self.motivo_tempo_extra) if self.motivo_tempo_extra else '',
        'nome_cliente': str(self.nome_cliente) if self.nome_cliente else '',
        'telefone_cliente': str(self.telefone_cliente) if self.telefone_cliente else '',
        'marca_carro': str(self.marca_carro) if self.marca_carro else '',
        'modelo_carro': str(self.modelo_carro) if self.modelo_carro else '',
        'cor_carro': str(self.cor_carro) if self.cor_carro else '',
        'placa_carro': str(self.placa_carro) if self.placa_carro else '',
        'status': str(self.status) if self.status else 'em_andamento',
        'observacoes': str(self.observacoes) if self.observacoes else '',
        'historico_pausas': str(self.historico_pausas) if self.historico_pausas else '[]',
    }
    
    # DATAS SEGURAS
    date_data = {
        'inicio': self.inicio.isoformat() if self.inicio else None,
        'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
        'fim_real': self.fim_real.isoformat() if self.fim_real else None,
        'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
        'criado_em': self.criado_em.isoformat() if self.criado_em else None,
        'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
    }
    
    # HORÁRIOS FORMATADOS SEGUROS
    horarios_data = {
        'horario_inicio': self.inicio.strftime('%H:%M') if self.inicio else None,
        'horario_fim_previsto': self.fim_previsto.strftime('%H:%M') if self.fim_previsto else None,
        'horario_fim_real': self.fim_real.strftime('%H:%M') if self.fim_real else None,
    }
    
    # CÁLCULOS SEGUROS - SEMPRE NÚMEROS VÁLIDOS
    calculos_data = {
        'tempo_decorrido_total_minutos': tempo_decorrido_total,
        'tempo_execucao_efetivo_minutos': tempo_execucao_efetivo,
        'tempo_restante_minutos': tempo_restante,
        'tempo_estimado_total_minutos': tempo_estimado_total,
        'percentual_conclusao': percentual_conclusao,
        'em_atraso': bool(em_atraso),
        'tempo_atraso_minutos': tempo_atraso,
    }
    
    # FORMATAÇÃO AMIGÁVEL SEGURA
    formatacao_data = {
        'tempo_decorrido_formatado': self._formatar_tempo_ultra_seguro(tempo_decorrido_total),
        'tempo_execucao_formatado': self._formatar_tempo_ultra_seguro(tempo_execucao_efetivo),
        'tempo_restante_formatado': self._formatar_tempo_ultra_seguro(tempo_restante),
        'tempo_estimado_formatado': self._formatar_tempo_ultra_seguro(tempo_estimado_total),
        'tempo_atraso_formatado': self._formatar_tempo_ultra_seguro(tempo_atraso) if em_atraso else None,
    }
    
    # RELACIONAMENTOS SEGUROS
    relacionamentos_data = {
        'box': self._safe_relationship_dict_ultra(self.box),
        'mecanico': self._safe_relationship_dict_ultra(self.mecanico),
        'tipo_servico': self._safe_relationship_dict_ultra(self.tipo_servico),
    }
    
    # CAMPOS ESPECÍFICOS PARA O DASHBOARD
    dashboard_data = {
        'pode_pausar': self.status == 'em_andamento',
        'pode_despausar': self.status == 'pausado',
        'pode_finalizar': self.status in ['em_andamento', 'pausado'],
        'esta_pausado': self.status == 'pausado',
        'esta_em_andamento': self.status == 'em_andamento',
        'esta_concluido': self.status == 'concluido'
    }
    
    # COMBINAR TODOS OS DADOS
    result = {}
    result.update(basic_data)
    result.update(date_data)
    result.update(horarios_data)
    result.update(calculos_data)
    result.update(formatacao_data)
    result.update(relacionamentos_data)
    result.update(dashboard_data)
    
    # VALIDAÇÃO FINAL - Garantir que não há valores None críticos
    for key, value in result.items():
        if key.endswith('_minutos') and (value is None or str(value).lower() in ['nan', 'none']):
            result[key] = 0
        elif key == 'percentual_conclusao' and (value is None or str(value).lower() in ['nan', 'none']):
            result[key] = 0
    
    return result

def _formatar_tempo_ultra_seguro(self, minutos):
    """Formata tempo em minutos de forma ULTRA segura - NUNCA retorna NaN"""
    try:
        # Validação inicial
        if minutos is None:
            return "0min"
        
        # Converter para número
        if isinstance(minutos, str):
            if minutos.lower() in ['nan', 'none', 'null', '', 'undefined']:
                return "0min"
            # Tentar extrair número
            import re
            numbers = re.findall(r'\d+', minutos)
            if numbers:
                minutos = int(numbers[0])
            else:
                return "0min"
        
        # Verificar se é número válido
        minutos_num = float(minutos)
        if math.isnan(minutos_num) or math.isinf(minutos_num):
            return "0min"
        
        # Converter para inteiro positivo
        minutos_int = max(0, int(minutos_num))
        
        # Formatação
        if minutos_int == 0:
            return "0min"
        elif minutos_int < 60:
            return f"{minutos_int}min"
        else:
            horas = minutos_int // 60
            mins = minutos_int % 60
            if mins == 0:
                return f"{horas}h"
            else:
                return f"{horas}h {mins}min"
                
    except Exception as e:
        print(f"Erro na formatação de tempo (valor: {minutos}): {e}")
        return "0min"

def _safe_relationship_dict_ultra(self, relationship):
    """Converte relacionamento para dict de forma ULTRA segura"""
    try:
        if not relationship:
            return None
        
        # Tentar método to_dict primeiro
        if hasattr(relationship, 'to_dict') and callable(relationship.to_dict):
            try:
                return relationship.to_dict()
            except Exception:
                pass
        
        # Fallback para atributos básicos
        result = {}
        
        # ID sempre presente
        if hasattr(relationship, 'id'):
            result['id'] = int(relationship.id) if relationship.id is not None else 0
        
        # Nome (vários campos possíveis)
        nome_campos = ['nome', 'name', 'title', 'descricao']
        for campo in nome_campos:
            if hasattr(relationship, campo):
                valor = getattr(relationship, campo)
                if valor:
                    result['nome'] = str(valor)
                    break
        
        # Se não encontrou nome, usar valor padrão
        if 'nome' not in result:
            result['nome'] = f"Item {result.get('id', 'N/A')}"
        
        return result if result else None
        
    except Exception as e:
        print(f"Erro ao processar relacionamento: {e}")
        return None


    
    def _formatar_tempo_seguro(self, minutos):
        """Formata tempo em minutos de forma segura"""
        try:
            minutos_int = int(float(minutos)) if minutos is not None and str(minutos).lower() not in ['nan', 'none', ''] else 0
            
            if minutos_int <= 0:
                return "0min"
            elif minutos_int < 60:
                return f"{minutos_int}min"
            else:
                horas = minutos_int // 60
                mins = minutos_int % 60
                if mins == 0:
                    return f"{horas}h"
                else:
                    return f"{horas}h {mins}min"
        except (ValueError, TypeError):
            return "0min"
    
    def _safe_relationship_dict(self, relationship):
        """Converte relacionamento para dict de forma segura"""
        try:
            if relationship and hasattr(relationship, 'to_dict'):
                return relationship.to_dict()
            elif relationship:
                # Fallback básico
                return {
                    'id': getattr(relationship, 'id', None),
                    'nome': getattr(relationship, 'nome', None)
                }
            return None
        except Exception:
            return None
    
    def pausar_servico(self, motivo=None):
        """Pausa o serviço de forma segura"""
        if self.status != 'em_andamento':
            raise ValueError('Serviço não está em andamento')
        
        agora = datetime.utcnow()
        self.status = 'pausado'
        self.pausado_em = agora
        self.atualizado_em = agora
        
        # Adicionar ao histórico de pausas
        if motivo:
            self._adicionar_historico_pausa(agora, motivo)
        
        return agora
    
    def despausar_servico(self):
        """Retoma o serviço de forma segura"""
        if self.status != 'pausado':
            raise ValueError('Serviço não está pausado')
        
        agora = datetime.utcnow()
        
        # Calcular tempo pausado
        tempo_pausado_minutos = 0
        if self.pausado_em:
            delta = agora - self.pausado_em
            tempo_pausado_minutos = max(0, int(delta.total_seconds() / 60))
            
            # Atualizar total de tempo pausado
            if self.tempo_pausado_total is None:
                self.tempo_pausado_total = 0
            self.tempo_pausado_total += tempo_pausado_minutos
            
            # Ajustar fim previsto
            if self.fim_previsto:
                self.fim_previsto = self.fim_previsto + (agora - self.pausado_em)
            
            # Finalizar entrada no histórico
            self._finalizar_historico_pausa(tempo_pausado_minutos)
        
        self.status = 'em_andamento'
        self.pausado_em = None
        self.atualizado_em = agora
        
        return tempo_pausado_minutos
    
    def finalizar_servico(self, observacoes_finais=None):
        """Finaliza o serviço de forma segura"""
        if self.status not in ['em_andamento', 'pausado']:
            raise ValueError('Serviço não pode ser finalizado')
        
        agora = datetime.utcnow()
        
        # Se estava pausado, calcular último tempo de pausa
        if self.status == 'pausado' and self.pausado_em:
            tempo_pausado = max(0, int((agora - self.pausado_em).total_seconds() / 60))
            if self.tempo_pausado_total is None:
                self.tempo_pausado_total = 0
            self.tempo_pausado_total += tempo_pausado
            self._finalizar_historico_pausa(tempo_pausado)
        
        # Adicionar observações finais
        if observacoes_finais:
            if self.observacoes:
                self.observacoes += f"\n\nObservações finais: {observacoes_finais}"
            else:
                self.observacoes = f"Observações finais: {observacoes_finais}"
        
        self.fim_real = agora
        self.status = 'concluido'
        self.pausado_em = None
        self.atualizado_em = agora
        
        return agora
    
    def _adicionar_historico_pausa(self, momento, motivo):
        """Adiciona entrada no histórico de pausas"""
        try:
            if self.historico_pausas:
                historico = json.loads(self.historico_pausas)
            else:
                historico = []
            
            entrada = {
                'inicio': momento.isoformat(),
                'motivo': motivo or 'Não informado',
                'duracao_minutos': None  # Será preenchido quando despausar
            }
            
            historico.append(entrada)
            self.historico_pausas = json.dumps(historico)
        except Exception:
            # Se falhar, continuar sem histórico
            pass
    
    def _finalizar_historico_pausa(self, duracao_minutos):
        """Finaliza última entrada no histórico de pausas"""
        try:
            if self.historico_pausas:
                historico = json.loads(self.historico_pausas)
                if historico and historico[-1].get('duracao_minutos') is None:
                    historico[-1]['duracao_minutos'] = duracao_minutos
                    self.historico_pausas = json.dumps(historico)
        except Exception:
            # Se falhar, continuar sem histórico
            pass
    
    def calcular_tempo_total_estimado(self):
        """Calcula o tempo total estimado incluindo tempo extra"""
        if self.tipo_servico and hasattr(self.tipo_servico, 'tempo_estimado'):
            tempo_base = self.tipo_servico.tempo_estimado or 60
        else:
            tempo_base = 60
        
        tempo_extra = self.tempo_extra_minutos or 0
        return tempo_base + tempo_extra


# ENDPOINTS ADICIONAIS PARA DIAGNÓSTICO E CORREÇÃO
# Adicionar ao arquivo src/routes/servico_execucao.py


