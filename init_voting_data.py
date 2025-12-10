"""
Script para inicializar datos de votación
Crea posiciones y candidatos por defecto si no existen
"""
from app import create_app, db
from app.models import Position, Candidate
import os

def init_voting_data():
    """Inicializar posiciones y candidatos de ejemplo"""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Verificar si ya existen posiciones
        existing_positions = Position.query.count()
        
        if existing_positions > 0:
            print(f"✓ Ya existen {existing_positions} posiciones en la base de datos")
            print("  Las posiciones actuales son:")
            for pos in Position.query.all():
                candidates_count = Candidate.query.filter_by(position_id=pos.id).count()
                print(f"  - {pos.name} (ID: {pos.id}, Activa: {pos.is_active}, Candidatos: {candidates_count})")
            return
        
        print("Creando posiciones y candidatos por defecto...")
        
        # Crear posiciones
        positions_data = [
            {'name': 'Presidente', 'description': 'Presidente de la organización', 'order': 1},
            {'name': 'Vicepresidente', 'description': 'Vicepresidente de la organización', 'order': 2},
            {'name': 'Secretario', 'description': 'Secretario general', 'order': 3},
            {'name': 'Tesorero', 'description': 'Tesorero de la organización', 'order': 4}
        ]
        
        positions = {}
        for pos_data in positions_data:
            position = Position(
                name=pos_data['name'],
                description=pos_data['description'],
                order=pos_data['order'],
                is_active=True
            )
            db.session.add(position)
            db.session.flush()
            positions[pos_data['name']] = position
            print(f"✓ Posición creada: {pos_data['name']}")
        
        # Crear candidatos
        candidates_data = [
            # Presidente
            {'name': 'Juan Pérez', 'description': 'Candidato A para Presidente', 'position': 'Presidente', 'order': 1},
            {'name': 'María González', 'description': 'Candidato B para Presidente', 'position': 'Presidente', 'order': 2},
            
            # Vicepresidente
            {'name': 'Carlos Ramírez', 'description': 'Candidato A para Vicepresidente', 'position': 'Vicepresidente', 'order': 1},
            {'name': 'Ana Martínez', 'description': 'Candidato B para Vicepresidente', 'position': 'Vicepresidente', 'order': 2},
            
            # Secretario
            {'name': 'Luis Torres', 'description': 'Candidato A para Secretario', 'position': 'Secretario', 'order': 1},
            {'name': 'Carmen Silva', 'description': 'Candidato B para Secretario', 'position': 'Secretario', 'order': 2},
            
            # Tesorero
            {'name': 'Roberto Díaz', 'description': 'Candidato A para Tesorero', 'position': 'Tesorero', 'order': 1},
            {'name': 'Patricia Ruiz', 'description': 'Candidato B para Tesorero', 'position': 'Tesorero', 'order': 2}
        ]
        
        for cand_data in candidates_data:
            candidate = Candidate(
                name=cand_data['name'],
                description=cand_data['description'],
                position_id=positions[cand_data['position']].id,
                order=cand_data['order']
            )
            db.session.add(candidate)
            print(f"✓ Candidato creado: {cand_data['name']} - {cand_data['position']}")
        
        db.session.commit()
        print("\n✅ Datos de votación inicializados correctamente")
        print(f"   - {len(positions_data)} posiciones creadas")
        print(f"   - {len(candidates_data)} candidatos creados")
        print("\nAhora los usuarios podrán votar cuando inicien sesión.")

if __name__ == '__main__':
    init_voting_data()
