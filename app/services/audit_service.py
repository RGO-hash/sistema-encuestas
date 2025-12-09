from flask import current_app
from app.models import AuditLog, AdminUser
from datetime import datetime

class AuditService:
    """Servicio para registrar auditoría"""
    
    @staticmethod
    def log_action(action, entity_type, entity_id=None, description=None, admin_id=None, ip_address=None):
        """
        Registrar una acción en el log de auditoría
        
        Args:
            action: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc)
            entity_type: Tipo de entidad (PARTICIPANT, POSITION, CANDIDATE, VOTE, etc)
            entity_id: ID de la entidad afectada
            description: Descripción adicional de la acción
            admin_id: ID del admin que realizó la acción
            ip_address: Dirección IP del cliente
        """
        try:
            log_entry = AuditLog(
                admin_id=admin_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                ip_address=ip_address,
                created_at=datetime.utcnow()
            )
            
            from app.extensions import db
            db.session.add(log_entry)
            db.session.commit()
            
            current_app.logger.info(
                f"[AUDIT] {action} - {entity_type}:{entity_id} - Admin:{admin_id} - IP:{ip_address}"
            )
            
        except Exception as e:
            current_app.logger.error(f"Error logging audit: {str(e)}")
    
    @staticmethod
    def get_audit_logs(limit=100, entity_type=None, action=None):
        """
        Obtener logs de auditoría con filtros opcionales
        
        Args:
            limit: Límite de registros
            entity_type: Filtrar por tipo de entidad
            action: Filtrar por acción
        
        Returns:
            Lista de logs
        """
        query = AuditLog.query
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if action:
            query = query.filter_by(action=action)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
