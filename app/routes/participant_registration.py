"""
Rutas para registro público de participantes que desean votar.
Permite que usuarios se registren con email, nombre y contraseña.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import ParticipantUser, Participant
from app.services.email_service import EmailService
from app.services.audit_service import AuditService
from datetime import datetime
import re

participant_reg_bp = Blueprint('participant_registration', __name__)

# Expresión regular para validar email
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validar formato de email"""
    if not email or len(email) > 120:
        return False
    return bool(EMAIL_REGEX.match(email))

def validate_password(password):
    """
    Validar contraseña segura:
    - Mínimo 8 caracteres
    - Contiene letras mayúsculas
    - Contiene letras minúsculas
    - Contiene números
    """
    if not password or len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    return True, "OK"

def email_exists_globally(email):
    """
    Validar que el email NO existe en ninguna tabla de usuarios.
    Crítico para evitar duplicados entre participantes, admins, etc.
    """
    from app.models import AdminUser
    
    # Verificar en ParticipantUser
    if ParticipantUser.query.filter_by(email=email).first():
        return True
    
    # Verificar en AdminUser
    if AdminUser.query.filter_by(email=email).first():
        return True
    
    # Verificar en Participant (tabla sin autenticación)
    if Participant.query.filter_by(email=email).first():
        return True
    
    return False

@participant_reg_bp.route('/registro', methods=['GET'])
def registration_page():
    """Mostrar página de registro de participantes"""
    return render_template('participant_registration.html')

@participant_reg_bp.route('/api/participant-auth/register', methods=['POST'])
def register_participant():
    """
    API para registrar nuevo participante.
    
    Request JSON:
    {
        "email": "user@example.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "password": "SecurePass123",
        "password_confirm": "SecurePass123"
    }
    
    Response:
    {
        "message": "Registro exitoso",
        "access_token": "jwt_token",
        "user": { ...user_data... }
    }
    """
    data = request.get_json()
    
    # Validación de campos requeridos
    required_fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    email = data.get('email', '').strip().lower()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    password = data.get('password', '')
    password_confirm = data.get('password_confirm', '')
    
    # Validación de email
    if not validate_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    
    # Validación de nombre
    if not first_name or len(first_name) < 2:
        return jsonify({'error': 'Nombre debe tener al menos 2 caracteres'}), 400
    
    if not last_name or len(last_name) < 2:
        return jsonify({'error': 'Apellido debe tener al menos 2 caracteres'}), 400
    
    # Validación de contraseña
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return jsonify({'error': password_msg}), 400
    
    # Validación de confirmación de contraseña
    if password != password_confirm:
        return jsonify({'error': 'Las contraseñas no coinciden'}), 400
    
    # VALIDACIÓN CRÍTICA: Email no debe existir en ningún lado
    if email_exists_globally(email):
        return jsonify({'error': 'Este email ya está registrado'}), 409
    
    try:
        # Crear ParticipantUser (usuario autenticado)
        participant_user = ParticipantUser(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,  # Activado inmediatamente
            email_confirmed=False  # Pero email no confirmado
        )
        participant_user.set_password(password)
        
        # Generar token de confirmación (para email opcional)
        participant_user.generate_confirmation_token()
        
        db.session.add(participant_user)
        db.session.flush()  # Para obtener el ID
        
        # Crear entrada en tabla Participant (para compatibilidad con votación)
        participant = Participant(
            email=email,
            first_name=first_name,
            last_name=last_name,
            has_voted=False
        )
        db.session.add(participant)
        db.session.flush()  # IMPORTANTE: Obtener ID del Participant antes de asignarlo
        
        # Relacionar
        participant_user.participant_id = participant.id
        
        db.session.commit()
        
        # Log de auditoría
        AuditService.log_action(
            action='CREATE',
            entity_type='PARTICIPANT_USER',
            entity_id=participant_user.id,
            description=f"Participante {first_name} {last_name} registrado",
            ip_address=request.remote_addr
        )
        
        # Enviar email de confirmación (opcional)
        try:
            EmailService.send_confirmation_email(
                participant_user.email,
                participant_user.first_name,
                participant_user.confirmation_token
            )
        except Exception as e:
            current_app.logger.warning(f"No se pudo enviar email de confirmación: {str(e)}")
        
        # Crear JWT token para login automático
        access_token = create_access_token(identity=str(participant_user.id))
        
        return jsonify({
            'message': 'Registro exitoso. Login automático realizado.',
            'access_token': access_token,
            'user': {
                'id': participant_user.id,
                'email': participant_user.email,
                'first_name': participant_user.first_name,
                'last_name': participant_user.last_name,
                'full_name': f"{first_name} {last_name}",
                'email_confirmed': participant_user.email_confirmed
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error en registro de participante: {str(e)}")
        return jsonify({'error': 'Error al registrar participante'}), 500

@participant_reg_bp.route('/api/participant-auth/login', methods=['POST'])
def login_participant():
    """
    API para login de participantes registrados.
    
    Request JSON:
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }
    
    Response:
    {
        "access_token": "jwt_token",
        "user": { ...user_data... }
    }
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Buscar participante
    participant_user = ParticipantUser.query.filter_by(email=email).first()
    
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not participant_user.verify_password(password):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Log de auditoría
    AuditService.log_action(
        action='LOGIN',
        entity_type='PARTICIPANT_USER',
        entity_id=participant_user.id,
        ip_address=request.remote_addr
    )
    
    # Crear token JWT
    access_token = create_access_token(identity=str(participant_user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': participant_user.id,
            'email': participant_user.email,
            'first_name': participant_user.first_name,
            'last_name': participant_user.last_name,
            'full_name': f"{participant_user.first_name} {participant_user.last_name}",
            'email_confirmed': participant_user.email_confirmed,
            'participant_id': participant_user.participant_id
        }
    }), 200

@participant_reg_bp.route('/api/participant-auth/verify', methods=['GET'])
def verify_participant_email():
    """
    Verificar email del participante mediante token.
    URL: /api/participant-auth/verify?token=xxx
    """
    token = request.args.get('token', '')
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 400
    
    participant_user = ParticipantUser.query.filter_by(
        confirmation_token=token
    ).first()
    
    if not participant_user:
        return jsonify({'error': 'Token inválido'}), 404
    
    if not participant_user.verify_confirmation_token(token):
        return jsonify({'error': 'Token expirado'}), 410
    
    # Confirmar email
    participant_user.email_confirmed = True
    participant_user.confirmation_token = None
    participant_user.confirmation_token_expires = None
    db.session.commit()
    
    AuditService.log_action(
        action='EMAIL_VERIFIED',
        entity_type='PARTICIPANT_USER',
        entity_id=participant_user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Email confirmado exitosamente'
    }), 200

@participant_reg_bp.route('/api/participant-auth/check-email', methods=['POST'])
def check_email_availability():
    """
    Validar disponibilidad de email EN TIEMPO REAL (AJAX).
    Útil para validación en el formulario del frontend.
    
    Request JSON:
    {
        "email": "user@example.com"
    }
    
    Response:
    {
        "available": true/false,
        "message": "..."
    }
    """
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not validate_email(email):
        return jsonify({
            'available': False,
            'message': 'Email inválido'
        }), 400
    
    # Verificar globalme
    if email_exists_globally(email):
        return jsonify({
            'available': False,
            'message': 'Este email ya está registrado'
        }), 200
    
    return jsonify({
        'available': True,
        'message': 'Email disponible'
    }), 200
