from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import AdminUser, AuditLog, ParticipantUser, Participant
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario administrador"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    admin = AdminUser.query.filter_by(email=data['email']).first()
    
    if not admin or not admin.is_active:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not admin.verify_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Registrar último login
    admin.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log de auditoría
    AuditService.log_action(
        action='LOGIN',
        entity_type='ADMIN',
        entity_id=admin.id,
        admin_id=admin.id,
        ip_address=request.remote_addr
    )
    
    # Crear token JWT
    access_token = create_access_token(identity=admin.id)
    
    return jsonify({
        'access_token': access_token,
        'user': admin.to_dict()
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar nuevo usuario administrador (solo si no existe ninguno)"""
    data = request.get_json()
    
    # Verificar si ya existen admins
    existing_admins = AdminUser.query.count()
    if existing_admins > 0 and not request.headers.get('X-Admin-Token'):
        return jsonify({'error': 'Registro no disponible'}), 403
    
    if not all(key in data for key in ['email', 'password', 'full_name']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    if AdminUser.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 409
    
    admin = AdminUser(
        email=data['email'],
        full_name=data['full_name'],
        is_active=True
    )
    admin.set_password(data['password'])
    
    db.session.add(admin)
    db.session.commit()
    
    AuditService.log_action(
        action='CREATE',
        entity_type='ADMIN',
        entity_id=admin.id,
        description=f"Admin {admin.full_name} registrado",
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Admin registrado exitosamente',
        'user': admin.to_dict()
    }), 201


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verificar token JWT válido"""
    admin_id = get_jwt_identity()
    admin = AdminUser.query.get(admin_id)
    
    if not admin or not admin.is_active:
        return jsonify({'error': 'Token inválido'}), 401
    
    return jsonify({'user': admin.to_dict()}), 200


# ============================================
# RUTAS PÚBLICAS DE REGISTRO DE PARTICIPANTES
# ============================================

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route('/participant/register', methods=['POST'])
def participant_register():
    """Registrar nuevo participante (público)"""
    data = request.get_json()
    
    # Validar campos requeridos
    if not all(key in data for key in ['email', 'password', 'first_name', 'last_name']):
        return jsonify({'error': 'Faltan campos requeridos: email, password, first_name, last_name'}), 400
    
    email = data['email'].strip().lower()
    
    # Validar formato de email
    if not validate_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    
    # Validar longitud de contraseña
    if len(data['password']) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
    
    # Validar que el email no esté registrado
    if ParticipantUser.query.filter_by(email=email).first():
        return jsonify({'error': 'Este email ya está registrado'}), 409
    
    # Validar que el email no esté en la lista de participantes
    if Participant.query.filter_by(email=email).first():
        return jsonify({'error': 'Este email ya existe en el sistema'}), 409
    
    try:
        # Crear usuario participante
        participant_user = ParticipantUser(
            email=email,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            is_active=False  # Requiere confirmación de email
        )
        participant_user.set_password(data['password'])
        
        # Generar token de confirmación
        confirmation_token = participant_user.generate_confirmation_token()
        
        db.session.add(participant_user)
        db.session.commit()
        
        # Enviar email de confirmación
        confirmation_url = url_for(
            'auth.confirm_participant_email',
            token=confirmation_token,
            _external=True
        )
        
        EmailService.send_confirmation_email(
            email=email,
            name=f"{data['first_name']} {data['last_name']}",
            confirmation_url=confirmation_url
        )
        
        return jsonify({
            'message': 'Registro exitoso. Por favor confirma tu email',
            'email': email,
            'user_id': participant_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error registrando participante: {str(e)}', exc_info=True)
        return jsonify({'error': 'Error al registrar participante'}), 500


@auth_bp.route('/participant/confirm/<token>', methods=['GET'])
def confirm_participant_email(token):
    """Confirmar email de participante"""
    # Buscar usuario con ese token
    participant_user = ParticipantUser.query.filter_by(confirmation_token=token).first()
    
    if not participant_user:
        return jsonify({'error': 'Token de confirmación inválido'}), 400
    
    # Verificar que el token sea válido
    if not participant_user.verify_confirmation_token(token):
        return jsonify({'error': 'Token expirado o inválido'}), 400
    
    try:
        # Marcar email como confirmado
        participant_user.email_confirmed = True
        participant_user.is_active = True
        participant_user.confirmation_token = None
        participant_user.confirmation_token_expires = None
        
        # Crear registro de participante si no existe
        if not participant_user.participant:
            participant = Participant(
                email=participant_user.email,
                first_name=participant_user.first_name,
                last_name=participant_user.last_name
            )
            db.session.add(participant)
            db.session.flush()  # Para obtener el ID
            participant_user.participant_id = participant.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Email confirmado exitosamente. Ya puedes ingresar.',
            'email': participant_user.email
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error confirmando email: {str(e)}', exc_info=True)
        return jsonify({'error': 'Error al confirmar email'}), 500


@auth_bp.route('/participant/login', methods=['POST'])
def participant_login():
    """Autenticar participante registrado"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    email = data['email'].strip().lower()
    participant_user = ParticipantUser.query.filter_by(email=email).first()
    
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not participant_user.verify_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Crear token JWT
    access_token = create_access_token(identity=participant_user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': participant_user.to_dict(),
        'type': 'participant'
    }), 200


@auth_bp.route('/participant/verify', methods=['GET'])
@jwt_required()
def verify_participant_token():
    """Verificar token JWT de participante"""
    user_id = get_jwt_identity()
    participant_user = ParticipantUser.query.get(user_id)
    
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Token inválido'}), 401
    
    return jsonify({
        'user': participant_user.to_dict(),
        'type': 'participant'
    }), 200

