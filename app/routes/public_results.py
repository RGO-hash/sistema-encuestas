"""
Rutas públicas para visualizar resultados de encuestas cerradas.
Accesible sin necesidad de autenticación.
"""

from flask import Blueprint, render_template, jsonify, request
from app.extensions import db
from app.models import Position, Candidate, Vote
from datetime import datetime

results_bp = Blueprint('results', __name__)

@results_bp.route('/resultados', methods=['GET'])
@results_bp.route('/results', methods=['GET'])
def results_page():
    """Mostrar página pública de resultados"""
    return render_template('public_results.html')

@results_bp.route('/api/results/summary', methods=['GET'])
def get_results_summary():
    """
    Obtener resumen de resultados de todas las encuestas.
    Ruta PÚBLICA - No requiere autenticación.
    
    Retorna información de todas las posiciones con:
    - Nombre de posición
    - Descripción
    - Candidatos y votos por cada uno
    - Porcentajes
    - Total de votos
    """
    try:
        # Obtener todas las posiciones activas
        positions = Position.query.filter_by(is_active=True).order_by(Position.order).all()
        
        results_data = []
        total_votes_cast = 0
        
        for position in positions:
            # Obtener candidatos de esta posición
            candidates = Candidate.query.filter_by(
                position_id=position.id
            ).order_by(Candidate.order).all()
            
            # Contar votos totales para esta posición
            position_votes = Vote.query.filter_by(position_id=position.id).all()
            total_position_votes = len(position_votes)
            total_votes_cast += total_position_votes
            
            # Contar votos por tipo
            votes_by_type = {
                'candidate': 0,
                'no_se': 0,
                'ninguno': 0,
                'abstencion': 0,
                'blanco': 0
            }
            
            for vote in position_votes:
                if vote.vote_type in votes_by_type:
                    votes_by_type[vote.vote_type] += 1
            
            # Construir datos de candidatos
            candidates_data = []
            for candidate in candidates:
                vote_count = candidate.votes.count()
                percentage = (vote_count / total_position_votes * 100) if total_position_votes > 0 else 0
                
                candidates_data.append({
                    'id': candidate.id,
                    'name': candidate.name,
                    'description': candidate.description,
                    'vote_count': vote_count,
                    'percentage': round(percentage, 2)
                })
            
            # Encontrar ganador (candidato con más votos)
            winner = None
            if candidates_data:
                winner = max(candidates_data, key=lambda x: x['vote_count'])
            
            results_data.append({
                'position_id': position.id,
                'position_name': position.name,
                'position_description': position.description,
                'total_votes': total_position_votes,
                'candidates': candidates_data,
                'winner': winner,
                'votes_by_type': votes_by_type
            })
        
        return jsonify({
            'summary': {
                'total_positions': len(results_data),
                'total_votes_cast': total_votes_cast,
                'generated_at': datetime.utcnow().isoformat()
            },
            'results': results_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener resultados',
            'message': str(e)
        }), 500

@results_bp.route('/api/results/position/<int:position_id>', methods=['GET'])
def get_position_results(position_id):
    """
    Obtener resultados detallados de una posición específica.
    Ruta PÚBLICA - No requiere autenticación.
    
    Response:
    {
        "position": {...},
        "candidates": [
            {
                "name": "Juan Pérez",
                "votes": 25,
                "percentage": 45.45
            }
        ],
        "statistics": {
            "total_votes": 55,
            "votes_blank": 2,
            "votes_abstain": 1,
            "votes_none": 2
        }
    }
    """
    position = Position.query.get(position_id)
    
    if not position:
        return jsonify({'error': 'Posición no encontrada'}), 404
    
    # Obtener candidatos
    candidates = Candidate.query.filter_by(
        position_id=position_id
    ).order_by(Candidate.order).all()
    
    # Obtener votos para esta posición
    votes = Vote.query.filter_by(position_id=position_id).all()
    total_votes = len(votes)
    
    # Contar votos por tipo
    votes_by_type = {
        'candidate': 0,
        'no_se': 0,
        'ninguno': 0,
        'abstencion': 0,
        'blanco': 0
    }
    
    for vote in votes:
        if vote.vote_type in votes_by_type:
            votes_by_type[vote.vote_type] += 1
    
    # Construir datos de candidatos
    candidates_data = []
    for candidate in candidates:
        vote_count = candidate.votes.count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        
        candidates_data.append({
            'id': candidate.id,
            'name': candidate.name,
            'description': candidate.description,
            'vote_count': vote_count,
            'percentage': round(percentage, 2)
        })
    
    # Ordenar por votos descendentes
    candidates_data.sort(key=lambda x: x['vote_count'], reverse=True)
    
    return jsonify({
        'position': {
            'id': position.id,
            'name': position.name,
            'description': position.description
        },
        'candidates': candidates_data,
        'statistics': {
            'total_votes': total_votes,
            'votes_candidate': votes_by_type['candidate'],
            'votes_no_se': votes_by_type['no_se'],
            'votes_none': votes_by_type['ninguno'],
            'votes_abstain': votes_by_type['abstencion'],
            'votes_blank': votes_by_type['blanco']
        }
    }), 200

@results_bp.route('/api/results/statistics', methods=['GET'])
def get_statistics():
    """
    Obtener estadísticas generales de la encuesta.
    Ruta PÚBLICA - No requiere autenticación.
    
    Response:
    {
        "statistics": {
            "total_participants": 100,
            "total_voted": 85,
            "participation_rate": 85.0,
            "total_positions": 5,
            "total_candidates": 12
        }
    }
    """
    from app.models import Participant
    
    try:
        # Contadores globales
        total_participants = Participant.query.count()
        total_voted = Participant.query.filter_by(has_voted=True).count()
        participation_rate = (total_voted / total_participants * 100) if total_participants > 0 else 0
        
        total_positions = Position.query.filter_by(is_active=True).count()
        total_candidates = Candidate.query.count()
        total_votes = Vote.query.count()
        
        return jsonify({
            'statistics': {
                'total_participants': total_participants,
                'total_voted': total_voted,
                'participation_rate': round(participation_rate, 2),
                'total_positions': total_positions,
                'total_candidates': total_candidates,
                'total_votes': total_votes,
                'average_votes_per_position': round(total_votes / total_positions, 2) if total_positions > 0 else 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener estadísticas',
            'message': str(e)
        }), 500

@results_bp.route('/api/results/timeline', methods=['GET'])
def get_voting_timeline():
    """
    Obtener línea de tiempo de votación (votos por hora).
    Útil para gráficos de participación en tiempo.
    Ruta PÚBLICA - No requiere autenticación.
    
    Response:
    {
        "timeline": [
            {
                "hour": "2024-01-15 10:00",
                "votes": 12,
                "cumulative": 12
            }
        ]
    }
    """
    try:
        # Obtener todos los votos ordenados por fecha
        votes = Vote.query.order_by(Vote.created_at).all()
        
        timeline_data = {}
        cumulative = 0
        
        for vote in votes:
            # Agrupar por hora
            hour_key = vote.created_at.strftime('%Y-%m-%d %H:00')
            
            if hour_key not in timeline_data:
                timeline_data[hour_key] = 0
            
            timeline_data[hour_key] += 1
            cumulative += 1
        
        # Convertir a lista ordenada
        timeline = []
        cumulative = 0
        for hour in sorted(timeline_data.keys()):
            cumulative += timeline_data[hour]
            timeline.append({
                'hour': hour,
                'votes': timeline_data[hour],
                'cumulative': cumulative
            })
        
        return jsonify({
            'timeline': timeline
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener línea de tiempo',
            'message': str(e)
        }), 500
