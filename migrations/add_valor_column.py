from app import db

def upgrade():
    # Adiciona a coluna valor à tabela rooms
    db.engine.execute('ALTER TABLE rooms ADD COLUMN valor FLOAT DEFAULT 0.0')

def downgrade():
    # Remove a coluna valor da tabela rooms
    db.engine.execute('ALTER TABLE rooms DROP COLUMN valor') 