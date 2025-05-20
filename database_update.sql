-- Instruções para atualizar o banco de dados com a nova estrutura de quadras
-- Execute estes comandos no seu gerenciador de banco de dados

-- Criar tabela de quadras
CREATE TABLE IF NOT EXISTS courts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    description TEXT,
    sport_type VARCHAR(50) NOT NULL,
    hourly_price FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    capacity INTEGER DEFAULT 10
);

-- Adicionar campos para relação com quadras na tabela rooms
ALTER TABLE rooms ADD COLUMN court_id INTEGER;
ALTER TABLE rooms ADD COLUMN duration_hours FLOAT DEFAULT 1.0;
ALTER TABLE rooms ADD COLUMN end_time TIMESTAMP;

-- Adicionar restrição de chave estrangeira (pode não ser suportado em alguns bancos)
-- Caso não suporte, você pode ignorar esta linha
ALTER TABLE rooms ADD CONSTRAINT fk_court FOREIGN KEY (court_id) REFERENCES courts(id);

-- Criar algumas quadras de exemplo
INSERT INTO courts (name, sport_type, hourly_price, location, capacity) VALUES
('Quadra de Futebol Society', 'Futebol', 150.00, 'Rua das Flores, 123', 14),
('Quadra de Vôlei de Areia', 'Vôlei', 100.00, 'Av. Paulista, 1000', 12),
('Quadra de Basquete Coberta', 'Basquete', 120.00, 'Rua dos Esportes, 456', 10),
('Quadra de Tênis Premium', 'Tênis', 180.00, 'Condomínio Clube, 789', 4),
('Salão de Futsal', 'Futebol', 140.00, 'Centro Esportivo', 10);

-- Nota para SQLite:
-- Se estiver usando SQLite, você pode precisar ativar as chaves estrangeiras com:
PRAGMA foreign_keys = ON;