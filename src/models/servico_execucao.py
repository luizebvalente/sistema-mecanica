# src/models/servico_execucao.py - VERSÃO CORRIGIDA COMPLETA
from src.models.user import db
from datetime import datetime
import json

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
    
    def to_dict(self):
        """Converte para dict com cálculos seguros - VERSÃO CORRIGIDA"""
        agora = datetime.utcnow()
        
        # Valores padrão seguros
        tempo_decorrido_total = 0
        tempo_execucao_efetivo = 0
        tempo_restante = 0
        percentual_conclusao = 0
        em_atraso = False
        tempo_atraso = 0
        tempo_estimado_total = 60  # Default para evitar divisão por zero
        
        try:
            # 1. Calcular tempo decorrido total desde o início
            if self.inicio:
                delta_inicio = agora - self.inicio
                tempo_decorrido_total = max(0, int(delta_inicio.total_seconds() / 60))
            
            # 2. Obter tempo estimado do tipo de serviço
            if self.tipo_servico and hasattr(self.tipo_servico, 'tempo_estimado'):
                tempo_estimado_base = self.tipo_servico.tempo_estimado or 60
            else:
                tempo_estimado_base = 60
            
            tempo_extra_safe = self.tempo_extra_minutos or 0
            tempo_estimado_total = tempo_estimado_base + tempo_extra_safe
            
            # 3. Calcular tempo pausado atual se estiver pausado
            tempo_pausado_atual = 0
            if self.status == 'pausado' and self.pausado_em:
                delta_pausa = agora - self.pausado_em
                tempo_pausado_atual = max(0, int(delta_pausa.total_seconds() / 60))
            
            # 4. Calcular tempo efetivo de execução
            tempo_pausado_total_safe = self.tempo_pausado_total or 0
            tempo_execucao_efetivo = tempo_decorrido_total - tempo_pausado_total_safe - tempo_pausado_atual
            tempo_execucao_efetivo = max(0, tempo_execucao_efetivo)
            
            # 5. Calcular tempo restante e percentual
            if tempo_estimado_total > 0:
                tempo_restante = max(0, tempo_estimado_total - tempo_execucao_efetivo)
                percentual_conclusao = min(100, max(0, int((tempo_execucao_efetivo / tempo_estimado_total) * 100)))
            
            # 6. Verificar atraso (apenas se não estiver pausado)
            if self.fim_previsto and self.status == 'em_andamento':
                if agora > self.fim_previsto:
                    em_atraso = True
                    delta_atraso = agora - self.fim_previsto
                    tempo_atraso = max(0, int(delta_atraso.total_seconds() / 60))
        
        except Exception as e:
            print(f"Erro no cálculo de tempo para serviço {self.id}: {e}")
            # Manter valores padrão seguros em caso de erro
        
        # Garantir que todos os valores são válidos
        def safe_int(value, default=0):
            try:
                return int(float(value)) if value is not None and str(value).lower() not in ['nan', 'none', 'null', ''] else default
            except (ValueError, TypeError):
                return default
        
        tempo_decorrido_total = safe_int(tempo_decorrido_total)
        tempo_execucao_efetivo = safe_int(tempo_execucao_efetivo)
        tempo_restante = safe_int(tempo_restante)
        percentual_conclusao = safe_int(percentual_conclusao)
        tempo_atraso = safe_int(tempo_atraso)
        tempo_estimado_total = safe_int(tempo_estimado_total, 60)
        
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
            'fim_real': self.fim_real.isoformat() if self.fim_real else None,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
            'tempo_extra_minutos': safe_int(self.tempo_extra_minutos),
            'tempo_pausado_total': safe_int(self.tempo_pausado_total),
            'motivo_tempo_extra': self.motivo_tempo_extra,
            'nome_cliente': self.nome_cliente,
            'telefone_cliente': self.telefone_cliente,
            'marca_carro': self.marca_carro,
            'modelo_carro': self.modelo_carro,
            'cor_carro': self.cor_carro,
            'placa_carro': self.placa_carro,
            'status': self.status,
            'observacoes': self.observacoes,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'historico_pausas': self.historico_pausas,
            
            # INFORMAÇÕES CALCULADAS - SEMPRE NÚMEROS VÁLIDOS
            'tempo_decorrido_total_minutos': tempo_decorrido_total,
            'tempo_execucao_efetivo_minutos': tempo_execucao_efetivo,
            'tempo_restante_minutos': tempo_restante,
            'tempo_estimado_total_minutos': tempo_estimado_total,
            'percentual_conclusao': percentual_conclusao,
            'em_atraso': bool(em_atraso),
            'tempo_atraso_minutos': tempo_atraso,
            
            # FORMATAÇÃO AMIGÁVEL
            'tempo_decorrido_formatado': self._formatar_tempo_seguro(tempo_decorrido_total),
            'tempo_execucao_formatado': self._formatar_tempo_seguro(tempo_execucao_efetivo),
            'tempo_restante_formatado': self._formatar_tempo_seguro(tempo_restante),
            'tempo_estimado_formatado': self._formatar_tempo_seguro(tempo_estimado_total),
            'tempo_atraso_formatado': self._formatar_tempo_seguro(tempo_atraso) if em_atraso else None,
            
            # HORÁRIOS FORMATADOS
            'horario_inicio': self.inicio.strftime('%H:%M') if self.inicio else None,
            'horario_fim_previsto': self.fim_previsto.strftime('%H:%M') if self.fim_previsto else None,
            'horario_fim_real': self.fim_real.strftime('%H:%M') if self.fim_real else None,
            
            # RELACIONAMENTOS SEGUROS
            'box': self._safe_relationship_dict(self.box),
            'mecanico': self._safe_relationship_dict(self.mecanico),
            'tipo_servico': self._safe_relationship_dict(self.tipo_servico),
            
            # CAMPOS ESPECÍFICOS PARA O DASHBOARD
            'pode_pausar': self.status == 'em_andamento',
            'pode_despausar': self.status == 'pausado',
            'pode_finalizar': self.status in ['em_andamento', 'pausado'],
            'esta_pausado': self.status == 'pausado',
            'esta_em_andamento': self.status == 'em_andamento',
            'esta_concluido': self.status == 'concluido'
        }
    
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
