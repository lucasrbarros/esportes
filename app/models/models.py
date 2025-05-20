from datetime import datetime, timedelta
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


class Court(db.Model):
    """Modelo para representar as quadras físicas disponíveis"""
    __tablename__ = 'courts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True, default='')
    description = db.Column(db.Text, nullable=True, default='')
    sport_type = db.Column(db.String(50), nullable=False)  # Tipo de esporte (futebol, vôlei, etc.)
    type = db.Column(db.String(50), nullable=False, default='default')  # Tipo de quadra (campo necessário na tabela)
    city = db.Column(db.String(100), nullable=False, default='Cidade')  # Cidade da quadra
    valor_hora = db.Column(db.Float, nullable=False, default=0.0)  # Preço por hora (campo legado)
    hourly_price = db.Column(db.Float, nullable=False, default=0.0)  # Preço por hora (campo atualizado)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    capacity = db.Column(db.Integer, nullable=False, default=10)  # Capacidade máxima de jogadores
    
    # Relacionamento com reservas
    reservations = db.relationship('Room', backref='court', lazy=True)
    
    def __init__(self, name=None, sport_type=None, hourly_price=0.0, location=None, description=None, capacity=10, is_active=True, city=None):
        self.name = name or ''
        self.sport_type = sport_type or 'Outros'
        self.type = sport_type or 'Outros'  # Usar sport_type como valor padrão para type também
        self.hourly_price = float(hourly_price or 0.0)
        self.valor_hora = float(hourly_price or 0.0)  # Manter os dois campos sincronizados
        self.location = location or ''
        self.description = description or ''
        self.capacity = int(capacity or 10)
        self.is_active = is_active if is_active is not None else True
        self.created_at = datetime.utcnow()
        self.city = city or 'Cidade'
        
    def __repr__(self):
        return f"<Court id={self.id}, name={self.name}, sport={self.sport_type}, price={self.hourly_price}>"
    
    def is_available(self, start_time, end_time):
        """Verifica se a quadra está disponível no período especificado"""
        # Verificar se há alguma reserva que se sobreponha ao período solicitado
        overlapping_reservations = Room.query.filter(
            Room.court_id == self.id,
            Room.is_active == True,
            Room.date < end_time,
            Room.end_time > start_time
        ).count()
        
        return overlapping_reservations == 0
    
    def get_reservations_for_day(self, date):
        """Retorna todas as reservas para uma data específica"""
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())
        
        return Room.query.filter(
            Room.court_id == self.id,
            Room.is_active == True,
            Room.date >= start_of_day,
            Room.date <= end_of_day
        ).all()


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
    city = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)  # Valor por participante
    
    # Campos para integração com o sistema de quadras
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)
    duration_hours = db.Column(db.Float, nullable=False, default=1.0)  # Duração em horas
    end_time = db.Column(db.DateTime, nullable=True)  # Horário de término calculado
    
    # Relacionamento com os participantes
    participants = db.relationship('Participant', backref='room', lazy=True)
    
    def __init__(self, name, sport, date, max_participants, creator_id, description=None, is_private=False, location=None, city=None, valor=0.0, court_id=None, duration_hours=1.0):
        self.name = name
        self.sport = sport
        self.date = date
        self.max_participants = max_participants
        self.description = description
        self.creator_id = creator_id
        self.is_private = is_private
        self.location = location
        self.city = city or "Não informada"
        self.valor = valor
        self.link_code = secrets.token_urlsafe(6)  # Gera um código único para o link
        
        # Configuração da quadra e duração
        self.court_id = court_id
        self.duration_hours = duration_hours
        if date:
            self.end_time = date + timedelta(hours=duration_hours)
    
    def is_full(self):
        """Verifica se a sala está cheia"""
        return len(self.get_active_participants()) >= self.max_participants
    
    def get_active_participants(self):
        """Retorna apenas os participantes ativos, ordenados por data de registro"""
        # Obter todos os participantes ativos
        active_participants = [p for p in self.participants if p.is_active]
        
        # Ordenar por data de registro (os mais antigos primeiro)
        active_participants.sort(key=lambda p: p.registered_at)
        
        # Debug
        print(f"Sala {self.name} (ID: {self.id}) - Participantes ativos: {len(active_participants)}")
        for i, p in enumerate(active_participants):
            status = "Confirmado" if i < self.max_participants else "Lista de espera"
            print(f"  {i+1}. {p.user.name} - Registrado em: {p.registered_at} - Status: {status}")
        
        return active_participants
    
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
    
    def calculate_total_price(self):
        """Calcula o preço total da reserva com base na quadra e duração"""
        if not self.court_id:
            return self.valor * len(self.get_confirmed_participants())
        
        return self.court.hourly_price * self.duration_hours
    
    def calculate_price_per_person(self):
        """Calcula o valor por pessoa com base no preço total e número de participantes"""
        total_price = self.calculate_total_price()
        participants_count = len(self.get_confirmed_participants())
        
        if participants_count == 0:
            return 0.0
            
        return total_price / participants_count


class Participant(db.Model):
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    checked_in = db.Column(db.Boolean, default=False)
    pagamento_status = db.Column(db.String(20), default='pendente')  # pendente, pago, cancelado
    pagamento_data = db.Column(db.DateTime, nullable=True)
    pagamento_metodo = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    def __init__(self, user_id, room_id):
        self.user_id = user_id
        self.room_id = room_id
        
    def is_in_waiting_list(self):
        """Verifica se o participante está na lista de espera"""
        if not self.is_active:
            return False
        
        room = self.room
        active_participants = room.get_active_participants()
        try:
            # Encontrar o índice do participante na lista de participantes ativos
            participant_index = active_participants.index(self)
            # Verificar se está após o limite de participantes máximos
            is_waiting = participant_index >= room.max_participants
            
            # Debug
            print(f"Participante {self.user.name} (ID: {self.id}) - Posição: {participant_index+1}/{len(active_participants)} - Máximo: {room.max_participants} - Lista de espera: {is_waiting}")
            
            return is_waiting
        except ValueError:
            # Se o participante não estiver na lista de participantes ativos
            print(f"Participante {self.user.name} (ID: {self.id}) não está na lista de participantes ativos")
            return False 