from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.models.models import Room
from app.models.forms import SearchRoomForm
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial com lista de salas ativas"""
    search_form = SearchRoomForm()
    
    # Filtrar por esporte se especificado
    sport_filter = request.args.get('sport')
    
    # Obter todas as salas ativas
    if sport_filter:
        rooms_query = Room.query.filter(Room.is_active == True, 
                               Room.sport.ilike(f'%{sport_filter}%'))
    else:
        rooms_query = Room.query.filter_by(is_active=True)
    
    # Filtrar salas privadas (mostrar apenas as públicas ou as privadas criadas pelo usuário atual)
    if current_user.is_authenticated:
        rooms = rooms_query.filter((Room.is_private == False) | 
                                  (Room.is_private == True) & (Room.creator_id == current_user.id)).order_by(Room.date).all()
    else:
        rooms = rooms_query.filter_by(is_private=False).order_by(Room.date).all()
    
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