from app import create_app, db
from app.models import Participant, Position, Candidate, Vote, AdminUser, AuditLog
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
    debug = os.environ.get('FLASK_ENV') == 'development'
    # Escuchar en localhost para ngrok
    app.run(host='127.0.0.1', port=port, debug=debug, use_reloader=False)
