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
    pausado_em = db.Column(db.DateTime)  # Novo campo para controle de pausa
    
    # Controle de tempo
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    tempo_pausado_total = db.Column(db.Integer, default=0)  # Total de minutos pausado
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
    status = db.Column(db.String(20), default='em_andamento')  # em_andamento, pausado, concluido
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    box = db.relationship('Box', backref=db.backref('servicos_execucao', lazy=True))
    mecanico = db.relationship('Mecanico', backref=db.backref('servicos_execucao', lazy=True))
    tipo_servico = db.relationship('TipoServico', backref=db.backref('servicos_execucao', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fim_previsto': self.fim_previsto.isoformat() if self.fim_previsto else None,
            'fim_real': self.fim_real.isoformat() if self.fim_real else None,
            'pausado_em': self.pausado_em.isoformat() if self.pausado_em else None,
            'tempo_extra_minutos': self.tempo_extra_minutos,
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
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }
