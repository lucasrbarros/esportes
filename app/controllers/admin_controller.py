from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.models.models import Room, User, Participant, Court
from app import db
from datetime import datetime, timedelta
from flask_login import login_required, current_user
import traceback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    rooms = Room.query.all()
    return render_template('admin.html', rooms=rooms)

# ===============================
# API para Gestão de Quadras
# ===============================

@admin_bp.route('/api/courts', methods=['GET'])
@login_required
def get_courts():
    """Retorna todas as quadras cadastradas"""
    courts = Court.query.all()
    
    result = []
    for court in courts:
        result.append({
            'id': court.id,
            'name': court.name,
            'location': court.location,
            'description': court.description,
            'sport_type': court.sport_type,
            'hourly_price': court.hourly_price,
            'is_active': court.is_active,
            'capacity': court.capacity,
            'created_at': court.created_at.isoformat()
        })
    
    return jsonify(result)

@admin_bp.route('/api/courts/<int:court_id>', methods=['GET'])
@login_required
def get_court(court_id):
    """Retorna detalhes de uma quadra específica"""
    court = Court.query.get_or_404(court_id)
    
    result = {
        'id': court.id,
        'name': court.name,
        'location': court.location,
        'description': court.description,
        'sport_type': court.sport_type,
        'hourly_price': court.hourly_price,
        'is_active': court.is_active,
        'capacity': court.capacity,
        'created_at': court.created_at.isoformat()
    }
    
    return jsonify(result)

@admin_bp.route('/api/courts', methods=['POST'])
@login_required
def create_court():
    """Cria uma nova quadra"""
    try:
        print("========= Criando nova quadra =========")
        data = request.json
        
        if not data:
            print("Erro: Dados vazios na requisição")
            return jsonify({
                'message': 'Nenhum dado recebido',
                'error': True
            }), 400
        
        print(f"Dados recebidos: {data}")
        
        # Validação de campos obrigatórios
        required_fields = ['name', 'sport_type', 'hourly_price']
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"Erro: Campo obrigatório ausente ou vazio: {field}")
                return jsonify({
                    'message': f'Campo obrigatório ausente ou vazio: {field}',
                    'error': True
                }), 400
        
        # Criar a nova quadra
        court = Court(
            name=data['name'],
            sport_type=data['sport_type'],
            hourly_price=float(data['hourly_price']),
            location=data.get('location', ''),
            description=data.get('description', ''),
            capacity=data.get('capacity', 10),
            is_active=data.get('is_active', True),
            city=data.get('city', 'Cidade')
        )
        
        # Garantir que valor_hora esteja sincronizado com hourly_price
        court.valor_hora = float(data['hourly_price'])
        
        db.session.add(court)
        db.session.commit()
        
        print(f"Quadra criada com sucesso. ID: {court.id}")
        
        return jsonify({
            'message': 'Quadra criada com sucesso',
            'id': court.id,
            'error': False
        })
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar quadra: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'message': f'Erro ao criar quadra: {str(e)}',
            'error': True
        }), 500

@admin_bp.route('/api/courts/<int:court_id>', methods=['PUT'])
@login_required
def update_court(court_id):
    """Atualiza detalhes de uma quadra"""
    court = Court.query.get_or_404(court_id)
    data = request.json
    
    court.name = data['name']
    court.sport_type = data['sport_type']
    court.hourly_price = float(data['hourly_price'])
    court.location = data.get('location')
    court.description = data.get('description')
    court.capacity = int(data.get('capacity', 10))
    court.is_active = data.get('is_active', True)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Quadra atualizada com sucesso'
    })

@admin_bp.route('/api/courts/<int:court_id>', methods=['DELETE'])
@login_required
def delete_court(court_id):
    """Remove uma quadra"""
    court = Court.query.get_or_404(court_id)
    
    # Verificar se existem jogos agendados para esta quadra
    future_reservations = Room.query.filter(
        Room.court_id == court_id,
        Room.date > datetime.utcnow(),
        Room.is_active == True
    ).count()
    
    if future_reservations > 0:
        return jsonify({
            'message': 'Não é possível excluir esta quadra pois existem jogos agendados para ela',
            'error': True
        }), 400
    
    db.session.delete(court)
    db.session.commit()
    
    return jsonify({
        'message': 'Quadra excluída com sucesso'
    })

