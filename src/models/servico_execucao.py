# src/models/servico_execucao.py - VERSÃO MÍNIMA FUNCIONANDO
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
        # Cálculos básicos para evitar NaN
        agora = datetime.utcnow()
        
        # Valores padrão seguros
        tempo_decorrido_total = 0
        tempo_execucao_efetivo = 0
        tempo_restante = 0
        percentual_conclusao = 0
        em_atraso = False
        tempo_atraso = 0
        
        try:
            if self.inicio:
                # Tempo decorrido desde o início
                tempo_decorrido_total = int((agora - self.inicio).total_seconds() / 60)
                
                # Tempo pausado atual se está pausado
                tempo_pausado_atual = 0
                if self.status == 'pausado' and self.pausado_em:
                    tempo_pausado_atual = int((agora - self.pausado_em).total_seconds() / 60)
                
                # Tempo efetivo = tempo total - tempo pausado
                tempo_pausado_total_safe = self.tempo_pausado_total or 0
                tempo_execucao_efetivo = tempo_decorrido_total - tempo_pausado_total_safe - tempo_pausado_atual
                tempo_execucao_efetivo = max(0, tempo_execucao_efetivo)
                
                # Calcular tempo restante e percentual
                if self.tipo_servico and self.tipo_servico.tempo_estimado:
                    tempo_extra_safe = self.tempo_extra_minutos or 0
                    tempo_estimado = self.tipo_servico.tempo_estimado + tempo_extra_safe
                    tempo_restante = max(0, tempo_estimado - tempo_execucao_efetivo)
                    
                    if tempo_estimado > 0:
                        percentual_conclusao = min(100, int((tempo_execucao_efetivo / tempo_estimado) * 100))
                
                # Verificar atraso
                if self.fim_previsto and self.status == 'em_andamento':
                    if agora > self.fim_previsto:
                        em_atraso = True
                        tempo_atraso = int((agora - self.fim_previsto).total_seconds() / 60)
        
        except Exception as e:
            # Em caso de erro, usar valores seguros
            print(f"Erro no cálculo de tempo: {e}")
        
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
            'fim_real': self.fim_real.isoformat() if self.fim_real else None,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
            'tempo_extra_minutos': self.tempo_extra_minutos or 0,
            'tempo_pausado_total': self.tempo_pausado_total or 0,
            'motivo_tempo_extra': self.motivo_tempo_extra,
            'nome_cliente': self.nome_cliente,
            'telefone_cliente': self.telefone_cliente,
            'marca_carro': self.marca_carro,
            'modelo_carro': self.modelo_carro,
            'cor_carro': self.cor_carro,
            'placa_carro': self.placa_carro,
            'status': self.status,
            'observacoes': self.observacoes,
            
            # Informações calculadas - SEMPRE números válidos
            'tempo_decorrido_total_minutos': tempo_decorrido_total,
            'tempo_execucao_efetivo_minutos': tempo_execucao_efetivo,
            'tempo_restante_minutos': tempo_restante,
            'percentual_conclusao': percentual_conclusao,
            'em_atraso': em_atraso,
            'tempo_atraso_minutos': tempo_atraso,
            
            # Formatação amigável
            'tempo_decorrido_formatado': self._formatar_tempo(tempo_decorrido_total),
            'tempo_execucao_formatado': self._formatar_tempo(tempo_execucao_efetivo),
            'tempo_restante_formatado': self._formatar_tempo(tempo_restante),
            'tempo_atraso_formatado': self._formatar_tempo(tempo_atraso) if em_atraso else None,
            
            # Horários formatados
            'horario_inicio': self.inicio.strftime('%H:%M') if self.inicio else None,
            'horario_fim_previsto': self.fim_previsto.strftime('%H:%M') if self.fim_previsto else None,
            'horario_fim_real': self.fim_real.strftime('%H:%M') if self.fim_real else None,
            
            # Relacionamentos
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }
    
    def _formatar_tempo(self, minutos):
        """Formata tempo em minutos para formato legível"""
        try:
            minutos = int(minutos) if minutos else 0
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
        except:
            return "0min"
