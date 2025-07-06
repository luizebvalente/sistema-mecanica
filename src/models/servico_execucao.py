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
    
    # Controle de tempo - CORRIGIDO: Adicionado campo que estava faltando
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    tempo_pausado_total = db.Column(db.Integer, default=0)
    motivo_tempo_extra = db.Column(db.String(200))
    
    # NOVO: Campo para armazenar histórico de pausas em JSON
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
    status = db.Column(db.String(20), default='em_andamento')  # em_andamento, pausado, concluido
    observacoes = db.Column(db.Text)
    
    # NOVO: Timestamps de criação e atualização
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    box = db.relationship('Box', backref=db.backref('servicos_execucao', lazy=True))
    mecanico = db.relationship('Mecanico', backref=db.backref('servicos_execucao', lazy=True))
    tipo_servico = db.relationship('TipoServico', backref=db.backref('servicos_execucao', lazy=True))
    
    def to_dict(self):
        # Calcular informações de tempo em tempo real
        agora = datetime.utcnow()
        
        # Tempo decorrido desde o início
        tempo_decorrido_total = 0
        tempo_execucao_efetivo = 0
        tempo_restante = 0
        percentual_conclusao = 0
        
        if self.inicio:
            tempo_decorrido_total = int((agora - self.inicio).total_seconds() / 60)
            
            # Tempo efetivo = tempo total - tempo pausado
            tempo_pausado_atual = 0
            if self.status == 'pausado' and self.pausado_em:
                tempo_pausado_atual = int((agora - self.pausado_em).total_seconds() / 60)
            
            tempo_execucao_efetivo = tempo_decorrido_total - (self.tempo_pausado_total or 0) - tempo_pausado_atual
            tempo_execucao_efetivo = max(0, tempo_execucao_efetivo)
            
            # Calcular tempo restante e percentual
            if self.tipo_servico:
                tempo_estimado = self.tipo_servico.tempo_estimado + (self.tempo_extra_minutos or 0)
                tempo_restante = max(0, tempo_estimado - tempo_execucao_efetivo)
                if tempo_estimado > 0:
                    percentual_conclusao = min(100, int((tempo_execucao_efetivo / tempo_estimado) * 100))
        
        # Verificar se está em atraso
        em_atraso = False
        tempo_atraso = 0
        if self.fim_previsto and self.status == 'em_andamento':
            if agora > self.fim_previsto:
                em_atraso = True
                tempo_atraso = int((agora - self.fim_previsto).total_seconds() / 60)
        
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
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            
            # Informações calculadas de tempo
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
    
    def pausar(self, motivo=None):
        """Pausa o serviço e registra no histórico"""
        import json
        
        if self.status != 'em_andamento':
            raise ValueError('Serviço não está em andamento')
        
        agora = datetime.utcnow()
        self.status = 'pausado'
        self.pausado_em = agora
        
        # Atualizar histórico de pausas
        historico = []
        if self.historico_pausas:
            try:
                historico = json.loads(self.historico_pausas)
            except:
                historico = []
        
        # Não adicionar no histórico ainda, só quando despausar
        return agora
    
    def despausar(self):
        """Retoma o serviço e atualiza o histórico"""
        import json
        
        if self.status != 'pausado':
            raise ValueError('Serviço não está pausado')
        
        agora = datetime.utcnow()
        
        # Calcular tempo pausado
        tempo_pausado = int((agora - self.pausado_em).total_seconds() / 60)
        
        # Atualizar histórico de pausas
        historico = []
        if self.historico_pausas:
            try:
                historico = json.loads(self.historico_pausas)
            except:
                historico = []
        
        historico.append({
            'pausado_em': self.pausado_em.isoformat(),
            'retomado_em': agora.isoformat(),
            'duracao_minutos': tempo_pausado,
            'motivo': getattr(self, '_motivo_pausa_temp', None)
        })
        
        self.historico_pausas = json.dumps(historico)
        
        # Atualizar totais
        self.tempo_pausado_total = (self.tempo_pausado_total or 0) + tempo_pausado
        
        # Ajustar fim previsto
        if self.fim_previsto:
            self.fim_previsto += timedelta(minutes=tempo_pausado)
        
        # Atualizar status
        self.status = 'em_andamento'
        self.pausado_em = None
        
        return tempo_pausado
    
    def finalizar(self):
        """Finaliza o serviço"""
        if self.status not in ['em_andamento', 'pausado']:
            raise ValueError('Serviço não pode ser finalizado')
        
        agora = datetime.utcnow()
        
        # Se estava pausado, calcular último tempo de pausa
        if self.status == 'pausado' and self.pausado_em:
            import json
            
            tempo_pausado = int((agora - self.pausado_em).total_seconds() / 60)
            self.tempo_pausado_total = (self.tempo_pausado_total or 0) + tempo_pausado
            
            # Atualizar histórico
            historico = []
            if self.historico_pausas:
                try:
                    historico = json.loads(self.historico_pausas)
                except:
                    historico = []
            
            historico.append({
                'pausado_em': self.pausado_em.isoformat(),
                'retomado_em': agora.isoformat(),
                'duracao_minutos': tempo_pausado,
                'motivo': 'Finalizado durante pausa'
            })
            
            self.historico_pausas = json.dumps(historico)
        
        self.fim_real = agora
        self.status = 'concluido'
        self.pausado_em = None
        
        return agora
