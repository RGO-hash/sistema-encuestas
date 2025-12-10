from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import config
import os
from app.extensions import db, jwt, mail, setup_logging
from app.routes.auth import auth_bp
from app.routes.participants import participants_bp
from app.routes.survey import survey_bp
from app.routes.voting import voting_bp
from app.routes.participant_registration import participant_reg_bp
from app.routes.candidates import candidates_bp
from app.routes.public_results import results_bp
from app.routes.voting_participant import voting_participant_bp
from flask_jwt_extended import exceptions as jwt_exceptions
from werkzeug.exceptions import HTTPException

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Manejadores de errores JWT - Usando decoradores de excepciones
    try:
        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            app.logger.warning(f'Invalid token: {error}')
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        @jwt.unauthorized_loader
        def missing_token_callback(error):
            app.logger.warning(f'Missing token: {error}')
            return jsonify({'error': 'Token de autorización no proporcionado'}), 401
        
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_data):
            app.logger.warning('Token expirado')
            return jsonify({'error': 'Token expirado'}), 401
    except Exception as e:
        app.logger.warning(f'Error configurando JWT callbacks: {e}')
    
    # Manejadores de excepciones HTTP
    @app.errorhandler(jwt_exceptions.NoAuthorizationError)
    def handle_auth_error(e):
        app.logger.warning(f'NoAuthorizationError: {str(e)}')
        return jsonify({'error': 'Token de autorización no proporcionado'}), 401
    
    @app.errorhandler(jwt_exceptions.InvalidHeaderError)
    def handle_invalid_header_error(e):
        app.logger.warning(f'InvalidHeaderError: {str(e)}')
        return jsonify({'error': 'Formato de header inválido'}), 401
    
    @app.errorhandler(jwt_exceptions.JWTDecodeError)
    def handle_jwt_decode_error(e):
        app.logger.warning(f'JWTDecodeError: {str(e)}')
        return jsonify({'error': 'Token inválido o expirado'}), 401
    
    @app.errorhandler(jwt_exceptions.WrongTokenError)
    def handle_wrong_token_error(e):
        app.logger.warning(f'WrongTokenError: {str(e)}')
        return jsonify({'error': 'Token inválido'}), 401
    
    @app.errorhandler(jwt_exceptions.JWTExtendedException)
    def handle_jwt_error(e):
        app.logger.warning(f'JWTExtendedException: {str(e)}')
        return jsonify({'error': 'Error de autenticación JWT'}), 401
    
    # Configurar logging
    setup_logging(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(voting_bp)
    app.register_blueprint(participant_reg_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(voting_participant_bp)
    
    # Rutas públicas
    @app.route('/')
    def index():
        """Página principal - Panel de admin"""
        return render_template('index.html', is_survey_page=False)
    
    @app.route('/survey')
    def survey_page():
        """Página de encuesta pública"""
        return render_template('survey.html', is_survey_page=True)
    
    @app.route('/results')
    def results_page():
        """Página de resultados públicos"""
        return render_template('public_results.html', is_survey_page=False)
    
    @app.route('/resultados')
    def results_spanish():
        """Página de resultados públicos (en español)"""
        return render_template('public_results.html', is_survey_page=False)
    
    @app.route('/registro')
    def registration_page():
        """Página de registro de participantes"""
        return render_template('participant_registration.html', is_survey_page=False)
    
    @app.route('/login-participante')
    @app.route('/participant-login')
    def participant_login_page():
        """Página de login de participantes"""
        return render_template('participant_login.html', is_survey_page=False)
    
    @app.route('/votar')
    @app.route('/vote')
    def voting_page():
        """Página de votación (requiere autenticación)"""
        return render_template('participant_voting.html', is_survey_page=False)
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(error)}', exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'No autorizado'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Acceso prohibido'}), 403
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'error': 'Datos inválidos o incompletos'}), 422
    
    # Manejar errores de JSON inválido
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Solicitud inválida'}), 400
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
        
        # Crear admin por defecto si no existe
        from app.models import AdminUser
        if AdminUser.query.count() == 0:
            admin = AdminUser(
                email='admin@encuestas.com',
                full_name='Administrador',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Admin por defecto creado: admin@encuestas.com / admin123')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
