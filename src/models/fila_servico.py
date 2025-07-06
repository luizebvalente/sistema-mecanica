from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class FilaServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanico.id'), nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)
    agendado_para = db.Column(db.DateTime, nullable=True)
    prioridade = db.Column(db.Integer, default=1)  # 1 = baixa, 5 = alta
    posicao_fila = db.Column(db.Integer, default=1)  # Posição na fila do box
    status = db.Column(db.String(20), default='agendado')  # agendado, iniciado, cancelado
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
    
    # Controle de tempo
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    motivo_tempo_extra = db.Column(db.String(200), nullable=True)

    # Relacionamentos
    box = db.relationship('Box', backref='fila_servicos')
    mecanico = db.relationship('Mecanico', backref='fila_servicos')
    tipo_servico = db.relationship('TipoServico', backref='fila_servicos')

    def __repr__(self):
        return f'<FilaServico {self.id} - {self.nome_cliente}>'

    def to_dict(self):
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'agendado_para': self.agendado_para.isoformat() if self.agendado_para else None,
            'prioridade': self.prioridade,
            'posicao_fila': self.posicao_fila,
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
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }

    def calcular_tempo_total_estimado(self):
        """Calcula o tempo total estimado incluindo tempo extra"""
        tempo_base = self.tipo_servico.tempo_estimado if self.tipo_servico else 60
        return tempo_base + self.tempo_extra_minutos

