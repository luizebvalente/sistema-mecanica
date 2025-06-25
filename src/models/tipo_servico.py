from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class TipoServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tempo_estimado = db.Column(db.Integer, nullable=False)  # em minutos
    descricao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TipoServico {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tempo_estimado': self.tempo_estimado,
            'descricao': self.descricao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

