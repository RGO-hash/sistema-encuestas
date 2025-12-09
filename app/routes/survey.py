from flask import Blueprint, render_template, request, jsonify, current_app
from app.extensions import db
from app.models import Position, Candidate, Vote, Participant
from app.services.audit_service import AuditService
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

survey_bp = Blueprint('survey', __name__, url_prefix='/api/survey')

@survey_bp.route('/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """Obtener lista de posiciones (admin)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Position.query.order_by(Position.order).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'positions': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@survey_bp.route('/positions', methods=['POST'])
@jwt_required()
def create_position():
    """Crear nueva posición"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    # Verificar duplicado
    if Position.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'La posición ya existe'}), 409
    
    position = Position(
        name=data['name'].strip(),
        description=data.get('description', '').strip(),
        order=data.get('order', 0)
    )
    
    db.session.add(position)
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='CREATE',
        entity_type='POSITION',
        entity_id=position.id,
        description=f"Posición '{position.name}' creada",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Posición creada exitosamente',
        'position': position.to_dict()
    }), 201


@survey_bp.route('/positions/<int:position_id>', methods=['PUT'])
@jwt_required()
def update_position(position_id):
    """Actualizar posición"""
    position = Position.query.get(position_id)
    
    if not position:
        return jsonify({'error': 'Posición no encontrada'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        position.name = data['name'].strip()
    if 'description' in data:
        position.description = data['description'].strip()
    if 'order' in data:
        position.order = data['order']
    if 'is_active' in data:
        position.is_active = data['is_active']
    
    position.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='UPDATE',
        entity_type='POSITION',
        entity_id=position_id,
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Posición actualizada exitosamente',
        'position': position.to_dict()
    }), 200


@survey_bp.route('/positions/<int:position_id>', methods=['DELETE'])
@jwt_required()
def delete_position(position_id):
    """Eliminar posición"""
    position = Position.query.get(position_id)
    
    if not position:
        return jsonify({'error': 'Posición no encontrada'}), 404
    
    pos_name = position.name
    db.session.delete(position)
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='DELETE',
        entity_type='POSITION',
        entity_id=position_id,
        description=f"Posición '{pos_name}' eliminada",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({'message': 'Posición eliminada exitosamente'}), 200


@survey_bp.route('/candidates', methods=['GET'])
@jwt_required()
def get_candidates():
    """Obtener candidatos (admin)"""
    position_id = request.args.get('position_id', type=int)
    
    query = Candidate.query
    
    if position_id:
        query = query.filter_by(position_id=position_id)
    
    candidates = query.order_by(Candidate.position_id, Candidate.order).all()
    
    return jsonify({
        'candidates': [c.to_dict() for c in candidates],
        'total': len(candidates)
    }), 200


@survey_bp.route('/candidates', methods=['POST'])
@jwt_required()
def create_candidate():
    """Crear nuevo candidato"""
    data = request.get_json()
    
    if not data.get('position_id') or not data.get('name'):
        return jsonify({'error': 'position_id y name son requeridos'}), 400
    
    position = Position.query.get(data['position_id'])
    if not position:
        return jsonify({'error': 'Posición no encontrada'}), 404
    
    # Verificar duplicado por posición
    existing = Candidate.query.filter_by(
        position_id=data['position_id'],
        name=data['name'].strip()
    ).first()
    
    if existing:
        return jsonify({'error': 'El candidato ya existe en esta posición'}), 409
    
    candidate = Candidate(
        position_id=data['position_id'],
        name=data['name'].strip(),
        description=data.get('description', '').strip(),
        order=data.get('order', 0)
    )
    
    db.session.add(candidate)
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='CREATE',
        entity_type='CANDIDATE',
        entity_id=candidate.id,
        description=f"Candidato '{candidate.name}' creado para {position.name}",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Candidato creado exitosamente',
        'candidate': candidate.to_dict()
    }), 201


@survey_bp.route('/candidates/<int:candidate_id>', methods=['PUT'])
@jwt_required()
def update_candidate(candidate_id):
    """Actualizar candidato"""
    candidate = Candidate.query.get(candidate_id)
    
    if not candidate:
        return jsonify({'error': 'Candidato no encontrado'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        candidate.name = data['name'].strip()
    if 'description' in data:
        candidate.description = data['description'].strip()
    if 'order' in data:
        candidate.order = data['order']
    
    candidate.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='UPDATE',
        entity_type='CANDIDATE',
        entity_id=candidate_id,
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Candidato actualizado exitosamente',
        'candidate': candidate.to_dict()
    }), 200


@survey_bp.route('/candidates/<int:candidate_id>', methods=['DELETE'])
@jwt_required()
def delete_candidate(candidate_id):
    """Eliminar candidato"""
    candidate = Candidate.query.get(candidate_id)
    
    if not candidate:
        return jsonify({'error': 'Candidato no encontrado'}), 404
    
    cand_name = candidate.name
    db.session.delete(candidate)
    db.session.commit()
    
    # Log de auditoría
    admin_id = get_jwt_identity()
    AuditService.log_action(
        action='DELETE',
        entity_type='CANDIDATE',
        entity_id=candidate_id,
        description=f"Candidato '{cand_name}' eliminado",
        admin_id=admin_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({'message': 'Candidato eliminado exitosamente'}), 200
