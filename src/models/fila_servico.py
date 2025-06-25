from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class FilaServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanico.id'), nullable=False)
    tipo_servico_id = db.Column(db.Integer, db.ForeignKey('tipo_servico.id'), nullable=False)
    
    # Dados de agendamento
    agendado_para = db.Column(db.DateTime, nullable=True)
    data_agendamento = db.Column(db.Date, nullable=True)  # Data específica do agendamento
    horario_agendamento = db.Column(db.Time, nullable=True)  # Horário específico do agendamento
    prioridade = db.Column(db.Integer, default=1)  # 1 = baixa, 5 = alta
    posicao_fila = db.Column(db.Integer, default=1)  # posição na fila
    
    # Dados de tempo
    tempo_extra_minutos = db.Column(db.Integer, default=0)
    motivo_tempo_extra = db.Column(db.String(200), nullable=True)
    
    # Dados do cliente
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone_cliente = db.Column(db.String(20), nullable=True)
    
    # Dados do veículo
    marca_carro = db.Column(db.String(50), nullable=False)
    modelo_carro = db.Column(db.String(50), nullable=False)
    cor_carro = db.Column(db.String(30), nullable=True)
    placa_carro = db.Column(db.String(10), nullable=True)
    
    # Status e observações
    status = db.Column(db.String(20), default='agendado')  # agendado, iniciado, cancelado
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

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
            'data_agendamento': self.data_agendamento.isoformat() if self.data_agendamento else None,
            'horario_agendamento': self.horario_agendamento.isoformat() if self.horario_agendamento else None,
            'prioridade': self.prioridade,
            'posicao_fila': self.posicao_fila,
            'tempo_extra_minutos': self.tempo_extra_minutos,
            'motivo_tempo_extra': self.motivo_tempo_extra,
            'nome_cliente': self.nome_cliente,
            'telefone_cliente': self.telefone_cliente,
            'marca_carro': self.marca_carro,
            'modelo_carro': self.modelo_carro,
            'cor_carro': self.cor_carro,
            'placa_carro': self.placa_carro,
            'status': self.status,
            'observacoes': self.observacoes,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'box': self.box.to_dict() if self.box else None,
            'mecanico': self.mecanico.to_dict() if self.mecanico else None,
            'tipo_servico': self.tipo_servico.to_dict() if self.tipo_servico else None
        }

