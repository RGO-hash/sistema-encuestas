from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import AdminUser, AuditLog
from app.services.audit_service import AuditService
from datetime import datetime

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