@admin_bp.route('/api/courts/<int:court_id>/availability', methods=['GET'])
@login_required
def check_court_availability(court_id):
    """Verifica a disponibilidade de uma quadra em uma data específica"""
    court = Court.query.get_or_404(court_id)
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({
            'message': 'Data não especificada',
            'error': True
        }), 400
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'message': 'Formato de data inválido. Use YYYY-MM-DD',
            'error': True
        }), 400
    
    # Buscar reservas existentes nesta data
    reservations = court.get_reservations_for_day(date)
    
    # Formatar informações de disponibilidade
    availability = []
    
    # Criar slots de 1 hora das 6h às 22h
    start_hour = 6
    end_hour = 22
    
    for hour in range(start_hour, end_hour):
        slot_start = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour)
        slot_end = slot_start + timedelta(hours=1)
        
        # Verificar se o slot está ocupado
        is_available = True
        conflicting_reservation = None
        
        for reservation in reservations:
            # Um slot está ocupado se qualquer parte dele se sobrepuser a uma reserva
            if (reservation.date < slot_end and 
                reservation.end_time > slot_start):
                is_available = False
                conflicting_reservation = {
                    'id': reservation.id,
                    'name': reservation.name,
                    'start': reservation.date.isoformat(),
                    'end': reservation.end_time.isoformat()
                }
                break
        
        slot = {
            'start': slot_start.isoformat(),
            'end': slot_end.isoformat(),
            'is_available': is_available
        }
        
        if conflicting_reservation:
            slot['reservation'] = conflicting_reservation
            
        availability.append(slot)
    
    return jsonify({
        'court_id': court_id,
        'court_name': court.name,
        'date': date_str,
        'availability': availability
    })

# ===============================
# API para Gestão de Salas/Jogos
# ===============================

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
        # Calcular valor por pessoa
        valor_por_pessoa = room.valor
        if room.court_id:
            valor_por_pessoa = room.calculate_price_per_person()
        
        eventos.append({
            'id': room.id,
            'title': f"{room.name} - {room.sport}",
            'start': room.date.isoformat(),
            'end': room.end_time.isoformat() if room.end_time else room.date.isoformat(),
            'sport': room.sport,
            'max_participants': room.max_participants,
            'current_participants': len(room.get_active_participants()),
            'location': room.location,
            'city': room.city,
            'description': room.description,
            'is_private': room.is_private,
            'is_active': room.is_active,
            'valor': valor_por_pessoa,
            'court_id': room.court_id,
            'duration_hours': room.duration_hours,
            'court_name': room.court.name if room.court else None,
            'court_price': room.court.hourly_price if room.court else None,
            'total_price': room.calculate_total_price() if room.court_id else None
        })
    
    return jsonify(eventos)

@admin_bp.route('/api/rooms', methods=['POST'])
@login_required
def criar_room():
    data = request.json
    
    # Calcular data de término com base na duração
    date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
    duration_hours = float(data.get('duration_hours', 1.0))
    end_time = date + timedelta(hours=duration_hours)
    
    nova_room = Room(
        name=data['name'],
        sport=data['sport'],
        date=date,
        max_participants=data['max_participants'],
        creator_id=current_user.id,
        description=data.get('description', ''),
        is_private=data.get('is_private', False),
        location=data.get('location', ''),
        city=data.get('city', 'Não informada'),
        valor=float(data.get('valor', 0.0)),
        court_id=data.get('court_id'),
        duration_hours=duration_hours
    )
    
    # Definir explicitamente o end_time
    nova_room.end_time = end_time
    
    # Verificar a disponibilidade da quadra, se especificada
    if nova_room.court_id:
        court = Court.query.get(nova_room.court_id)
        if court and not court.is_available(date, end_time):
            return jsonify({
                'message': 'A quadra não está disponível no horário selecionado',
                'error': True
            }), 400
    
    db.session.add(nova_room)
    db.session.commit()
    
    return jsonify({'message': 'Jogo criado com sucesso', 'id': nova_room.id})

