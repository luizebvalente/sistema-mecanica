from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class MarcaCarro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MarcaCarro {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

class ModeloCarro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca_carro.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento
    marca = db.relationship('MarcaCarro', backref='modelos')

    def __repr__(self):
        return f'<ModeloCarro {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'marca_id': self.marca_id,
            'marca': self.marca.to_dict() if self.marca else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

