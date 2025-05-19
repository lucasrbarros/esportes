from app import db
from datetime import date

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)  # Formato HH:MM
    hora_fim = db.Column(db.String(5), nullable=False)    # Formato HH:MM
    responsavel = db.Column(db.String(100), nullable=False)
    observacoes = db.Column(db.Text)
    
    # Relacionamento com a sala
    sala = db.relationship('Sala', backref=db.backref('reservas', lazy=True))
    
    def __repr__(self):
        return f'<Reserva {self.id}: {self.sala.nome} - {self.data} {self.hora_inicio}-{self.hora_fim}>' 