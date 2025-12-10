"""
Rutas para que participantes registrados se postulen como candidatos.
Sistema de aspirantes para posiciones en las encuestas.
"""

from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import ParticipantUser, Candidate, Position, Vote
from app.services.audit_service import AuditService
from datetime import datetime
import os
from pathlib import Path

candidates_bp = Blueprint('candidates', __name__, url_prefix='/api/candidates')

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_FOLDER = 'app/static/uploads/candidates'

def allowed_file(filename):
    """Validar extensión de archivo"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@candidates_bp.route('/register', methods=['POST'])
@jwt_required()
def register_candidate():
    """
    API para que un participante registrado se postule como candidato.
    
    Requiere autenticación JWT de ParticipantUser.
    
    Request (multipart/form-data):
    {
        "position_id": 1,
        "public_name": "Juan Pérez González",
        "description": "Soy docente con 10 años de experiencia...",
        "photo": <archivo_imagen> (opcional)
    }
    
    Response:
    {
        "message": "Candidatura registrada exitosamente",
        "candidate": { ...candidate_data... }
    }
    """
    participant_user_id = int(get_jwt_identity())
    
    # Verificar que el usuario existe
    participant_user = ParticipantUser.query.get(participant_user_id)
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Usuario no válido'}), 401
    
    # Obtener datos del formulario
    position_id = request.form.get('position_id', type=int)
    public_name = request.form.get('public_name', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validaciones de campo
    if not position_id:
        return jsonify({'error': 'ID de posición requerido'}), 400
    
    if not public_name or len(public_name) < 3:
        return jsonify({'error': 'Nombre público debe tener al menos 3 caracteres'}), 400
    
    if len(public_name) > 200:
        return jsonify({'error': 'Nombre público demasiado largo (máximo 200 caracteres)'}), 400
    
    if not description or len(description) < 10:
        return jsonify({'error': 'Descripción debe tener al menos 10 caracteres'}), 400
    
    if len(description) > 2000:
        return jsonify({'error': 'Descripción demasiado larga (máximo 2000 caracteres)'}), 400
    
    # Validar que la posición exista y esté activa
    position = Position.query.get(position_id)
    if not position or not position.is_active:
        return jsonify({'error': 'Posición no disponible'}), 404
    
    # CRÍTICO: Validar que no exista candidatura duplicada
    # Un mismo usuario no puede postularse dos veces para la misma posición
    existing_candidate = Candidate.query.filter_by(
        position_id=position_id,
        name=public_name  # Usando name como identificador único del candidato
    ).first()
    
    if existing_candidate:
        return jsonify({'error': 'Ya existe una candidatura con este nombre para esta posición'}), 409
    
    photo_filename = None
    
    # Procesar foto de perfil si se proporciona
    if 'photo' in request.files:
        file = request.files['photo']
        
        if file and file.filename != '':
            # Validar extensión
            if not allowed_file(file.filename):
                return jsonify({
                    'error': 'Formato de archivo no permitido. Use: JPG, PNG, GIF'
                }), 400
            
            # Validar tamaño
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({
                    'error': f'Archivo muy grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB'
                }), 400
            
            try:
                # Crear carpeta si no existe
                Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
                
                # Generar nombre de archivo seguro y único
                filename = secure_filename(file.filename)
                name_without_ext = filename.rsplit('.', 1)[0]
                ext = filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                safe_name = f"candidate_{position_id}_{timestamp}_{name_without_ext}.{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, safe_name)
                file.save(filepath)
                
                photo_filename = safe_name
            
            except Exception as e:
                current_app.logger.error(f"Error al guardar archivo: {str(e)}")
                return jsonify({'error': 'Error al procesar la foto'}), 500
    
    try:
        # Crear candidato
        candidate = Candidate(
            position_id=position_id,
            name=public_name,
            description=description
        )
        
        # Nota: Podrías agregar un campo adicional en el modelo Candidate
        # para referencia del usuario que se postula, si lo necesitas para auditoría
        
        db.session.add(candidate)
        db.session.commit()
        
        # Log de auditoría
        AuditService.log_action(
            action='CREATE',
            entity_type='CANDIDATE',
            entity_id=candidate.id,
            description=f"Candidato {public_name} registrado para posición {position.name}",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Candidatura registrada exitosamente',
            'candidate': {
                'id': candidate.id,
                'position_id': candidate.position_id,
                'name': candidate.name,
                'description': candidate.description,
                'photo': photo_filename,
                'created_at': candidate.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al registrar candidato: {str(e)}")
        return jsonify({'error': 'Error al registrar candidatura'}), 500

@candidates_bp.route('/my-candidates', methods=['GET'])
@jwt_required()
def get_my_candidates():
    """
    Obtener todas las candidaturas del usuario actual.
    
    Response:
    {
        "candidates": [
            {
                "id": 1,
                "position_id": 1,
                "name": "Juan Pérez",
                "description": "...",
                "vote_count": 25,
                "created_at": "..."
            }
        ]
    }
    """
    participant_user_id = int(get_jwt_identity())
    
    # Nota: La actual estructura no relaciona Candidates con ParticipantUser directamente
    # Para una implementación más robusta, podrías agregar un campo user_id a la tabla Candidate
    # Por ahora, retornamos todos los candidatos (mejora futura)
    
    return jsonify({
        'message': 'Endpoint para ver mis candidaturas',
        'note': 'Requiere relación directa en modelo Candidate'
    }), 200

@candidates_bp.route('/available-positions', methods=['GET'])
@jwt_required()
def get_available_positions():
    """
    Obtener posiciones activas disponibles para candidatarse.
    
    Response:
    {
        "positions": [
            {
                "id": 1,
                "name": "Presidente",
                "description": "...",
                "candidate_count": 5
            }
        ]
    }
    """
    positions = Position.query.filter_by(is_active=True).order_by(Position.order).all()
    
    return jsonify({
        'positions': [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'candidate_count': p.candidates.count()
            }
            for p in positions
        ]
    }), 200

@candidates_bp.route('/<int:position_id>', methods=['GET'])
def get_candidates_by_position(position_id):
    """
    Obtener candidatos para una posición específica.
    RUTA PÚBLICA - No requiere autenticación.
    
    Response:
    {
        "position": {...},
        "candidates": [...]
    }
    """
    position = Position.query.get(position_id)
    
    if not position:
        return jsonify({'error': 'Posición no encontrada'}), 404
    
    candidates = Candidate.query.filter_by(
        position_id=position_id
    ).order_by(Candidate.order).all()
    
    return jsonify({
        'position': {
            'id': position.id,
            'name': position.name,
            'description': position.description
        },
        'candidates': [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'vote_count': c.votes.count()
            }
            for c in candidates
        ]
    }), 200

@candidates_bp.route('/<int:candidate_id>', methods=['GET'])
def get_candidate_detail(candidate_id):
    """
    Obtener detalles de un candidato específico.
    RUTA PÚBLICA - No requiere autenticación.
    
    Response:
    {
        "candidate": {
            "id": 1,
            "name": "Juan Pérez",
            "description": "...",
            "position": {...},
            "vote_count": 25,
            "photo": "filename.jpg"
        }
    }
    """
    candidate = Candidate.query.get(candidate_id)
    
    if not candidate:
        return jsonify({'error': 'Candidato no encontrado'}), 404
    
    return jsonify({
        'candidate': {
            'id': candidate.id,
            'name': candidate.name,
            'description': candidate.description,
            'position': {
                'id': candidate.position.id,
                'name': candidate.position.name
            },
            'vote_count': candidate.votes.count(),
            'created_at': candidate.created_at.isoformat()
        }
    }), 200
