from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # box, elevador
    status = db.Column(db.String(20), default='livre')  # livre, ocupado, pausado, manutencao
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Box {self.numero}>'

    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

    def get_status_display(self):
        """Retorna o status em formato amigável"""
        status_map = {
            'livre': 'Livre',
            'ocupado': 'Ocupado',
            'pausado': 'Pausado',
            'manutencao': 'Manutenção'
        }
        return status_map.get(self.status, self.status.title())

    def pode_iniciar_servico(self):
        """Verifica se o box pode iniciar um novo serviço"""
        return self.status == 'livre'

    def esta_disponivel(self):
        """Verifica se o box está disponível (livre ou pausado)"""
        return self.status in ['livre', 'pausado']

