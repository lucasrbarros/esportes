from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.models.models import Room, User, Participant
from app import db
from datetime import datetime
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    rooms = Room.query.all()
    return render_template('admin.html', rooms=rooms)

@admin_bp.route('/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    sport = request.args.get('sport')
    date = request.args.get('date')
    
    query = Room.query
    
    if sport:
        query = query.filter_by(sport=sport)
    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(db.func.date(Room.date) == date_obj)
    
    rooms = query.all()
    
    eventos = []
    for room in rooms:
        eventos.append({
            'id': room.id,
            'title': f"{room.name} - {room.sport}",
            'start': room.date.isoformat(),
            'end': room.date.isoformat(),  # Ajuste conforme necessário
            'sport': room.sport,
            'max_participants': room.max_participants,
            'current_participants': len(room.get_active_participants()),
            'location': room.location,
            'city': room.city,
            'description': room.description,
            'is_private': room.is_private,
            'is_active': room.is_active,
            'valor': room.valor
        })
    
    return jsonify(eventos)

@admin_bp.route('/api/rooms', methods=['POST'])
@login_required
def criar_room():
    data = request.json
    
    nova_room = Room(
        name=data['name'],
        sport=data['sport'],
        date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M'),
        max_participants=data['max_participants'],
        creator_id=current_user.id,
        description=data.get('description', ''),
        is_private=data.get('is_private', False),
        location=data.get('location', ''),
        city=data.get('city', 'Não informada'),
        valor=data.get('valor', 0.0)
    )
    
    db.session.add(nova_room)
    db.session.commit()
    
    return jsonify({'message': 'Quadra criada com sucesso', 'id': nova_room.id})

@admin_bp.route('/api/rooms', methods=['PUT'])
@login_required
def atualizar_room():
    data = request.json
    
    room = Room.query.get_or_404(data['id'])
    
    room.name = data['name']
    room.sport = data['sport']
    room.date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
    room.max_participants = data['max_participants']
    room.description = data.get('description', '')
    room.is_private = data.get('is_private', False)
    room.location = data.get('location', '')
    room.city = data.get('city', 'Não informada')
    room.is_active = data.get('is_active', True)
    room.valor = data.get('valor', 0.0)
    
    db.session.commit()
    
    return jsonify({'message': 'Quadra atualizada com sucesso'})

@admin_bp.route('/api/rooms/<int:id>', methods=['DELETE'])
@login_required
def excluir_room(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    
    return jsonify({'message': 'Quadra excluída com sucesso'})

@admin_bp.route('/api/rooms/<int:room_id>/participants', methods=['GET'])
@login_required
def get_participants(room_id):
    room = Room.query.get_or_404(room_id)
    participants = room.participants
    
    participantes = []
    for p in participants:
        participantes.append({
            'id': p.id,
            'user_id': p.user_id,
            'user_name': p.user.name,
            'user_email': p.user.email,
            'registered_at': p.registered_at.isoformat(),
            'is_active': p.is_active,
            'checked_in': p.checked_in,
            'pagamento_status': p.pagamento_status,
            'pagamento_data': p.pagamento_data.isoformat() if p.pagamento_data else None,
            'pagamento_metodo': p.pagamento_metodo,
            'observacoes': p.observacoes,
            'is_in_waiting_list': p.is_in_waiting_list()
        })
    
    return jsonify(participantes)

@admin_bp.route('/api/rooms/<int:room_id>/participants/<int:participant_id>', methods=['PUT'])
@login_required
def atualizar_participant(room_id, participant_id):
    data = request.json
    participant = Participant.query.get_or_404(participant_id)
    
    if participant.room_id != room_id:
        return jsonify({'error': 'Participante não pertence a esta quadra'}), 400
    
    participant.is_active = data.get('is_active', participant.is_active)
    participant.checked_in = data.get('checked_in', participant.checked_in)
    participant.pagamento_status = data.get('pagamento_status', participant.pagamento_status)
    participant.pagamento_metodo = data.get('pagamento_metodo', participant.pagamento_metodo)
    participant.observacoes = data.get('observacoes', participant.observacoes)
    
    if data.get('pagamento_status') == 'pago' and not participant.pagamento_data:
        participant.pagamento_data = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Participante atualizado com sucesso'})

@admin_bp.route('/api/rooms/<int:room_id>/participants/<int:participant_id>', methods=['DELETE'])
@login_required
def remover_participant(room_id, participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    if participant.room_id != room_id:
        return jsonify({'error': 'Participante não pertence a esta quadra'}), 400
    
    db.session.delete(participant)
    db.session.commit()
    
    return jsonify({'message': 'Participante removido com sucesso'}) 