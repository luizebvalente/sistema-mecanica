from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime, timedelta

class ServicoExecucao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanico.id'), nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)
    inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fim_previsto = db.Column(db.DateTime, nullable=False)
    fim_real = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='em_andamento')  # em_andamento, pausado, concluido, cancelado, interrompido
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Dados do cliente e veículo
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone_cliente = db.Column(db.String(20), nullable=True)
    marca_carro = db.Column(db.String(50), nullable=False)
    modelo_carro = db.Column(db.String(50), nullable=False)
    cor_carro = db.Column(db.String(30), nullable=True)
    placa_carro = db.Column(db.String(10), nullable=True)
    
    # Controle de tempo e pausas
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    motivo_tempo_extra = db.Column(db.String(200), nullable=True)
    tempo_pausado_total = db.Column(db.Integer, default=0)  # Em minutos
    pausado_em = db.Column(db.DateTime, nullable=True)
    retomado_em = db.Column(db.DateTime, nullable=True)
    motivo_pausa = db.Column(db.String(200), nullable=True)
    
    # Histórico de pausas (JSON string)
    historico_pausas = db.Column(db.Text, nullable=True)  # JSON com histórico de pausas

    # Relacionamentos
    box = db.relationship('Box', backref='servicos_execucao')
    mecanico = db.relationship('Mecanico', backref='servicos_execucao')
    tipo_servico = db.relationship('TipoServico', backref='servicos_execucao')

    def __repr__(self):
        return f'<ServicoExecucao {self.id} - {self.nome_cliente}>'

    def to_dict(self):
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
            'fim_real': self.fim_real.isoformat() if self.fim_real else None,
            'status': self.status,
            'observacoes': self.observacoes,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'nome_cliente': self.nome_cliente,
            'telefone_cliente': self.telefone_cliente,
            'marca_carro': self.marca_carro,
            'modelo_carro': self.modelo_carro,
            'cor_carro': self.cor_carro,
            'placa_carro': self.placa_carro,
            'tempo_extra_minutos': self.tempo_extra_minutos,
            'motivo_tempo_extra': self.motivo_tempo_extra,
            'tempo_pausado_total': self.tempo_pausado_total,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
            'retomado_em': self.retomado_em.isoformat() if self.retomado_em else None,
            'motivo_pausa': self.motivo_pausa,
            'historico_pausas': self.historico_pausas,
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None,
            'tempo_decorrido': self.calcular_tempo_decorrido(),
            'tempo_restante': self.calcular_tempo_restante(),
            'percentual_concluido': self.calcular_percentual_concluido()
        }

    def calcular_tempo_decorrido(self):
        """Calcula o tempo decorrido em minutos, excluindo pausas"""
        if not self.inicio:
            return 0
        
        fim_calculo = self.fim_real or datetime.utcnow()
        tempo_total = (fim_calculo - self.inicio).total_seconds() / 60
        
        # Subtrair tempo pausado
        tempo_efetivo = tempo_total - self.tempo_pausado_total
        
        # Se está pausado atualmente, não contar o tempo desde a pausa
        if self.status == 'pausado' and self.pausado_em:
            tempo_pausa_atual = (datetime.utcnow() - self.pausado_em).total_seconds() / 60
            tempo_efetivo -= tempo_pausa_atual
        
        return max(0, int(tempo_efetivo))

    def calcular_tempo_real_atual(self):
        """Calcula o tempo real atual de execução incluindo atrasos"""
        if not self.inicio:
            return {
                'tempo_decorrido_segundos': 0,
                'tempo_restante_segundos': 0,
                'percentual_concluido': 0,
                'em_atraso': False,
                'atraso_segundos': 0,
                'status': self.status,
                'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None
            }
        
        agora = datetime.utcnow()
        
        # Calcular tempo decorrido (sem contar pausas)
        if self.status == 'pausado' and self.pausado_em:
            tempo_decorrido = (self.pausado_em - self.inicio).total_seconds()
        else:
            tempo_decorrido = (agora - self.inicio).total_seconds()
            # Subtrair tempo pausado total se houver
            if hasattr(self, 'tempo_pausado_total') and self.tempo_pausado_total:
                tempo_decorrido -= self.tempo_pausado_total * 60
        
        tempo_decorrido = max(0, tempo_decorrido)
        
        # Tempo estimado em segundos
        tempo_estimado_segundos = (self.tipo_servico.tempo_estimado if self.tipo_servico else 60) * 60
        
        # Calcular tempo restante (pode ser negativo = atraso)
        tempo_restante = tempo_estimado_segundos - tempo_decorrido
        
        # Calcular percentual
        percentual = min(100, max(0, (tempo_decorrido / tempo_estimado_segundos) * 100))
        
        # Verificar se está em atraso
        em_atraso = tempo_restante < 0
        atraso_segundos = abs(tempo_restante) if em_atraso else 0
        
        return {
            'tempo_decorrido_segundos': int(tempo_decorrido),
            'tempo_restante_segundos': int(tempo_restante),
            'percentual_concluido': int(percentual),
            'em_atraso': em_atraso,
            'atraso_segundos': int(atraso_segundos),
            'status': self.status,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None
        }

    def calcular_tempo_restante(self):
        """Calcula o tempo restante em minutos"""
        if self.status in ['concluido', 'cancelado', 'interrompido']:
            return 0
        
        tempo_decorrido = self.calcular_tempo_decorrido()
        tempo_total_estimado = self.tipo_servico.tempo_estimado + self.tempo_extra_minutos if self.tipo_servico else 60
        
        return max(0, tempo_total_estimado - tempo_decorrido)

    def calcular_percentual_concluido(self):
        """Calcula o percentual de conclusão do serviço"""
        if self.status in ['concluido']:
            return 100
        
        if self.status in ['cancelado', 'interrompido']:
            return 0
        
        tempo_decorrido = self.calcular_tempo_decorrido()
        tempo_total_estimado = self.tipo_servico.tempo_estimado + self.tempo_extra_minutos if self.tipo_servico else 60
        
        if tempo_total_estimado <= 0:
            return 0
        
        percentual = (tempo_decorrido / tempo_total_estimado) * 100
        return min(100, max(0, int(percentual)))

    def pausar(self, motivo=None):
        """Pausa o serviço"""
        if self.status != 'em_andamento':
            return False
        
        self.status = 'pausado'
        self.pausado_em = datetime.utcnow()
        self.motivo_pausa = motivo
        return True

    def retomar(self):
        """Retoma o serviço pausado"""
        if self.status != 'pausado' or not self.pausado_em:
            return False
        
        # Calcular tempo pausado
        tempo_pausa = (datetime.utcnow() - self.pausado_em).total_seconds() / 60
        self.tempo_pausado_total += int(tempo_pausa)
        
        # Atualizar histórico de pausas
        import json
        historico = json.loads(self.historico_pausas) if self.historico_pausas else []
        historico.append({
            'pausado_em': self.pausado_em.isoformat(),
            'retomado_em': datetime.utcnow().isoformat(),
            'duracao_minutos': int(tempo_pausa),
            'motivo': self.motivo_pausa
        })
        self.historico_pausas = json.dumps(historico)
        
        # Resetar campos de pausa
        self.status = 'em_andamento'
        self.retomado_em = datetime.utcnow()
        self.pausado_em = None
        self.motivo_pausa = None
        
        return True

