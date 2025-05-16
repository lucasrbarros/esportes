from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    rooms_created = db.relationship('Room', backref='creator', lazy=True, foreign_keys='Room.creator_id')
    participations = db.relationship('Participant', backref='user', lazy=True)
    
    def __init__(self, username, email, name, password):
        self.username = username
        self.email = email
        self.name = name
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_participating(self, room_id):
        """Verifica se o usuário está participando de uma sala"""
        return any(p.room_id == room_id and p.is_active for p in self.participations)
    
    def get_participation(self, room_id):
        """Retorna a participação do usuário em uma sala específica"""
        for p in self.participations:
            if p.room_id == room_id and p.is_active:
                return p
        return None


class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    link_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200), nullable=True)
    
    # Relacionamento com os participantes
    participants = db.relationship('Participant', backref='room', lazy=True)
    
    def __init__(self, name, sport, date, max_participants, creator_id, description=None, is_private=False, location=None):
        self.name = name
        self.sport = sport
        self.date = date
        self.max_participants = max_participants
        self.description = description
        self.creator_id = creator_id
        self.is_private = is_private
        self.location = location
        self.link_code = secrets.token_urlsafe(6)  # Gera um código único para o link
    
    def is_full(self):
        """Verifica se a sala está cheia"""
        return len(self.get_active_participants()) >= self.max_participants
    
    def get_active_participants(self):
        """Retorna apenas os participantes ativos"""
        return [p for p in self.participants if p.is_active]
    
    def get_waiting_list(self):
        """Retorna a lista de espera"""
        active_participants = self.get_active_participants()
        if len(active_participants) <= self.max_participants:
            return []
        return active_participants[self.max_participants:]
    
    def get_confirmed_participants(self):
        """Retorna os participantes confirmados"""
        active_participants = self.get_active_participants()
        return active_participants[:min(len(active_participants), self.max_participants)]


class Participant(db.Model):
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    checked_in = db.Column(db.Boolean, default=False)
    
    def __init__(self, user_id, room_id):
        self.user_id = user_id
        self.room_id = room_id 