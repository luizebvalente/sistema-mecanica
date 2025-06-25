from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # box, elevador
    status = db.Column(db.String(20), default='livre')  # livre, ocupado, manutencao
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Box {self.numero}>'

    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

