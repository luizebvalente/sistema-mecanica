# src/models/servico_execucao.py - VERSÃO CORRIGIDA COMPLETA
from src.models.user import db
from datetime import datetime

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
    
    # ADICIONADO: Campos de timestamp que estavam faltando
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ADICIONADO: Campo para histórico de pausas
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
        """Converte para dict com cálculos seguros (anti-NaN)"""
        agora = datetime.utcnow()
        
        # Valores padrão seguros para evitar NaN
        tempo_decorrido_total = 0
        tempo_execucao_efetivo = 0
        tempo_restante = 0
        percentual_conclusao = 0
        em_atraso = False
        tempo_atraso = 0
        
        try:
            if self.inicio:
                # Tempo decorrido desde o início (sempre número válido)
                delta_inicio = agora - self.inicio
                tempo_decorrido_total = max(0, int(delta_inicio.total_seconds() / 60))
                
                # Tempo pausado atual se está pausado
                tempo_pausado_atual = 0
                if self.status == 'pausado' and self.pausado_em:
                    delta_pausa = agora - self.pausado_em
                    tempo_pausado_atual = max(0, int(delta_pausa.total_seconds() / 60))
                
                # Tempo efetivo = tempo total - tempo pausado total - tempo pausado atual
                tempo_pausado_total_safe = self.tempo_pausado_total if self.tempo_pausado_total is not None else 0
                tempo_execucao_efetivo = tempo_decorrido_total - tempo_pausado_total_safe - tempo_pausado_atual
                tempo_execucao_efetivo = max(0, tempo_execucao_efetivo)
                
                # Calcular tempo restante e percentual com base no tipo de serviço
                if self.tipo_servico and hasattr(self.tipo_servico, 'tempo_estimado') and self.tipo_servico.tempo_estimado:
                    tempo_estimado_base = self.tipo_servico.tempo_estimado
                    tempo_extra_safe = self.tempo_extra_minutos if self.tempo_extra_minutos is not None else 0
                    tempo_estimado_total = tempo_estimado_base + tempo_extra_safe
                    
                    if tempo_estimado_total > 0:
                        tempo_restante = max(0, tempo_estimado_total - tempo_execucao_efetivo)
                        percentual_conclusao = min(100, max(0, int((tempo_execucao_efetivo / tempo_estimado_total) * 100)))
                    else:
                        tempo_restante = 0
                        percentual_conclusao = 0
                else:
                    # Se não tem tipo de serviço, assumir 60 minutos padrão
                    tempo_estimado_total = 60 + (self.tempo_extra_minutos or 0)
                    tempo_restante = max(0, tempo_estimado_total - tempo_execucao_efetivo)
                    if tempo_estimado_total > 0:
                        percentual_conclusao = min(100, max(0, int((tempo_execucao_efetivo / tempo_estimado_total) * 100)))
                
                # Verificar atraso (apenas se não estiver pausado)
                if self.fim_previsto and self.status == 'em_andamento':
                    if agora > self.fim_previsto:
                        em_atraso = True
                        delta_atraso = agora - self.fim_previsto
                        tempo_atraso = max(0, int(delta_atraso.total_seconds() / 60))
        
        except Exception as e:
            # Em caso de qualquer erro, usar valores padrão seguros
            print(f"Erro no cálculo de tempo para serviço {self.id}: {e}")
            tempo_decorrido_total = 0
            tempo_execucao_efetivo = 0
            tempo_restante = 0
            percentual_conclusao = 0
            em_atraso = False
            tempo_atraso = 0
        
        # Garantir que todos os valores são números válidos
        tempo_decorrido_total = int(tempo_decorrido_total) if tempo_decorrido_total is not None else 0
        tempo_execucao_efetivo = int(tempo_execucao_efetivo) if tempo_execucao_efetivo is not None else 0
        tempo_restante = int(tempo_restante) if tempo_restante is not None else 0
        percentual_conclusao = int(percentual_conclusao) if percentual_conclusao is not None else 0
        tempo_atraso = int(tempo_atraso) if tempo_atraso is not None else 0
        
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
            'fim_real': self.fim_real.isoformat() if self.fim_real else None,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
            'tempo_extra_minutos': self.tempo_extra_minutos if self.tempo_extra_minutos is not None else 0,
            'tempo_pausado_total': self.tempo_pausado_total if self.tempo_pausado_total is not None else 0,
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
            
            # Informações calculadas - SEMPRE números válidos (anti-NaN)
            'tempo_decorrido_total_minutos': tempo_decorrido_total,
            'tempo_execucao_efetivo_minutos': tempo_execucao_efetivo,
            'tempo_restante_minutos': tempo_restante,
            'percentual_conclusao': percentual_conclusao,
            'em_atraso': bool(em_atraso),
            'tempo_atraso_minutos': tempo_atraso,
            
            # Formatação amigável
            'tempo_decorrido_formatado': self._formatar_tempo_seguro(tempo_decorrido_total),
            'tempo_execucao_formatado': self._formatar_tempo_seguro(tempo_execucao_efetivo),
            'tempo_restante_formatado': self._formatar_tempo_seguro(tempo_restante),
            'tempo_atraso_formatado': self._formatar_tempo_seguro(tempo_atraso) if em_atraso else None,
            
            # Horários formatados
            'horario_inicio': self.inicio.strftime('%H:%M') if self.inicio else None,
            'horario_fim_previsto': self.fim_previsto.strftime('%H:%M') if self.fim_previsto else None,
            'horario_fim_real': self.fim_real.strftime('%H:%M') if self.fim_real else None,
            
            # Relacionamentos (com proteção contra None)
            'box': self._safe_relationship_dict(self.box),
            'mecanico': self._safe_relationship_dict(self.mecanico),
            'tipo_servico': self._safe_relationship_dict(self.tipo_servico)
        }
    
    def _formatar_tempo_seguro(self, minutos):
        """Formata tempo em minutos de forma segura (anti-NaN)"""
        try:
            # Converter para int e garantir que não é None/NaN
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
        except (ValueError, TypeError, ZeroDivisionError):
            return "0min"
    
    def _safe_relationship_dict(self, relationship):
        """Converte relacionamento para dict de forma segura"""
        try:
            if relationship and hasattr(relationship, 'to_dict'):
                return relationship.to_dict()
            elif relationship and hasattr(relationship, 'id'):
                return {'id': relationship.id}
            else:
                return None
        except:
            return None
    
    def pausar_seguro(self, motivo=None):
        """Pausa o serviço de forma segura"""
        if self.status != 'em_andamento':
            raise ValueError('Serviço não está em andamento')
        
        agora = datetime.utcnow()
        self.status = 'pausado'
        self.pausado_em = agora
        self.atualizado_em = agora
        return agora
    
    def despausar_seguro(self):
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
        
        self.status = 'em_andamento'
        self.pausado_em = None
        self.atualizado_em = agora
        
        return tempo_pausado_minutos
    
    def finalizar_seguro(self):
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
        
        self.fim_real = agora
        self.status = 'concluido'
        self.pausado_em = None
        self.atualizado_em = agora
        
        return agora
