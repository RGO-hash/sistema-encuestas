#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos con datos de ejemplo
Uso: python init_db.py
"""

from app import create_app, db
from app.models import Position, Candidate, Participant, AdminUser
from datetime import datetime

def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    
    app = create_app('development')
    
    with app.app_context():
        # Crear tablas
        db.create_all()
        print("✓ Tablas de base de datos creadas")
        
        # Crear admin por defecto
        if AdminUser.query.count() == 0:
            admin = AdminUser(
                email='admin@encuestas.com',
                full_name='Administrador',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin creado: admin@encuestas.com / admin123")
        
        # Crear posiciones de ejemplo
        if Position.query.count() == 0:
            positions_data = [
                {
                    'name': 'Presidente',
                    'description': 'Responsable de la dirección general',
                    'order': 1
                },
                {
                    'name': 'Vicepresidente',
                    'description': 'Apoyo al presidente',
                    'order': 2
                },
                {
                    'name': 'Tesorero',
                    'description': 'Gestión de finanzas',
                    'order': 3
                },
                {
                    'name': 'Secretario',
                    'description': 'Gestión administrativa',
                    'order': 4
                }
            ]
            
            positions = []
            for pos_data in positions_data:
                position = Position(**pos_data)
                db.session.add(position)
                positions.append(position)
            
            db.session.commit()
            print(f"✓ {len(positions)} posiciones creadas")
            
            # Crear candidatos de ejemplo
            candidates_data = [
                {'position': 0, 'name': 'Juan Pérez', 'description': 'Experiencia en gestión empresarial'},
                {'position': 0, 'name': 'María García', 'description': 'Especialista en liderazgo'},
                {'position': 0, 'name': 'Carlos López', 'description': 'Emprendedor exitoso'},
                {'position': 1, 'name': 'Ana Martínez', 'description': 'Coordinadora experimentada'},
                {'position': 1, 'name': 'David Ruiz', 'description': 'Especialista en operaciones'},
                {'position': 2, 'name': 'Laura Fernández', 'description': 'Contadora certificada'},
                {'position': 2, 'name': 'Roberto Díaz', 'description': 'Analista financiero'},
                {'position': 3, 'name': 'Isabel Sánchez', 'description': 'Abogada especializada'},
                {'position': 3, 'name': 'Miguel Rodríguez', 'description': 'Comunicólogo profesional'},
            ]
            
            candidate_count = 0
            for cand_data in candidates_data:
                position = positions[cand_data['position']]
                candidate = Candidate(
                    position_id=position.id,
                    name=cand_data['name'],
                    description=cand_data['description'],
                    order=cand_data['position']
                )
                db.session.add(candidate)
                candidate_count += 1
            
            db.session.commit()
            print(f"✓ {candidate_count} candidatos creados")
        
        # Crear participantes de ejemplo
        if Participant.query.count() == 0:
            participants_data = [
                {
                    'email': 'juan@example.com',
                    'first_name': 'Juan',
                    'last_name': 'Pérez',
                    'field1': 'Ventas',
                    'field2': 'Gerente',
                    'field3': 'Madrid'
                },
                {
                    'email': 'maria@example.com',
                    'first_name': 'María',
                    'last_name': 'García',
                    'field1': 'RRHH',
                    'field2': 'Especialista',
                    'field3': 'Barcelona'
                },
                {
                    'email': 'carlos@example.com',
                    'first_name': 'Carlos',
                    'last_name': 'López',
                    'field1': 'TI',
                    'field2': 'Ingeniero',
                    'field3': 'Valencia'
                },
                {
                    'email': 'ana@example.com',
                    'first_name': 'Ana',
                    'last_name': 'Martínez',
                    'field1': 'Finanzas',
                    'field2': 'Analista',
                    'field3': 'Sevilla'
                },
                {
                    'email': 'francisco@example.com',
                    'first_name': 'Francisco',
                    'last_name': 'Rodríguez',
                    'field1': 'Marketing',
                    'field2': 'Coordinador',
                    'field3': 'Bilbao'
                },
            ]
            
            for part_data in participants_data:
                participant = Participant(**part_data)
                db.session.add(participant)
            
            db.session.commit()
            print(f"✓ {len(participants_data)} participantes de ejemplo creados")
        
        print("\n" + "="*50)
        print("✓ Base de datos inicializada exitosamente")
        print("="*50)
        print("\nNOTA: Accede a http://localhost:5000")
        print("Usuario: admin@encuestas.com")
        print("Contraseña: admin123")
        print("\n⚠️  CAMBIAR LA CONTRASEÑA EN PRODUCCIÓN")

if __name__ == '__main__':
    init_database()
