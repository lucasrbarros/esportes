from app import create_app, db
from app.models.models import User, Room, Participant
from app.models.sala import Sala

def init_db():
    app = create_app()
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        
        # Verifica se já existem salas
        if Sala.query.count() == 0:
            # Cria algumas salas de exemplo
            salas = [
                Sala(nome='Sala de Reunião 1', capacidade=10, descricao='Sala de reunião pequena'),
                Sala(nome='Sala de Reunião 2', capacidade=20, descricao='Sala de reunião média'),
                Sala(nome='Auditório', capacidade=50, descricao='Auditório para eventos maiores'),
                Sala(nome='Sala de Treinamento', capacidade=30, descricao='Sala para treinamentos'),
                Sala(nome='Sala de Conferência', capacidade=15, descricao='Sala para videoconferências')
            ]
            
            # Adiciona as salas ao banco de dados
            for sala in salas:
                db.session.add(sala)
            
            # Commit das alterações
            db.session.commit()
            print("Banco de dados inicializado com sucesso!")
        else:
            print("O banco de dados já contém salas.")

if __name__ == '__main__':
    init_db() 