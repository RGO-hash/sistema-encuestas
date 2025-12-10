from app import create_app, db
from app.models import Position, Candidate, ParticipantUser, Participant, Vote

app = create_app('development')
with app.app_context():
    print('=== POSICIONES ===')
    positions = Position.query.all()
    for p in positions:
        print(f'ID: {p.id}, Nombre: {p.name}, Activa: {p.is_active}')
    
    print('\n=== CANDIDATOS ===')
    candidates = Candidate.query.all()
    for c in candidates:
        print(f'ID: {c.id}, Nombre: {c.name}, Posicion: {c.position_id}')
    
    print('\n=== USUARIOS PARTICIPANTES ===')
    users = ParticipantUser.query.all()
    for u in users[:5]:
        participant = u.participant
        ha_votado = 'N/A'
        if participant:
            ha_votado = participant.has_voted
        print(f'User ID: {u.id}, Email: {u.email}, Participante: {participant is not None}, Ha votado: {ha_votado}')
    
    print('\n=== VOTOS REGISTRADOS ===')
    votes = Vote.query.all()
    print(f'Total votos: {len(votes)}')
    for v in votes[:5]:
        print(f'ID: {v.id}, Participante: {v.participant_id}, Posicion: {v.position_id}, Candidato: {v.candidate_id}')
