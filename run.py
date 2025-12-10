from app import create_app, db
from app.models import Participant, Position, Candidate, Vote, AdminUser, AuditLog
from werkzeug.serving import make_server
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Participant': Participant,
        'Position': Position,
        'Candidate': Candidate,
        'Vote': Vote,
        'AdminUser': AdminUser,
        'AuditLog': AuditLog
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Usar Werkzeug directamente para evitar problemas con Flask dev server
    server = make_server('0.0.0.0', port, app, threaded=True)
    print(f' * Running on http://0.0.0.0:{port}')
    print(f' * Running on http://127.0.0.1:{port}')
    print(' * Press CTRL+C to quit')
    server.serve_forever()
