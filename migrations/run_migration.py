import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from add_valor_column import upgrade

with app.app_context():
    print("Executando migração para adicionar coluna valor...")
    upgrade()
    print("Migração concluída com sucesso!") 