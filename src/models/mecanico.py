from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class Mecanico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Mecanico {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

