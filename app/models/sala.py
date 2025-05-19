from app import db

class Sala(db.Model):
    __tablename__ = 'salas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    capacidade = db.Column(db.Integer)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo, manutenção
    
    def __repr__(self):
        return f'<Sala {self.id}: {self.nome}>' 