from app import create_app, db
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app()

def upgrade_courts_table():
    """Atualiza a tabela courts para adicionar campo sport_type"""
    try:
        print("\n\n===== INICIANDO MIGRAÇÃO DA TABELA COURTS =====")
        logger.info("Iniciando migração da tabela courts")
        # Conectar ao banco diretamente usando sqlite3
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        logger.info(f"Conectando ao banco de dados: {db_path}")
        print(f"Caminho do banco de dados: {db_path}")
        
        # Se for um caminho relativo, ajustar
        if not db_path.startswith('/'):
            db_path = 'app/' + db_path
        
        print(f"Caminho completo: {os.path.abspath(db_path)}")
        print(f"Arquivo existe: {os.path.exists(db_path)}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar se a tabela courts existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courts'")
        table_exists = c.fetchone()
        print(f"Tabela courts existe: {table_exists is not None}")
        
        if not table_exists:
            print("Criando tabela courts...")
            c.execute("""
            CREATE TABLE courts (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                description TEXT,
                sport_type VARCHAR(50) NOT NULL DEFAULT 'Outros',
                hourly_price FLOAT NOT NULL DEFAULT 0.0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                capacity INTEGER NOT NULL DEFAULT 10
            )
            """)
            conn.commit()
            print("Tabela courts criada com sucesso!")
            return
        
        # Verificar colunas existentes
        c.execute("PRAGMA table_info(courts)")
        columns_data = c.fetchall()
        columns = [col[1] for col in columns_data]
        print(f"Colunas existentes: {columns}")
        print(f"Dados completos das colunas: {columns_data}")
        
        # Adicionar colunas faltantes
        required_columns = {
            'sport_type': 'VARCHAR(50) NOT NULL DEFAULT "Outros"',
            'hourly_price': 'FLOAT NOT NULL DEFAULT 0.0',
            'is_active': 'BOOLEAN DEFAULT 1',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'capacity': 'INTEGER NOT NULL DEFAULT 10'
        }
        
        for col_name, col_def in required_columns.items():
            if col_name not in columns:
                print(f"Adicionando coluna {col_name}...")
                try:
                    c.execute(f"ALTER TABLE courts ADD COLUMN {col_name} {col_def}")
                    print(f"Coluna {col_name} adicionada com sucesso")
                except Exception as e:
                    print(f"Erro ao adicionar coluna {col_name}: {str(e)}")
        
        conn.commit()
        
        # Verificar colunas após a alteração
        c.execute("PRAGMA table_info(courts)")
        columns_after = [col[1] for col in c.fetchall()]
        print(f"Colunas após alteração: {columns_after}")
        
        print("Migração da tabela courts concluída com sucesso!")
    except Exception as e:
        print(f"ERRO DURANTE A MIGRAÇÃO: {str(e)}")
        logger.error(f"Erro durante a migração: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    upgrade_courts_table() 