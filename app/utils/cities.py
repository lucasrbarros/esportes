"""
Utilitário com lista de cidades brasileiras para seleção nos formulários
Utiliza a API do IBGE para obter a lista de cidades
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Caminho para o arquivo de cache
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cities_cache.json')
# Tempo de expiração do cache em dias
CACHE_EXPIRATION_DAYS = 30

def get_cities_from_api():
    """
    Obtém a lista de cidades da API do IBGE
    
    Returns:
        list: Lista de cidades no formato "Nome - UF"
    """
    try:
        # Primeiro, obter todos os estados
        estados_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
        estados_response = requests.get(estados_url)
        estados_response.raise_for_status()
        
        # Criar um dicionário de estados por ID
        estados = {}
        for estado in estados_response.json():
            estados[estado['id']] = estado['sigla']
        
        # Agora, obter todos os municípios
        municipios_url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
        municipios_response = requests.get(municipios_url)
        municipios_response.raise_for_status()
        
        # Processar os dados
        cidades = ["Não informada"]
        
        # Tenta extrair os dados de cada município
        for municipio in municipios_response.json():
            try:
                nome_municipio = municipio['nome']
                
                # Navegar através da estrutura para obter o ID do estado
                estado_id = None
                if 'microrregiao' in municipio and 'mesorregiao' in municipio['microrregiao']:
                    if 'UF' in municipio['microrregiao']['mesorregiao']:
                        estado_id = municipio['microrregiao']['mesorregiao']['UF']['id']
                
                # Se encontrou o ID do estado, obter a sigla
                if estado_id and estado_id in estados:
                    sigla_estado = estados[estado_id]
                    cidade_completa = f"{nome_municipio} - {sigla_estado}"
                    cidades.append(cidade_completa)
            except Exception as e:
                # Se ocorrer qualquer erro ao processar um município, apenas pula para o próximo
                print(f"Erro ao processar município: {e}")
                continue
        
        # Se não conseguiu obter nenhuma cidade além de "Não informada", usa a lista padrão
        if len(cidades) <= 1:
            print("Nenhuma cidade obtida da API. Usando lista padrão.")
            return get_default_cities()
        
        # Ordenar por nome
        cidades = sorted(cidades)
        
        # Salvar no cache
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "cities": cidades
        }
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False)
        
        return cidades
    except Exception as e:
        print(f"Erro ao obter cidades da API: {e}")
        # Em caso de erro, retorna uma lista padrão
        return get_default_cities()

def get_cities_from_cache():
    """
    Obtém a lista de cidades do cache
    
    Returns:
        list: Lista de cidades do cache ou None se o cache não existir ou estiver expirado
    """
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Verificar se o cache expirou
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        expiration_time = datetime.now() - timedelta(days=CACHE_EXPIRATION_DAYS)
        
        if cache_time < expiration_time:
            return None
        
        return cache_data['cities']
    except Exception as e:
        print(f"Erro ao ler cache: {e}")
        return None

def get_default_cities():
    """
    Retorna uma lista padrão de cidades brasileiras
    
    Returns:
        list: Lista padrão de cidades brasileiras
    """
    return [
        "Não informada",
        "São Paulo - SP",
        "Rio de Janeiro - RJ",
        "Brasília - DF",
        "Salvador - BA",
        "Fortaleza - CE",
        "Belo Horizonte - MG",
        "Manaus - AM",
        "Curitiba - PR",
        "Recife - PE",
        "Porto Alegre - RS",
        "Belém - PA",
        "Goiânia - GO",
        "Guarulhos - SP",
        "Campinas - SP",
        "São Luís - MA",
        "São Gonçalo - RJ",
        "Maceió - AL",
        "Duque de Caxias - RJ",
        "Natal - RN",
        "Campo Grande - MS",
        "Teresina - PI",
        "São Bernardo do Campo - SP",
        "Nova Iguaçu - RJ",
        "João Pessoa - PB",
        "Santo André - SP",
        "São José dos Campos - SP",
        "Osasco - SP",
        "Jaboatão dos Guararapes - PE",
        "Ribeirão Preto - SP",
        "Uberlândia - MG",
        "Sorocaba - SP",
        "Contagem - MG",
        "Aracaju - SE",
        "Feira de Santana - BA",
        "Cuiabá - MT",
        "Joinville - SC",
        "Juiz de Fora - MG",
        "Londrina - PR",
        "Aparecida de Goiânia - GO",
        "Niterói - RJ",
        "Ananindeua - PA",
        "Porto Velho - RO",
        "Florianópolis - SC",
        "Vitória - ES",
        "Santos - SP",
        "Maringá - PR",
        "Mauá - SP",
        "Diadema - SP",
        "São José do Rio Preto - SP",
        "Carapicuíba - SP",
        "Piracicaba - SP",
        "Montes Claros - MG",
        "Bauru - SP",
        "Jundiaí - SP",
        "Olinda - PE",
        "Campina Grande - PB",
        "Anápolis - GO",
        "Franca - SP",
        "Macapá - AP",
        "Rio Branco - AC",
        "Boa Vista - RR",
        "Palmas - TO",
    ]

def get_all_cities():
    """
    Obtém a lista completa de cidades brasileiras
    Tenta obter do cache primeiro, depois da API e, se falhar, usa a lista padrão
    
    Returns:
        list: Lista de cidades brasileiras
    """
    cities = get_cities_from_cache()
    if cities is None:
        cities = get_cities_from_api()
    return cities

def get_cities_list():
    """
    Retorna a lista de cidades em formato para uso em SelectField
    
    Returns:
        list: Lista de tuplas (valor, rótulo) para uso em SelectField
    """
    cities = get_all_cities()
    return [(city, city) for city in cities]

def search_cities(query):
    """
    Pesquisa cidades que correspondem à consulta
    
    Args:
        query (str): Texto para pesquisar
        
    Returns:
        list: Lista de cidades que correspondem à pesquisa
    """
    if not query or len(query) < 2:
        return []
        
    query = query.lower()
    cities = get_all_cities()
    results = [city for city in cities if query in city.lower()]
    return results[:20]  # Limitar a 20 resultados para não sobrecarregar a interface 