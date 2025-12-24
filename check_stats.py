#!/usr/bin/env python
"""Verificar estadísticas reales de la base de datos"""

from app import create_app, db
from app.models import Participant, Vote

app = create_app('development')

with app.app_context():
    total = Participant.query.count()
    voted = db.session.query(Vote.participant_id).distinct().count()
    pending = total - voted
    rate = (voted / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 50)
    print("ESTADÍSTICAS REALES DEL DASHBOARD")
    print("=" * 50)
    print(f"Total Registrados:     {total}")
    print(f"Han Votado:            {voted}")
    print(f"Pendientes:            {pending}")
    print(f"Tasa Participación:    {rate:.1f}%")
    print("=" * 50 + "\n")
