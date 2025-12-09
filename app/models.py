from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON
import hashlib
import secrets

class Participant(db.Model):
    """Modelo para participantes de la encuesta"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    field1 = db.Column(db.String(255), nullable=True)
    field2 = db.Column(db.String(255), nullable=True)
    field3 = db.Column(db.String(255), nullable=True)
    has_voted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    votes = db.relationship('Vote', backref='participant', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'field1': self.field1,
            'field2': self.field2,
            'field3': self.field3,
            'has_voted': self.has_voted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Position(db.Model):
    """Modelo para cargos/posiciones"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    candidates = db.relationship('Candidate', backref='position', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='position', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'is_active': self.is_active,
            'candidate_count': self.candidates.count(),
            'created_at': self.created_at.isoformat()
        }


class Candidate(db.Model):
    """Modelo para candidatos/aspirantes"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('position_id', 'name', name='unique_candidate_per_position'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'position_id': self.position_id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'vote_count': self.votes.count(),
            'created_at': self.created_at.isoformat()
        }


class Vote(db.Model):
    """Modelo para votos/intención de voto"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=True)
    vote_type = db.Column(db.String(50), nullable=False)  # 'candidate', 'no_se', 'ninguno', 'abstencion', 'blanco'
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 o IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'position_id', name='unique_vote_per_position'),
        db.Index('idx_position_vote_type', 'position_id', 'vote_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'position_id': self.position_id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'vote_type': self.vote_type,
            'created_at': self.created_at.isoformat()
        }


class AdminUser(db.Model):
    """Modelo para usuarios administradores"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hashear contraseña"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verificar contraseña"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class AuditLog(db.Model):
    """Modelo para logs de auditoría"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
