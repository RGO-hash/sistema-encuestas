from flask import Blueprint, render_template, request, jsonify, current_app
from app.extensions import db
from app.models import Participant, Position, Candidate, Vote
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
from datetime import datetime

participants_bp = Blueprint('participants', __name__, url_prefix='/api/participants')

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@participants_bp.route('', methods=['GET'])
@jwt_required()
def get_participants():
    """Obtener lista de participantes (admin)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Participant.query
    
    if search:
        query = query.filter(
            db.or_(
                Participant.email.ilike(f'%{search}%'),
                Participant.first_name.ilike(f'%{search}%'),
                Participant.last_name.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'participants': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@participants_bp.route('', methods=['POST'])
@jwt_required()
def create_participant():
    """Crear nuevo participante"""
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': f'Datos JSON inválidos: {str(e)}'}), 400
    
    # Validar que data no es None
    if data is None:
        return jsonify({'error': 'Datos JSON inválidos', 'content_type': request.content_type}), 400
    
    # Validar campos requeridos
    required_fields = ['email', 'first_name', 'last_name']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Faltan campos requeridos: {", ".join(missing_fields)}'}), 400
    
    # Validar email
    if not validate_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400
    
    # Verificar si el email ya existe
    if Participant.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 409
    
    participant = Participant(
        email=data['email'],
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        field1=data.get('field1', '').strip(),
        field2=data.get('field2', '').strip(),
        field3=data.get('field3', '').strip()
    )
    
    db.session.add(participant)
    db.session.commit()
    
    # Log de auditoría
    admin_id = int(get_jwt_identity())
    AuditService.log_action(
        action='CREATE',
        entity_type='PARTICIPANT',
        entity_id=participant.id,
        description=f"Participante {participant.email} creado",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Participante creado exitosamente',
        'participant': participant.to_dict()
    }), 201


@participants_bp.route('/<int:participant_id>', methods=['GET'])
@jwt_required()
def get_participant(participant_id):
    """Obtener detalles de un participante"""
    participant = Participant.query.get(participant_id)
    
    if not participant:
        return jsonify({'error': 'Participante no encontrado'}), 404
    
    return jsonify(participant.to_dict()), 200


@participants_bp.route('/<int:participant_id>', methods=['PUT'])
@jwt_required()
def update_participant(participant_id):
    """Actualizar datos de participante"""
    participant = Participant.query.get(participant_id)
    
    if not participant:
        return jsonify({'error': 'Participante no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos permitidos
    if 'first_name' in data:
        participant.first_name = data['first_name'].strip()
    if 'last_name' in data:
        participant.last_name = data['last_name'].strip()
    if 'field1' in data:
        participant.field1 = data['field1'].strip()
    if 'field2' in data:
        participant.field2 = data['field2'].strip()
    if 'field3' in data:
        participant.field3 = data['field3'].strip()
    
    participant.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log de auditoría
    admin_id = int(get_jwt_identity())
    AuditService.log_action(
        action='UPDATE',
        entity_type='PARTICIPANT',
        entity_id=participant_id,
        description=f"Participante {participant.email} actualizado",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Participante actualizado exitosamente',
        'participant': participant.to_dict()
    }), 200


@participants_bp.route('/<int:participant_id>', methods=['DELETE'])
@jwt_required()
def delete_participant(participant_id):
    """Eliminar participante"""
    participant = Participant.query.get(participant_id)
    
    if not participant:
        return jsonify({'error': 'Participante no encontrado'}), 404
    
    email = participant.email
    db.session.delete(participant)
    db.session.commit()
    
    # Log de auditoría
    admin_id = int(get_jwt_identity())
    AuditService.log_action(
        action='DELETE',
        entity_type='PARTICIPANT',
        entity_id=participant_id,
        description=f"Participante {email} eliminado",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({'message': 'Participante eliminado exitosamente'}), 200


@participants_bp.route('/bulk-upload', methods=['POST'])
@jwt_required()
def bulk_upload_participants():
    """Cargar múltiples participantes desde CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó archivo'}), 400
    
    file = request.files['file']
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Solo se aceptan archivos CSV'}), 400
    
    import csv
    from io import StringIO
    
    try:
        stream = StringIO(file.stream.read().decode('UTF8'), newline=None)
        csv_data = csv.DictReader(stream)
        
        created = 0
        errors = []
        
        for row_num, row in enumerate(csv_data, start=2):
            try:
                email = row.get('email', '').strip()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                if not email or not first_name or not last_name:
                    errors.append(f"Fila {row_num}: Faltan campos requeridos")
                    continue
                
                if not validate_email(email):
                    errors.append(f"Fila {row_num}: Email inválido")
                    continue
                
                if Participant.query.filter_by(email=email).first():
                    errors.append(f"Fila {row_num}: Email ya registrado")
                    continue
                
                participant = Participant(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    field1=row.get('field1', '').strip(),
                    field2=row.get('field2', '').strip(),
                    field3=row.get('field3', '').strip()
                )
                
                db.session.add(participant)
                created += 1
                
            except Exception as e:
                errors.append(f"Fila {row_num}: {str(e)}")
        
        db.session.commit()
        
        # Log de auditoría
        admin_id = int(get_jwt_identity())
        AuditService.log_action(
            action='BULK_CREATE',
            entity_type='PARTICIPANT',
            description=f"Se cargaron {created} participantes desde CSV",
            admin_id=admin_id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': f'Se cargaron {created} participantes',
            'created': created,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 400


@participants_bp.route('/send-invitations', methods=['POST'])
@jwt_required()
def send_invitations():
    """Enviar invitaciones de encuesta a participantes seleccionados"""
    data = request.get_json()
    participant_ids = data.get('participant_ids', [])
    
    if not participant_ids:
        # Si no se especifican IDs, enviar a todos los que no han votado
        participants = Participant.query.filter_by(has_voted=False).all()
    else:
        participants = Participant.query.filter(Participant.id.in_(participant_ids)).all()
    
    if not participants:
        return jsonify({'error': 'No hay participantes para enviar invitaciones'}), 400
    
    success_count, failed_count, errors = EmailService.send_bulk_invitations(participants)
    
    # Log de auditoría
    admin_id = int(get_jwt_identity())
    AuditService.log_action(
        action='SEND_INVITATIONS',
        entity_type='PARTICIPANT',
        description=f"Se enviaron {success_count} invitaciones",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': f'Invitaciones enviadas exitosamente',
        'success_count': success_count,
        'failed_count': failed_count,
        'errors': errors[:10]  # Limitar a 10 errores
    }), 200


@participants_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas de participantes - Público"""
    current_app.logger.info('=== LLAMADA A /api/participants/stats ===')
    
    total = Participant.query.count()
    current_app.logger.info(f'Total participants: {total}')
    
    # Contar participantes únicos que han votado (basado en votos reales)
    voted_participant_ids = db.session.query(Vote.participant_id).distinct().count()
    current_app.logger.info(f'Voted participants (distinct): {voted_participant_ids}')
    
    pending = total - voted_participant_ids
    participation_rate = (voted_participant_ids / total * 100) if total > 0 else 0
    
    result = {
        'total': total,
        'voted': voted_participant_ids,
        'pending': pending,
        'participation_rate': participation_rate
    }
    current_app.logger.info(f'Retornando stats: {result}')
    
    return jsonify(result), 200