@admin_bp.route('/api/rooms', methods=['PUT'])
@login_required
def atualizar_room():
    data = request.json
    
    room = Room.query.get_or_404(data['id'])
    
    # Verificar se há alteração na data ou duração
    old_date = room.date
    old_end_time = room.end_time
    old_court_id = room.court_id
    
    # Atualizar os campos básicos
    room.name = data['name']
    room.sport = data['sport']
    room.date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
    room.max_participants = data['max_participants']
    room.description = data.get('description', '')
    room.is_private = data.get('is_private', False)
    room.location = data.get('location', '')
    room.city = data.get('city', 'Não informada')
    room.is_active = data.get('is_active', True)
    room.valor = float(data.get('valor', 0.0))
    room.court_id = data.get('court_id')
    room.duration_hours = float(data.get('duration_hours', 1.0))
    
    # Recalcular o horário de término
    room.end_time = room.date + timedelta(hours=room.duration_hours)
    
    # Verificar disponibilidade da quadra se houver mudança
    date_changed = old_date != room.date or old_end_time != room.end_time
    court_changed = old_court_id != room.court_id
    
    if room.court_id and (date_changed or court_changed):
        court = Court.query.get(room.court_id)
        
        # Verificar se a nova data/quadra está disponível (excluindo a própria reserva)
        overlapping = Room.query.filter(
            Room.id != room.id,
            Room.court_id == room.court_id,
            Room.is_active == True,
            Room.date < room.end_time,
            Room.end_time > room.date
        ).count()
        
        if overlapping > 0:
            return jsonify({
                'message': 'A quadra não está disponível no horário selecionado',
                'error': True
            }), 400
    
    db.session.commit()
    
    return jsonify({'message': 'Jogo atualizado com sucesso'})

@admin_bp.route('/api/rooms/<int:id>', methods=['DELETE'])
@login_required
def excluir_room(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    
    return jsonify({'message': 'Jogo excluído com sucesso'})

@admin_bp.route('/api/rooms/<int:room_id>/participants', methods=['GET'])
@login_required
def get_participants(room_id):
    room = Room.query.get_or_404(room_id)
    participants = room.participants
    
    # Debug
    print(f"Sala {room.name}: {len(participants)} participantes encontrados")
    
    # Calcular valor por pessoa
    valor_por_pessoa = room.calculate_price_per_person() if room.court_id else room.valor
    
    participantes = []
    for p in participants:
        is_in_waiting = p.is_in_waiting_list()
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
            'is_in_waiting_list': is_in_waiting,
            'valor': valor_por_pessoa
        })
        
        # Debug para cada participante
        print(f"Participante {p.user.name}: ativo={p.is_active}, lista_espera={is_in_waiting}")
    
    return jsonify(participantes)

@admin_bp.route('/api/rooms/<int:room_id>/participants/<int:participant_id>', methods=['PUT'])
@login_required
def atualizar_participant(room_id, participant_id):
    data = request.json
    participant = Participant.query.get_or_404(participant_id)
    
    if participant.room_id != room_id:
        return jsonify({'error': 'Participante não pertence a este jogo'}), 400
    
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
        return jsonify({'error': 'Participante não pertence a este jogo'}), 400
    
    db.session.delete(participant)
    db.session.commit()
    
    return jsonify({'message': 'Participante removido com sucesso'})

