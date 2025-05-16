import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializa as extensões
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave_secreta_padrao')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///esportes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa o banco de dados com a aplicação
    db.init_app(app)
    login_manager.init_app(app)
    
    # Importa e registra os blueprints
    from app.controllers.main_routes import main_bp
    from app.controllers.room_routes import room_bp
    from app.controllers.auth_routes import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(auth_bp)
    
    # Carrega o usuário a partir do ID na sessão
    from app.models.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Cria as tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app 