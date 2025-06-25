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
    status = db.Column(db.String(20), default='agendado')  # agendado, iniciado, cancelado
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    box = db.relationship('Box', backref='fila_servicos')
    mecanico = db.relationship('Mecanico', backref='fila_servicos')
    tipo_servico = db.relationship('TipoServico', backref='fila_servicos')

    def __repr__(self):
        return f'<FilaServico {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'box_id': self.box_id,
            'mecanico_id': self.mecanico_id,
            'tipo_servico_id': self.tipo_servico_id,
            'agendado_para': self.agendado_para.isoformat() if self.agendado_para else None,
            'prioridade': self.prioridade,
            'status': self.status,
            'observacoes': self.observacoes,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }

