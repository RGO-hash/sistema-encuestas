from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.extensions import db
from app.models import Vote, Participant, Position, Candidate
from app.services.report_service import ReportService
from app.services.audit_service import AuditService
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

voting_bp = Blueprint('voting', __name__, url_prefix='/api/voting')

@voting_bp.route('/public/positions', methods=['GET'])
def get_survey_positions():
    """Obtener posiciones para la encuesta pública"""
    email = request.args.get('email', '')
    token = request.args.get('token', '')
    
    # Validar participante
    participant = Participant.query.filter_by(email=email).first()
    
    if not participant:
        return jsonify({'error': 'Participante no encontrado'}), 404
    
    # Permitir votar en cada sesión - no verificar has_voted
    
    # Obtener posiciones activas con candidatos
    positions = Position.query.filter_by(is_active=True).order_by(Position.order).all()
    
    positions_data = []
    for position in positions:
        candidates = Candidate.query.filter_by(position_id=position.id).order_by(Candidate.order).all()
        
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
    
    return jsonify({
        'participant': {
            'email': participant.email,
            'name': f"{participant.first_name} {participant.last_name}"
        },
        'positions': positions_data
    }), 200


@voting_bp.route('/public/submit', methods=['POST'])
def submit_vote():
    """Registrar voto del participante"""
    data = request.get_json()
    email = data.get('email', '').strip()
    token = data.get('token', '')
    votes = data.get('votes', {})
    
    # Validar participante
    participant = Participant.query.filter_by(email=email).first()
    
    if not participant:
        return jsonify({'error': 'Participante no encontrado'}), 404
    
    # Permitir votar múltiples veces - eliminar votos previos
    existing_votes = Vote.query.filter_by(participant_id=participant.id).all()
    if existing_votes:
        for vote in existing_votes:
            db.session.delete(vote)
        db.session.commit()
    
    try:
        # Registrar votos
        for position_id_str, vote_data in votes.items():
            position_id = int(position_id_str)
            position = Position.query.get(position_id)
            
            if not position:
                continue
            
            # Verificar que no exista voto previo
            existing_vote = Vote.query.filter_by(
                participant_id=participant.id,
                position_id=position_id
            ).first()
            
            if existing_vote:
                db.session.delete(existing_vote)
            
            vote_type = vote_data.get('type')
            candidate_id = vote_data.get('candidate_id')
            
            # Validar tipo de voto
            valid_types = ['candidate', 'no_se', 'ninguno', 'abstencion', 'blanco']
            if vote_type not in valid_types:
                return jsonify({'error': f'Tipo de voto inválido: {vote_type}'}), 400
            
            vote = Vote(
                participant_id=participant.id,
                position_id=position_id,
                candidate_id=candidate_id if vote_type == 'candidate' else None,
                vote_type=vote_type,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            
            db.session.add(vote)
        
        # Marcar como votado
        participant.has_voted = True
        participant.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log de auditoría
        AuditService.log_action(
            action='VOTE',
            entity_type='VOTE',
            entity_id=participant.id,
            description=f"Participante {email} ha votado",
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Voto registrado exitosamente',
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registrando voto: {str(e)}")
        return jsonify({'error': 'Error al registrar voto'}), 500


@voting_bp.route('/results', methods=['GET'])
@jwt_required()
def get_results():
    """Obtener resultados de la encuesta (admin)"""
    position_id = request.args.get('position_id', type=int)
    
    results = ReportService.get_position_results(position_id)
    summary = ReportService.get_survey_summary()
    
    return jsonify({
        'summary': summary,
        'results': results
    }), 200


@voting_bp.route('/results/timeline', methods=['GET'])
@jwt_required()
def get_timeline():
    """Obtener línea de tiempo de votos"""
    timeline = ReportService.get_participation_timeline()
    return jsonify({'timeline': timeline}), 200


@voting_bp.route('/results/export-csv', methods=['GET'])
@jwt_required()
def export_csv():
    """Exportar resultados a CSV"""
    try:
        csv_file = ReportService.export_to_csv()
        
        return send_file(
            csv_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"encuesta_resultados_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        current_app.logger.error(f"Error exportando CSV: {str(e)}")
        return jsonify({'error': 'Error al exportar resultados'}), 500


@voting_bp.route('/results/audit-log', methods=['GET'])
@jwt_required()
def get_audit_log():
    """Obtener log de auditoría de votos"""
    audit_log = ReportService.get_detailed_audit_log()
    return jsonify({'audit_log': audit_log}), 200


@voting_bp.route('/results/export-audit', methods=['GET'])
@jwt_required()
def export_audit_json():
    """Exportar log de auditoría a JSON"""
    try:
        json_data = ReportService.export_audit_to_json()
        
        return send_file(
            BytesIO(json_data.encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"auditoria_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
    except Exception as e:
        current_app.logger.error(f"Error exportando auditoría: {str(e)}")
        return jsonify({'error': 'Error al exportar auditoría'}), 500


from io import BytesIO
