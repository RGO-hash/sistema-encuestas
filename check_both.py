from app import create_app, db
from app.models import Participant, ParticipantUser

app = create_app('development')
with app.app_context():
    print('=== PARTICIPANTES EN BD ===')
    participants = Participant.query.all()
    for p in participants:
        print(f'ID: {p.id}, Email: {p.email}, Ha votado: {p.has_voted}')
    
    print('\n=== USUARIOS PARTICIPANTES ===')
    users = ParticipantUser.query.all()
    for u in users:
        print(f'User ID: {u.id}, Email: {u.email}, Participant ID: {u.participant_id}')
