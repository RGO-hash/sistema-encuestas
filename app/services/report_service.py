from flask import current_app
from app.extensions import db
from app.models import Vote, Position, Candidate, Participant
from sqlalchemy import func
from datetime import datetime
from io import BytesIO
import csv
import json

class ReportService:
    """Servicio para generar reportes de la encuesta"""
    
    @staticmethod
    def get_survey_summary():
        """Obtener resumen general de la encuesta"""
        total_participants = Participant.query.count()
        voted_participants = Participant.query.filter_by(has_voted=True).count()
        total_votes = Vote.query.count()
        
        return {
            'total_participants': total_participants,
            'voted_participants': voted_participants,
            'pending_participants': total_participants - voted_participants,
            'participation_rate': (voted_participants / total_participants * 100) if total_participants > 0 else 0,
            'total_votes': total_votes,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_position_results(position_id=None):
        """
        Obtener resultados detallados por posición
        
        Args:
            position_id: ID de la posición (None para todas)
        
        Returns:
            Diccionario con resultados por posición
        """
        query = Position.query
        if position_id:
            query = query.filter_by(id=position_id)
        
        positions = query.all()
        results = {}
        
        for position in positions:
            position_votes = Vote.query.filter_by(position_id=position.id).all()
            
            candidates_data = {}
            vote_counts = {
                'no_se': 0,
                'ninguno': 0,
                'abstencion': 0,
                'blanco': 0,
                'total': len(position_votes)
            }
            
            # Contar votos por candidato
            candidates = Candidate.query.filter_by(position_id=position.id).all()
            for candidate in candidates:
                vote_count = Vote.query.filter_by(
                    position_id=position.id,
                    candidate_id=candidate.id
                ).count()
                candidates_data[candidate.id] = {
                    'name': candidate.name,
                    'description': candidate.description,
                    'votes': vote_count,
                    'percentage': (vote_count / len(position_votes) * 100) if len(position_votes) > 0 else 0
                }
            
            # Contar votos especiales
            for vote in position_votes:
                if vote.vote_type == 'no_se':
                    vote_counts['no_se'] += 1
                elif vote.vote_type == 'ninguno':
                    vote_counts['ninguno'] += 1
                elif vote.vote_type == 'abstencion':
                    vote_counts['abstencion'] += 1
                elif vote.vote_type == 'blanco':
                    vote_counts['blanco'] += 1
            
            results[position.id] = {
                'position_id': position.id,
                'position_name': position.name,
                'candidates': candidates_data,
                'special_votes': {
                    'no_se': {
                        'count': vote_counts['no_se'],
                        'percentage': (vote_counts['no_se'] / vote_counts['total'] * 100) if vote_counts['total'] > 0 else 0
                    },
                    'ninguno': {
                        'count': vote_counts['ninguno'],
                        'percentage': (vote_counts['ninguno'] / vote_counts['total'] * 100) if vote_counts['total'] > 0 else 0
                    },
                    'abstencion': {
                        'count': vote_counts['abstencion'],
                        'percentage': (vote_counts['abstencion'] / vote_counts['total'] * 100) if vote_counts['total'] > 0 else 0
                    },
                    'blanco': {
                        'count': vote_counts['blanco'],
                        'percentage': (vote_counts['blanco'] / vote_counts['total'] * 100) if vote_counts['total'] > 0 else 0
                    }
                },
                'total_votes': vote_counts['total'],
                'winner': ReportService._get_position_winner(position.id, candidates_data)
            }
        
        return results
    
    @staticmethod
    def _get_position_winner(position_id, candidates_data):
        """Determinar el ganador de una posición"""
        if not candidates_data:
            return None
        
        winner = max(candidates_data.items(), key=lambda x: x[1]['votes'])
        if winner[1]['votes'] > 0:
            return {
                'candidate_id': winner[0],
                'candidate_name': winner[1]['name'],
                'votes': winner[1]['votes'],
                'percentage': winner[1]['percentage']
            }
        return None
    
    @staticmethod
    def export_to_csv():
        """Exportar resultados a CSV"""
        output = BytesIO()
        writer = csv.writer(output)
        
        # Encabezado
        writer.writerow(['Reporte de Encuesta', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Resumen
        summary = ReportService.get_survey_summary()
        writer.writerow(['Resumen General'])
        writer.writerow(['Total de Participantes', summary['total_participants']])
        writer.writerow(['Participantes que Votaron', summary['voted_participants']])
        writer.writerow(['Tasa de Participación', f"{summary['participation_rate']:.2f}%"])
        writer.writerow([])
        
        # Resultados por posición
        results = ReportService.get_position_results()
        for pos_id, pos_data in results.items():
            writer.writerow(['Posición: ' + pos_data['position_name']])
            writer.writerow(['Candidato', 'Votos', 'Porcentaje'])
            
            for cand_id, cand_data in pos_data['candidates'].items():
                writer.writerow([cand_data['name'], cand_data['votes'], f"{cand_data['percentage']:.2f}%"])
            
            writer.writerow(['No Sé', pos_data['special_votes']['no_se']['count'], f"{pos_data['special_votes']['no_se']['percentage']:.2f}%"])
            writer.writerow(['Ninguno', pos_data['special_votes']['ninguno']['count'], f"{pos_data['special_votes']['ninguno']['percentage']:.2f}%"])
            writer.writerow(['Abstención', pos_data['special_votes']['abstencion']['count'], f"{pos_data['special_votes']['abstencion']['percentage']:.2f}%"])
            writer.writerow(['Voto en Blanco', pos_data['special_votes']['blanco']['count'], f"{pos_data['special_votes']['blanco']['percentage']:.2f}%"])
            writer.writerow([])
        
        output.seek(0)
        return output
    
    @staticmethod
    def get_participation_timeline():
        """Obtener línea de tiempo de participación"""
        from sqlalchemy import func, text
        
        # Votos por día
        votes_per_day = db.session.query(
            func.date(Vote.created_at).label('date'),
            func.count().label('count')
        ).group_by('date').order_by('date').all()
        
        return [
            {
                'date': str(date),
                'votes': count
            }
            for date, count in votes_per_day
        ]
    
    @staticmethod
    def get_detailed_audit_log():
        """Obtener log detallado de votos con información de participante"""
        votes = Vote.query.join(Participant).join(Position).outerjoin(Candidate).all()
        
        audit_data = []
        for vote in votes:
            audit_data.append({
                'timestamp': vote.created_at.isoformat(),
                'participant_email': vote.participant.email,
                'position': vote.position.name,
                'vote_type': vote.vote_type,
                'candidate': vote.candidate.name if vote.candidate else None,
                'ip_address': vote.ip_address
            })
        
        return audit_data
    
    @staticmethod
    def export_audit_to_json():
        """Exportar log de auditoría a JSON"""
        audit_log = ReportService.get_detailed_audit_log()
        return json.dumps(audit_log, indent=2, ensure_ascii=False)