@admin_bp.route('/api/rooms/<int:room_id>/participants/batch_update', methods=['POST'])
@login_required
def atualizar_participantes_lote(room_id):
    """Atualiza vários participantes de uma vez (pagamento em lote)"""
    data = request.json
    participant_ids = data.get('participant_ids', [])
    
    if not participant_ids:
        return jsonify({'error': 'Nenhum participante especificado'}), 400
    
    # Dados a serem atualizados
    update_data = {
        'pagamento_status': data.get('pagamento_status'),
        'pagamento_metodo': data.get('pagamento_metodo'),
        'checked_in': data.get('checked_in', False),
        'observacoes': data.get('observacoes')
    }
    
    # Atualizar pagamento_data apenas se for definido ou se for marcado como pago
    if data.get('pagamento_data'):
        try:
            update_data['pagamento_data'] = datetime.strptime(data.get('pagamento_data'), '%Y-%m-%dT%H:%M')
        except ValueError:
            # Se não for possível converter, usar a data atual
            update_data['pagamento_data'] = datetime.utcnow()
    elif update_data.get('pagamento_status') == 'pago':
        update_data['pagamento_data'] = datetime.utcnow()
    
    # Filtrar valores None
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    # Atualizar todos os participantes especificados
    participantes_atualizados = 0
    for p_id in participant_ids:
        participant = Participant.query.filter_by(id=p_id, room_id=room_id).first()
        if participant:
            for key, value in update_data.items():
                setattr(participant, key, value)
            participantes_atualizados += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'{participantes_atualizados} participantes atualizados com sucesso',
        'updated_count': participantes_atualizados
    })

@admin_bp.route('/api/estatisticas/resumo', methods=['GET'])
@login_required
def estatisticas_resumo():
    # Total de jogos
    total_jogos = Room.query.count()
    
    # Total de participantes únicos
    total_participantes = db.session.query(db.func.count(db.distinct(Participant.user_id))).scalar()
    
    # Média de jogadores por jogo
    total_participacoes = Participant.query.filter_by(is_active=True).count()
    media_jogadores = round(total_participacoes / total_jogos, 1) if total_jogos > 0 else 0
    
    # Total de esportes diferentes
    total_esportes = db.session.query(db.func.count(db.distinct(Room.sport))).scalar()
    
    # Jogos por mês
    # Formatar datas para agrupar por mês
    jogos_por_mes_query = db.session.query(
        db.func.strftime('%m/%Y', Room.date).label('mes'),
        db.func.count(Room.id).label('count')
    ).group_by('mes').order_by('mes').all()
    
    jogos_por_mes = [{'mes': res[0], 'quantidade': res[1]} for res in jogos_por_mes_query]
    
    # Próximos jogos
    proximos_jogos = Room.query.filter(
        Room.date >= datetime.now(),
        Room.is_active == True
    ).order_by(Room.date).limit(5).all()
    
    proximos_jogos_data = []
    for jogo in proximos_jogos:
        participantes_ativos = len(jogo.get_active_participants())
        proximos_jogos_data.append({
            'id': jogo.id,
            'name': jogo.name,
            'sport': jogo.sport,
            'date': jogo.date.isoformat(),
            'max_participants': jogo.max_participants,
            'participantes_ativos': participantes_ativos,
            'court_name': jogo.court.name if jogo.court else None
        })
    
    # Estatísticas de quadras
    total_quadras = Court.query.count()
    quadras_mais_usadas = db.session.query(
        Court.name, 
        db.func.count(Room.id).label('count')
    ).join(Room, Court.id == Room.court_id
    ).group_by(Court.id
    ).order_by(db.func.count(Room.id).desc()
    ).limit(5).all()
    
    quadras_stats = [{
        'name': quad[0], 
        'reservas': quad[1]
    } for quad in quadras_mais_usadas]
    
    return jsonify({
        'total_jogos': total_jogos,
        'total_participantes': total_participantes,
        'media_jogadores': media_jogadores,
        'total_esportes': total_esportes,
        'total_quadras': total_quadras,
        'jogos_por_mes': jogos_por_mes,
        'proximos_jogos': proximos_jogos_data,
        'quadras_mais_usadas': quadras_stats
    })

