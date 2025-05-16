from app import create_app
from app.utils.cities import get_cities_from_api

app = create_app()

with app.app_context():
    print("Buscando cidades da API do IBGE...")
    cities = get_cities_from_api()
    print(f"Total de cidades: {len(cities)}")
    print("Primeiras 10 cidades:")
    for city in cities[:10]:
        print(f"- {city}") 