from app import create_app, db
from app.models import Participant, ParticipantUser

app = create_app('development')
with app.app_context():
    print('=== VINCULANDO USUARIOS CON PARTICIPANTES EXISTENTES ===')
    users = ParticipantUser.query.all()
    
    for u in users:
        if not u.participant_id:
            # Buscar un participante con el mismo email
            participant = Participant.query.filter_by(email=u.email).first()
            
            if participant:
                u.participant_id = participant.id
                db.session.add(u)
                print(f'Vinculado: {u.email} -> Participante ID: {participant.id}')
            else:
                print(f'Sin participante: {u.email}')
        else:
            print(f'Skipped: {u.email} (ya vinculado a {u.participant_id})')
    
    db.session.commit()
    print('\n✓ Vinculación completada')
    
    # Verificar
    print('\n=== VERIFICACIÓN FINAL ===')
    users = ParticipantUser.query.all()
    for u in users:
        participant = u.participant
        if participant:
            print(f'✓ User: {u.email} -> Participante: {participant.email} (Ha votado: {participant.has_voted})')
        else:
            print(f'✗ User: {u.email} -> SIN PARTICIPANTE')
