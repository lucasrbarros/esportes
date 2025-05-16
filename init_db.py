from app import create_app, db
from app.models.models import User, Room, Participant

# Criar a aplicação
app = create_app()

# Criar o contexto da aplicação
with app.app_context():
    # Remover todas as tabelas existentes
    db.drop_all()
    
    # Criar todas as tabelas
    db.create_all()
    
    # Criar um usuário administrador
    admin = User(
        username='admin',
        email='admin@example.com',
        name='Administrador',
        password='admin123'
    )
    
    # Adicionar o usuário ao banco de dados
    db.session.add(admin)
    
    # Criar um usuário normal
    user = User(
        username='usuario',
        email='usuario@example.com',
        name='Usuário Teste',
        password='usuario123'
    )
    
    # Adicionar o usuário ao banco de dados
    db.session.add(user)
    
    # Confirmar as alterações
    db.session.commit()
    
    print('Banco de dados inicializado com sucesso!')
    print('Usuários criados:')
    print('- Admin: admin / admin123')
    print('- Usuário: usuario / usuario123') 