@admin_bp.route('/api/estatisticas/esportes', methods=['GET'])
@login_required
def estatisticas_esportes():
    """Retorna estatísticas relacionadas aos esportes"""
    
    # Distribuição de esportes
    distribuicao_query = db.session.query(
        Room.sport.label('esporte'),
        db.func.count(Room.id).label('quantidade')
    ).group_by(Room.sport).all()
    
    distribuicao = [{'esporte': res[0], 'quantidade': res[1]} for res in distribuicao_query]
    
    # Participantes por esporte
    participantes_por_esporte_query = db.session.query(
        Room.sport.label('esporte'),
        db.func.count(Participant.id).label('participantes')
    ).join(Participant, Room.id == Participant.room_id
    ).filter(Participant.is_active == True
    ).group_by(Room.sport).all()
    
    participantes_por_esporte = [{'esporte': res[0], 'participantes': res[1]} for res in participantes_por_esporte_query]
    
    # Detalhes por esporte
    detalhes_esportes = []
    for esporte in db.session.query(db.distinct(Room.sport)).all():
        nome_esporte = esporte[0]
        total_jogos = Room.query.filter_by(sport=nome_esporte).count()
        
        # Total de participantes para este esporte
        total_participantes = db.session.query(db.func.count(Participant.id)).join(
            Room, Room.id == Participant.room_id
        ).filter(
            Room.sport == nome_esporte,
            Participant.is_active == True
        ).scalar()
        
        # Média de participantes por jogo
        media_participantes = total_participantes / total_jogos if total_jogos > 0 else 0
        
        # Valor médio por jogo
        valor_medio_query = db.session.query(db.func.avg(Room.valor)).filter_by(sport=nome_esporte).scalar()
        valor_medio = valor_medio_query or 0
        
        detalhes_esportes.append({
            'nome': nome_esporte,
            'total_jogos': total_jogos,
            'total_participantes': total_participantes,
            'media_participantes': media_participantes,
            'valor_medio': valor_medio
        })
    
    return jsonify({
        'distribuicao': distribuicao,
        'participantes_por_esporte': participantes_por_esporte,
        'detalhes': detalhes_esportes
    })

@admin_bp.route('/api/estatisticas/jogadores', methods=['GET'])
@login_required
def estatisticas_jogadores():
    """Retorna estatísticas relacionadas aos jogadores"""
    
    # Jogadores mais frequentes (com mais participações)
    jogadores_frequentes_query = db.session.query(
        User.name.label('nome'),
        db.func.count(Participant.id).label('participacoes')
    ).join(
        Participant, User.id == Participant.user_id
    ).filter(
        Participant.is_active == True
    ).group_by(User.id
    ).order_by(db.func.count(Participant.id).desc()
    ).limit(10).all()
    
    jogadores_frequentes = [{'nome': res[0], 'jogos_participados': res[1]} for res in jogadores_frequentes_query]
    
    # Taxa de check-in
    com_checkin = Participant.query.filter_by(checked_in=True).count()
    sem_checkin = Participant.query.filter_by(checked_in=False).count()
    
    taxa_checkin = {
        'com_checkin': com_checkin,
        'sem_checkin': sem_checkin
    }
    
    # Ranking de jogadores
    ranking = []
    jogadores_query = db.session.query(
        User.id, User.name
    ).join(
        Participant, User.id == Participant.user_id
    ).filter(
        Participant.is_active == True
    ).group_by(User.id
    ).having(db.func.count(Participant.id) > 1
    ).order_by(db.func.count(Participant.id).desc()).all()
    
    for jogador_id, jogador_nome in jogadores_query:
        # Total de jogos que participou
        jogos_participados = Participant.query.filter_by(user_id=jogador_id, is_active=True).count()
        
        # Taxa de check-in
        checkins = Participant.query.filter_by(user_id=jogador_id, is_active=True, checked_in=True).count()
        taxa_checkin_jogador = checkins / jogos_participados if jogos_participados > 0 else 0
        
        # Esporte favorito (que mais participou)
        esporte_favorito_query = db.session.query(
            Room.sport.label('esporte'),
            db.func.count(Participant.id).label('count')
        ).join(
            Participant, Room.id == Participant.room_id
        ).filter(
            Participant.user_id == jogador_id,
            Participant.is_active == True
        ).group_by(Room.sport
        ).order_by(db.func.count(Participant.id).desc()).first()
        
        esporte_favorito = esporte_favorito_query[0] if esporte_favorito_query else "Não definido"
        
        ranking.append({
            'nome': jogador_nome,
            'jogos_participados': jogos_participados,
            'taxa_checkin': taxa_checkin_jogador,
            'esporte_favorito': esporte_favorito
        })
    
    return jsonify({
        'mais_frequentes': jogadores_frequentes,
        'taxa_checkin': taxa_checkin,
        'ranking': ranking
    })

