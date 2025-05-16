from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.models import Room
from app.models.forms import SearchRoomForm
from app.utils.cities import search_cities, get_cities_from_api
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial com lista de salas ativas"""
    search_form = SearchRoomForm()
    
    # Filtrar por esporte e/ou cidade se especificado
    sport_filter = request.args.get('sport')
    city_filter = request.args.get('city')
    
    # Construir a query base para salas ativas e públicas
    rooms_query = Room.query.filter(Room.is_active == True, Room.is_private == False)
    
    # Aplicar filtros se especificados
    if sport_filter:
        rooms_query = rooms_query.filter(Room.sport.ilike(f'%{sport_filter}%'))
    
    if city_filter:
        rooms_query = rooms_query.filter(Room.city == city_filter)
    
    # Executar a query e ordenar por data
    rooms = rooms_query.order_by(Room.date).all()
    
    # Separar salas em próximas e passadas
    now = datetime.utcnow()
    upcoming_rooms = [room for room in rooms if room.date > now]
    past_rooms = [room for room in rooms if room.date <= now]
    
    # Obter as participações do usuário atual (se estiver logado)
    user_participations = []
    if current_user.is_authenticated:
        user_participations = [p.room_id for p in current_user.participations if p.is_active]
    
    return render_template('index.html', 
                          upcoming_rooms=upcoming_rooms, 
                          past_rooms=past_rooms,
                          search_form=search_form,
                          user_participations=user_participations)

@main_bp.route('/sobre')
def about():
    """Página sobre o projeto"""
    return render_template('about.html')

@main_bp.route('/api/cidades')
def search_cities_api():
    """API para pesquisa de cidades (autocompletar)"""
    query = request.args.get('q', '')
    results = search_cities(query)
    return jsonify(results)

@main_bp.route('/admin/atualizar-cidades')
@login_required
def update_cities_cache():
    """Atualiza o cache de cidades (apenas para administradores)"""
    # Verificar se o usuário é administrador (id=1)
    if current_user.id != 1:
        flash('Acesso negado. Apenas administradores podem atualizar o cache de cidades.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        cities = get_cities_from_api()
        flash(f'Cache de cidades atualizado com sucesso! {len(cities)} cidades carregadas.', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar o cache de cidades: {str(e)}', 'danger')
    
    return redirect(url_for('main.index')) 