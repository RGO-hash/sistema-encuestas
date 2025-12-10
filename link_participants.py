from app import create_app, db
from app.models import ParticipantUser, Participant

app = create_app('development')
with app.app_context():
    print('=== VINCULANDO PARTICIPANTES ===')
    users = ParticipantUser.query.all()
    
    for u in users:
        if not u.participant:
            # Buscar si ya existe un Participant con este email
            existing_participant = Participant.query.filter_by(email=u.email).first()
            
            if existing_participant:
                # Vincular con el Participant existente
                u.participant_id = existing_participant.id
                db.session.add(u)
                print(f'Vinculado con existente: {u.email} -> Participante ID: {existing_participant.id}')
            else:
                # Crear un nuevo Participant para este usuario con sus datos
                participant = Participant(
                    email=u.email,
                    first_name=u.first_name,
                    last_name=u.last_name
                )
                db.session.add(participant)
                db.session.flush()  # Para obtener el ID
                
                # Vincular el usuario al participante
                u.participant_id = participant.id
                db.session.add(u)
                print(f'Vinculado nuevo: {u.email} -> Participante ID: {participant.id}')
        else:
            print(f'Skipped: {u.email} (ya vinculado)')
    
    db.session.commit()
    print('\n✓ Participantes vinculados exitosamente')
    
    # Verificar
    print('\n=== VERIFICACIÓN ===')
    users = ParticipantUser.query.all()
    for u in users:
        print(f'User: {u.email}, Participante ID: {u.participant_id}, Ha votado: {u.participant.has_voted if u.participant else "N/A"}')
