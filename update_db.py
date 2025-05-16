from app import create_app, db
from app.models.models import User, Room, Participant
import sqlite3
import os

# Criar a aplicação
app = create_app()

# Caminho para o banco de dados
db_path = 'app/esportes.db'

# Verificar se o arquivo existe
if os.path.exists(db_path):
    try:
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(rooms)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Adicionar coluna is_private se não existir
        if 'is_private' not in column_names:
            cursor.execute("ALTER TABLE rooms ADD COLUMN is_private BOOLEAN DEFAULT 0")
            print("Coluna 'is_private' adicionada com sucesso à tabela 'rooms'!")
        else:
            print("A coluna 'is_private' já existe na tabela 'rooms'.")
            
        # Adicionar coluna location se não existir
        if 'location' not in column_names:
            cursor.execute("ALTER TABLE rooms ADD COLUMN location TEXT")
            print("Coluna 'location' adicionada com sucesso à tabela 'rooms'!")
        else:
            print("A coluna 'location' já existe na tabela 'rooms'.")
        
        # Confirmar as alterações
        conn.commit()
        
        # Fechar a conexão
        conn.close()
        
        print("Banco de dados atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
else:
    print(f"O arquivo de banco de dados {db_path} não foi encontrado.")
    print("Criando um novo banco de dados...")
    
    # Criar o contexto da aplicação
    with app.app_context():
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
        
        print("Banco de dados criado com sucesso!")
        print('Usuários criados:')
        print('- Admin: admin / admin123')
        print('- Usuário: usuario / usuario123') 