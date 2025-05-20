from app import create_app, db
from app.models.models import Court

app = create_app()

with app.app_context():
    try:
        print("Testando a criação de uma quadra")
        
        # Verificar se a tabela existe
        tables = db.metadata.tables.keys()
        print(f"Tabelas existentes no banco: {list(tables)}")
        
        # Criar uma nova quadra
        new_court = Court(
            name="Quadra de Teste",
            sport_type="Futebol",
            hourly_price=50.0,
            location="Local de teste",
            description="Descrição de teste",
            capacity=15,
            city="São Paulo"
        )
        
        print(f"Objeto quadra criado: {new_court}")
        
        # Salvar no banco de dados
        db.session.add(new_court)
        db.session.commit()
        
        print(f"Quadra salva com sucesso! ID: {new_court.id}")
        
        # Buscar todas as quadras para confirmar
        courts = Court.query.all()
        print(f"Total de quadras encontradas: {len(courts)}")
        
        for court in courts:
            print(f"ID: {court.id}, Nome: {court.name}, Preço: {court.hourly_price}, Esporte: {court.sport_type}, Cidade: {court.city}")
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback() 