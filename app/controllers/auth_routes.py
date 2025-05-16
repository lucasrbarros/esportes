from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User, Room, Participant
from app.models.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Se o usuário já está logado, redireciona para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Busca o usuário pelo nome de usuário
        user = User.query.filter_by(username=form.username.data).first()
        
        # Verifica se o usuário existe e a senha está correta
        if user and user.check_password(form.password.data):
            # Faz o login do usuário
            login_user(user, remember=form.remember_me.data)
            
            # Redireciona para a página que o usuário tentou acessar ou para a página inicial
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        
        # Mensagem de erro caso o login falhe
        flash('Nome de usuário ou senha incorretos', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    # Se o usuário já está logado, redireciona para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Cria um novo usuário
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            password=form.password.data
        )
        
        # Adiciona o usuário ao banco de dados
        db.session.add(new_user)
        db.session.commit()
        
        # Mensagem de sucesso
        flash('Registro realizado com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota para fazer logout"""
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/perfil')
@login_required
def profile():
    """Página de perfil do usuário"""
    # Obtém as salas criadas pelo usuário
    rooms_created = current_user.rooms_created
    
    # Obtém as participações do usuário
    participations = db.session.query(Participant, Room).join(Room).filter(
        Participant.user_id == current_user.id,
        Participant.is_active == True
    ).all()
    
    return render_template('auth/profile.html', 
                          rooms_created=rooms_created,
                          participations=participations) 