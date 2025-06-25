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
    status = db.Column(db.String(20), default='em_andamento')  # em_andamento, concluido, cancelado
    observacoes = db.Column(db.Text, nullable=True)

    # Relacionamentos
    box = db.relationship('Box', backref='servicos_execucao')
    mecanico = db.relationship('Mecanico', backref='servicos_execucao')
    tipo_servico = db.relationship('TipoServico', backref='servicos_execucao')

    def __repr__(self):
        return f'<ServicoExecucao {self.id}>'

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
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }

