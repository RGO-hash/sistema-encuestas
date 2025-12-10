"""
Rutas para área de votación de participantes autenticados.
Sistema seguro de votación con prevención de duplicados.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import ParticipantUser, Participant, Position, Candidate, Vote
from app.services.audit_service import AuditService
from datetime import datetime

voting_participant_bp = Blueprint('voting_participant', __name__, url_prefix='')

@voting_participant_bp.route('/votar', methods=['GET'])
@voting_participant_bp.route('/vote', methods=['GET'])
@jwt_required()
def voting_page():
    """Mostrar página de votación para participantes autenticados"""
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    return render_template('participant_voting.html', user=participant_user)

@voting_participant_bp.route('/api/voting/active-surveys', methods=['GET'])
@jwt_required()
def get_active_surveys():
    """
    Obtener encuestas activas donde el usuario no ha votado aún.
    
    Response:
    {
        "surveys": [
            {
                "id": 1,
                "positions": [
                    {
                        "id": 1,
                        "name": "Presidente",
                        "candidates": [...]
                    }
                ]
            }
        ]
    }
    """
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Obtener el Participant asociado
    participant = participant_user.participant
    if not participant:
        return jsonify({'error': 'Participante no vinculado'}), 404
    
    # Permitir votar en cada sesión - no verificar has_voted
    # Los usuarios pueden votar cada vez que inician sesión
    
    # Obtener todas las posiciones activas
    positions = Position.query.filter_by(is_active=True).order_by(Position.order).all()
    
    if not positions:
        return jsonify({
            'message': 'No hay encuestas activas en este momento',
            'surveys': []
        }), 200
    
    surveys_data = []
    
    positions_data = []
    for position in positions:
        # Obtener candidatos para esta posición
        candidates = Candidate.query.filter_by(
            position_id=position.id
        ).order_by(Candidate.order).all()
        
        positions_data.append({
            'id': position.id,
            'name': position.name,
            'description': position.description,
            'candidates': [
                {
                    'id': c.id,
                    'name': c.name,
                    'description': c.description
                }
                for c in candidates
            ]
        })
    
    # Por ahora, retornamos una "encuesta" con todas las posiciones
    surveys_data.append({
        'id': 1,
        'title': 'Encuesta General',
        'description': 'Votación de posiciones',
        'positions': positions_data,
        'has_voted': participant.has_voted
    })
    
    return jsonify({
        'participant': {
            'id': participant.id,
            'email': participant.email,
            'first_name': participant.first_name,
            'last_name': participant.last_name
        },
        'surveys': surveys_data
    }), 200

@voting_participant_bp.route('/api/voting/submit-votes', methods=['POST'])
@jwt_required()
def submit_votes():
    """
    API para registrar votos del participante.
    
    CRÍTICO: Prevenir votos duplicados y garantizar un voto por posición.
    
    Request JSON:
    {
        "votes": {
            "1": {
                "type": "candidate",
                "candidate_id": 5
            },
            "2": {
                "type": "blanco"
            }
        }
    }
    
    Response:
    {
        "message": "Votos registrados exitosamente",
        "votes_count": 5
    }
    """
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user or not participant_user.is_active:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    participant = participant_user.participant
    if not participant:
        return jsonify({'error': 'Participante no vinculado'}), 404
    
    # Permitir votar múltiples veces - los votos se acumulan sin eliminar previos
    # Todos los votos quedan registrados en el historial
    
    data = request.get_json()
    votes_data = data.get('votes', {})
    
    if not votes_data:
        return jsonify({'error': 'No se proporcionaron votos'}), 400
    
    valid_vote_types = ['candidate', 'no_se', 'ninguno', 'abstencion', 'blanco']
    votes_to_register = []
    
    try:
        # Validar todos los votos antes de guardar
        for position_id_str, vote_info in votes_data.items():
            try:
                position_id = int(position_id_str)
            except (ValueError, TypeError):
                return jsonify({'error': f'ID de posición inválido: {position_id_str}'}), 400
            
            vote_type = vote_info.get('type', '').lower()
            candidate_id = vote_info.get('candidate_id')
            
            # Validar posición
            position = Position.query.get(position_id)
            if not position or not position.is_active:
                return jsonify({'error': f'Posición {position_id} no disponible'}), 404
            
            # Validar tipo de voto
            if vote_type not in valid_vote_types:
                return jsonify({'error': f'Tipo de voto inválido: {vote_type}'}), 400
            
            # Si es voto a candidato, validar que exista
            if vote_type == 'candidate':
                if not candidate_id:
                    return jsonify({'error': f'Candidato requerido para posición {position_id}'}), 400
                
                candidate = Candidate.query.get(candidate_id)
                if not candidate or candidate.position_id != position_id:
                    return jsonify({'error': f'Candidato {candidate_id} no válido para posición {position_id}'}), 404
            else:
                candidate_id = None
            
            # CRÍTICO: Validar que no exista voto anterior para esta posición
            existing_vote = Vote.query.filter_by(
                participant_id=participant.id,
                position_id=position_id
            ).first()
            
            if existing_vote:
                return jsonify({'error': f'Ya existe voto para la posición {position_id}'}), 409
            
            votes_to_register.append({
                'position_id': position_id,
                'vote_type': vote_type,
                'candidate_id': candidate_id
            })
        
        # Si llegamos aquí, todos los votos son válidos
        # Ahora registrar los votos
        
        for vote_data in votes_to_register:
            vote = Vote(
                participant_id=participant.id,
                position_id=vote_data['position_id'],
                candidate_id=vote_data['candidate_id'],
                vote_type=vote_data['vote_type'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(vote)
        
        # Marcar participante como votante
        participant.has_voted = True
        participant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log de auditoría
        AuditService.log_action(
            action='VOTE_SUBMITTED',
            entity_type='PARTICIPANT',
            entity_id=participant.id,
            description=f"Participante {participant.email} ha votado ({len(votes_to_register)} posiciones)",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Votos registrados exitosamente',
            'votes_count': len(votes_to_register),
            'participant': {
                'has_voted': True,
                'voted_at': datetime.utcnow().isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al registrar votos: {str(e)}")
        return jsonify({'error': 'Error al registrar votos'}), 500

@voting_participant_bp.route('/api/voting/vote-status', methods=['GET'])
@jwt_required()
def get_vote_status():
    """
    Obtener estado de votación del usuario actual.
    
    Response:
    {
        "has_voted": false,
        "user": {...}
    }
    """
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    participant = participant_user.participant
    
    return jsonify({
        'has_voted': participant.has_voted if participant else False,
        'user': {
            'id': participant_user.id,
            'email': participant_user.email,
            'first_name': participant_user.first_name,
            'last_name': participant_user.last_name,
            'full_name': f"{participant_user.first_name} {participant_user.last_name}"
        }
    }), 200

@voting_participant_bp.route('/api/voting/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """
    Obtener información del usuario participante autenticado.
    """
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'user': participant_user.to_dict()
    }), 200

@voting_participant_bp.route('/api/voting/my-votes', methods=['GET'])
@jwt_required()
def get_user_votes():
    """
    Obtener los votos registrados del usuario actual.
    Útil para confirmar o verificar votos posteriores.
    """
    participant_user_id = int(get_jwt_identity())
    participant_user = ParticipantUser.query.get(participant_user_id)
    
    if not participant_user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    participant = participant_user.participant
    if not participant:
        return jsonify({
            'message': 'Participante no vinculado',
            'votes': []
        }), 200
    
    # Obtener votos del participante
    votes = Vote.query.filter_by(participant_id=participant.id).all()
    
    votes_data = []
    for vote in votes:
        position = Position.query.get(vote.position_id)
        candidate_name = vote.candidate.name if vote.candidate else None
        
        votes_data.append({
            'id': vote.id,
            'position': {
                'id': position.id,
                'name': position.name
            },
            'vote_type': vote.vote_type,
            'candidate': candidate_name,
            'created_at': vote.created_at.isoformat()
        })
    
    return jsonify({
        'votes': votes_data,
        'total_votes': len(votes_data)
    }), 200
