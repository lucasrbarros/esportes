import sqlite3
from app import create_app

app = create_app()

# Obter o caminho do banco de dados da configuração do Flask
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
if not db_path.startswith('/'):
    db_path = 'app/' + db_path

print(f"Verificando estrutura da tabela courts no banco {db_path}")

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Verificar a estrutura da tabela courts
c.execute("PRAGMA table_info(courts)")
columns = c.fetchall()

print("Estrutura da tabela courts:")
print("---------------------------")
for col in columns:
    # cid, name, type, notnull, default_value, pk
    print(f"Coluna {col[0]}: {col[1]} ({col[2]}), NOT NULL: {col[3]}, Default: {col[4]}, PK: {col[5]}")

# Fechar a conexão
conn.close() 