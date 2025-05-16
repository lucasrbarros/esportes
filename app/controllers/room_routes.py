from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.models import Room, Participant
from app.models.forms import CreateRoomForm, EditRoomForm

room_bp = Blueprint('room', __name__, url_prefix='/sala')

@room_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def create_room():
    """Criar uma nova sala"""
    form = CreateRoomForm()
    
    if form.validate_on_submit():
        # Criar a sala com os dados do formulário
        new_room = Room(
            name=form.name.data,
            sport=form.sport.data,
            date=form.date.data,
            max_participants=form.max_participants.data,
            description=form.description.data,
            creator_id=current_user.id,
            is_private=form.is_private.data,
            location=form.location.data
        )
        
        # Salvar no banco de dados
        db.session.add(new_room)
        db.session.commit()
        
        # Adicionar o organizador como participante
        organizer_participant = Participant(
            user_id=current_user.id,
            room_id=new_room.id
        )
        db.session.add(organizer_participant)
        db.session.commit()
        
        flash('Sala criada com sucesso!', 'success')
        return redirect(url_for('room.manage_room', link_code=new_room.link_code))
    
    return render_template('create_room.html', form=form)

@room_bp.route('/<link_code>')
def view_room(link_code):
    """Visualizar uma sala específica"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário está participando
    is_participating = False
    if current_user.is_authenticated:
        is_participating = current_user.is_participating(room.id)
    
    # Verificar se o usuário é o organizador
    is_owner = current_user.is_authenticated and room.creator_id == current_user.id
    
    # Verificar permissão para acessar sala privada
    if room.is_private and not is_owner and not is_participating:
        if not current_user.is_authenticated:
            flash('Esta é uma sala privada. Faça login para acessá-la.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        else:
            flash('Esta é uma sala privada. Apenas o organizador e os participantes podem acessá-la.', 'warning')
            return redirect(url_for('main.index'))
    
    return render_template('view_room.html', 
                          room=room, 
                          is_owner=is_owner,
                          is_participating=is_participating)

@room_bp.route('/<link_code>/participar')
@login_required
def join_room(link_code):
    """Participar de uma sala (inscrição rápida)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador e já está participando
    if room.creator_id == current_user.id:
        participation = current_user.get_participation(room.id)
        if participation and participation.is_active:
            flash('Você já está inscrito nesta sala como organizador!', 'info')
        else:
            # Adicionar o organizador como participante (caso tenha sido removido por algum motivo)
            new_participant = Participant(
                user_id=current_user.id,
                room_id=room.id
            )
            db.session.add(new_participant)
            db.session.commit()
            flash('Você foi adicionado como organizador da sala!', 'success')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Verificar se o usuário já está participando
    if current_user.is_participating(room.id):
        flash('Você já está inscrito nesta sala!', 'info')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Criar novo participante
    new_participant = Participant(
        user_id=current_user.id,
        room_id=room.id
    )
    
    db.session.add(new_participant)
    db.session.commit()
    
    if room.is_full():
        flash('Você foi adicionado à lista de espera!', 'info')
    else:
        flash('Você foi adicionado à lista de participantes!', 'success')
        
    return redirect(url_for('room.view_room', link_code=link_code))

@room_bp.route('/<link_code>/sair')
@login_required
def leave_room(link_code):
    """Sair de uma sala"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id == current_user.id:
        flash('Como organizador, você não pode sair da sala.', 'warning')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Verificar se o usuário está participando
    participation = current_user.get_participation(room.id)
    
    if not participation:
        flash('Você não está inscrito nesta sala!', 'warning')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Desativar a participação (não excluir)
    participation.is_active = False
    db.session.commit()
    
    flash('Você saiu da sala com sucesso', 'success')
    return redirect(url_for('room.view_room', link_code=link_code))

@room_bp.route('/<link_code>/gerenciar')
@login_required
def manage_room(link_code):
    """Gerenciar uma sala (apenas para o organizador)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id != current_user.id:
        flash('Você não tem permissão para gerenciar esta sala', 'danger')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    return render_template('manage_room.html', room=room)

@room_bp.route('/<link_code>/remover/<int:participant_id>')
@login_required
def remove_participant(link_code, participant_id):
    """Remover um participante (apenas para o organizador)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id != current_user.id:
        flash('Você não tem permissão para gerenciar esta sala', 'danger')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    participant = Participant.query.get_or_404(participant_id)
    
    # Verificar se o participante pertence a esta sala
    if participant.room_id != room.id:
        abort(404)
    
    # Verificar se o participante é o organizador
    if participant.user_id == room.creator_id:
        flash('O organizador não pode ser removido da sala', 'warning')
        return redirect(url_for('room.manage_room', link_code=link_code))
    
    # Desativar o participante (não excluir)
    participant.is_active = False
    db.session.commit()
    
    flash('Participante removido com sucesso', 'success')
    return redirect(url_for('room.manage_room', link_code=link_code))

@room_bp.route('/<link_code>/encerrar')
@login_required
def close_room(link_code):
    """Encerrar uma sala (apenas para o organizador)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id != current_user.id:
        flash('Você não tem permissão para gerenciar esta sala', 'danger')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    room.is_active = False
    db.session.commit()
    
    flash('Sala encerrada com sucesso', 'success')
    return redirect(url_for('main.index'))

@room_bp.route('/<link_code>/excluir')
@login_required
def delete_room(link_code):
    """Excluir uma sala (apenas para o organizador)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id != current_user.id:
        flash('Você não tem permissão para excluir esta sala', 'danger')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Obter o nome da sala para mensagem de confirmação
    room_name = room.name
    
    # Excluir todas as participações relacionadas à sala
    Participant.query.filter_by(room_id=room.id).delete()
    
    # Excluir a sala
    db.session.delete(room)
    db.session.commit()
    
    flash(f'A sala "{room_name}" foi excluída permanentemente', 'success')
    return redirect(url_for('main.index'))

@room_bp.route('/<link_code>/editar', methods=['GET', 'POST'])
@login_required
def edit_room(link_code):
    """Editar uma sala (apenas para o organizador)"""
    room = Room.query.filter_by(link_code=link_code).first_or_404()
    
    # Verificar se o usuário é o organizador
    if room.creator_id != current_user.id:
        flash('Você não tem permissão para editar esta sala', 'danger')
        return redirect(url_for('room.view_room', link_code=link_code))
    
    # Criar o formulário preenchido com os dados atuais da sala
    form = EditRoomForm(obj=room)
    
    if form.validate_on_submit():
        # Atualizar os dados da sala
        form.populate_obj(room)
        db.session.commit()
        
        flash('Sala atualizada com sucesso!', 'success')
        return redirect(url_for('room.manage_room', link_code=room.link_code))
    
    return render_template('edit_room.html', form=form, room=room) 