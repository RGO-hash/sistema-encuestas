#!/usr/bin/env python
"""Script para actualizar la base de datos con nuevas tablas"""
from app import create_app, db
from app.models import ParticipantUser
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✓ Database tables created successfully")
    
    # Verificar que la tabla existe
    inspector = inspect(db.engine)
    if 'participant_users' in inspector.get_table_names():
        print("✓ ParticipantUser table exists")
    else:
        print("✗ ParticipantUser table was not created")