@admin_bp.route('/api/estatisticas/financeiro', methods=['GET'])
@login_required
def estatisticas_financeiro():
    """Retorna estatísticas financeiras"""
    
    # Total arrecadado (participantes com status 'pago')
    total_arrecadado_query = db.session.query(
        db.func.sum(Room.valor)
    ).join(
        Participant, Room.id == Participant.room_id
    ).filter(
        Participant.pagamento_status == 'pago'
    ).scalar()
    
    total_arrecadado = total_arrecadado_query or 0
    
    # Total pendente (participantes com status 'pendente')
    total_pendente_query = db.session.query(
        db.func.sum(Room.valor)
    ).join(
        Participant, Room.id == Participant.room_id
    ).filter(
        Participant.pagamento_status == 'pendente',
        Participant.is_active == True
    ).scalar()
    
    total_pendente = total_pendente_query or 0
    
    # Valor médio por jogo
    valor_medio_jogo_query = db.session.query(db.func.avg(Room.valor)).scalar()
    valor_medio_jogo = valor_medio_jogo_query or 0
    
    # Arrecadação mensal
    arrecadacao_mensal_query = db.session.query(
        db.func.strftime('%m/%Y', Participant.pagamento_data).label('mes'),
        db.func.sum(Room.valor).label('valor')
    ).join(
        Room, Room.id == Participant.room_id
    ).filter(
        Participant.pagamento_status == 'pago',
        Participant.pagamento_data != None
    ).group_by('mes').order_by('mes').all()
    
    arrecadacao_mensal = [{'mes': res[0], 'valor': res[1]} for res in arrecadacao_mensal_query]
    
    # Status de pagamentos
    status_query = db.session.query(
        Participant.pagamento_status,
        db.func.count(Participant.id)
    ).filter(
        Participant.is_active == True
    ).group_by(Participant.pagamento_status).all()
    
    status_pagamentos = {status[0]: status[1] for status in status_query}
    
    # Últimos pagamentos
    ultimos_pagamentos_query = db.session.query(
        Participant.pagamento_data.label('data'),
        User.name.label('jogador'),
        Room.name.label('jogo'),
        Room.valor.label('valor'),
        Participant.pagamento_metodo.label('metodo'),
        Participant.pagamento_status.label('status')
    ).join(
        User, User.id == Participant.user_id
    ).join(
        Room, Room.id == Participant.room_id
    ).filter(
        Participant.pagamento_status.in_(['pago', 'pendente']),
        Participant.is_active == True
    ).order_by(Participant.pagamento_data.desc()
    ).limit(10).all()
    
    ultimos_pagamentos = []
    for pagamento in ultimos_pagamentos_query:
        if pagamento.data:  # Verificar se a data não é None
            ultimos_pagamentos.append({
                'data': pagamento.data.isoformat() if pagamento.data else None,
                'jogador': pagamento.jogador,
                'jogo': pagamento.jogo,
                'valor': pagamento.valor,
                'metodo': pagamento.metodo,
                'status': pagamento.status
            })
    
    return jsonify({
        'total_arrecadado': total_arrecadado,
        'total_pendente': total_pendente,
        'valor_medio_jogo': valor_medio_jogo,
        'arrecadacao_mensal': arrecadacao_mensal,
        'status_pagamentos': status_pagamentos,
        'ultimos_pagamentos': ultimos_pagamentos
    }) 