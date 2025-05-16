# Esportes em Grupo

Sistema web para organização de partidas esportivas em grupo, desenvolvido com Python (Flask) e SQLite.

## Objetivo

Substituir listas manuais de confirmação (como em grupos de mensagens), tornando o processo mais automatizado e prático. O sistema permite criar "salas" para diferentes esportes, nas quais os participantes podem se inscrever via link.

## Funcionalidades

### 1. Criação de salas de jogos
- Definir nome do esporte (ex: vôlei, futebol, basquete)
- Especificar data e horário
- Definir quantidade máxima de participantes
- Adicionar descrição (opcional)
- Gerar link único para inscrições

### 2. Inscrição de participantes
- Visualização dos detalhes da sala
- Inscrição simples com nome
- Exibição da posição na fila
- Lista de espera automática quando a sala está cheia

### 3. Painel do Organizador
- Visualização da lista de inscritos
- Remoção de participantes
- Encerramento da sala
- Compartilhamento do link da sala

### 4. Dashboard / Página Inicial
- Listagem de todas as salas ativas
- Informações sobre cada sala
- Filtro por esporte

## Tecnologias utilizadas

- **Backend**: Python 3.x com Flask
- **Frontend**: HTML, CSS e Bootstrap 5
- **Banco de dados**: SQLite com SQLAlchemy
- **Formulários**: Flask-WTF

## Instalação e execução

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/esportes-em-grupo.git
cd esportes-em-grupo
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute a aplicação:
```
python app.py
```

5. Acesse no navegador:
```
http://localhost:5000
```

## Estrutura do projeto

```
esportes/
├── app/
│   ├── controllers/
│   │   ├── main_routes.py
│   │   └── room_routes.py
│   ├── models/
│   │   ├── forms.py
│   │   └── models.py
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   ├── templates/
│   │   ├── about.html
│   │   ├── create_room.html
│   │   ├── index.html
│   │   ├── layout.html
│   │   ├── manage_room.html
│   │   └── view_room.html
│   └── __init__.py
├── app.py
├── requirements.txt
└── README.md
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests. 