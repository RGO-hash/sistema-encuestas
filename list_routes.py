"""Script para listar todas las rutas registradas en la aplicación"""
from app import create_app
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

print("\n" + "="*80)
print("RUTAS REGISTRADAS EN LA APLICACIÓN")
print("="*80 + "\n")

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': str(rule)
    })

# Ordenar por path
routes.sort(key=lambda x: x['path'])

# Buscar específicamente la ruta que nos interesa
voting_routes = [r for r in routes if 'voting' in r['path'].lower() or 'survey' in r['path'].lower()]

print("RUTAS DE VOTACIÓN ENCONTRADAS:")
print("-" * 80)
for route in voting_routes:
    print(f"{route['methods']:10} {route['path']:50} -> {route['endpoint']}")

print("\n\nTODAS LAS RUTAS API:")
print("-" * 80)
api_routes = [r for r in routes if r['path'].startswith('/api/')]
for route in api_routes:
    print(f"{route['methods']:10} {route['path']:50} -> {route['endpoint']}")

print("\n" + "="*80)
print(f"Total de rutas: {len(routes)}")
print("="*80)
