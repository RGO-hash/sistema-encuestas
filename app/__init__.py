from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import config
import os
from app.extensions import db, jwt, mail, setup_logging
from app.routes.auth import auth_bp
from app.routes.participants import participants_bp
from app.routes.survey import survey_bp
from app.routes.voting import voting_bp

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
    
    # Configurar logging
    setup_logging(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(voting_bp)
    
    # Rutas públicas
    @app.route('/')
    def index():
        """Página principal - Panel de admin"""
        return render_template('index.html')
    
    @app.route('/survey')
    def survey_page():
        """Página de encuesta pública"""
        return render_template('survey.html')
    
    @app.route('/results')
    def results_page():
        """Página de resultados"""
        return render_template('results.html')
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
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
