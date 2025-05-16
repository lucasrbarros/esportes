from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, TextAreaField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, NumberRange, Optional, Length, EqualTo, ValidationError
from app.models.models import User

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('password', message='As senhas devem ser iguais')
    ])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, use outro ou faça login.')

class CreateRoomForm(FlaskForm):
    name = StringField('Nome da Sala', validators=[DataRequired(), Length(min=3, max=100)])
    sport = StringField('Esporte', validators=[DataRequired(), Length(min=2, max=50)])
    date = DateTimeField('Data e Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    max_participants = IntegerField('Número Máximo de Participantes', validators=[
        DataRequired(),
        NumberRange(min=2, message='A sala deve ter pelo menos 2 participantes')
    ])
    city = StringField('Cidade', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Local', validators=[Optional(), Length(max=200)])
    description = TextAreaField('Descrição (opcional)', validators=[Optional(), Length(max=500)])
    is_private = BooleanField('Sala Privada')
    submit = SubmitField('Criar Sala')

class JoinRoomForm(FlaskForm):
    name = StringField('Seu Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email (opcional)', validators=[Optional(), Email()])
    submit = SubmitField('Participar')

class SearchRoomForm(FlaskForm):
    sport = StringField('Filtrar por Esporte', validators=[Optional()])
    city = StringField('Filtrar por Cidade', validators=[Optional()])
    submit = SubmitField('Buscar')

class EditRoomForm(FlaskForm):
    name = StringField('Nome da Sala', validators=[DataRequired(), Length(min=3, max=100)])
    sport = StringField('Esporte', validators=[DataRequired(), Length(min=2, max=50)])
    date = DateTimeField('Data e Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    max_participants = IntegerField('Número Máximo de Participantes', validators=[
        DataRequired(),
        NumberRange(min=2, message='A sala deve ter pelo menos 2 participantes')
    ])
    city = StringField('Cidade', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Local', validators=[Optional(), Length(max=200)])
    description = TextAreaField('Descrição (opcional)', validators=[Optional(), Length(max=500)])
    is_private = BooleanField('Sala Privada')
    submit = SubmitField('Salvar Alterações') 