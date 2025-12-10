from flask_mail import Message
from flask import current_app, url_for
from app.extensions import mail
import secrets
from datetime import datetime, timedelta
import base64

class EmailService:
    """Servicio para envío de correos"""
    
    @staticmethod
    def send_confirmation_email(email, name, confirmation_url):
        """
        Enviar email de confirmación de registro
        
        Args:
            email: Email del usuario
            name: Nombre completo del usuario
            confirmation_url: URL para confirmar el email
        """
        try:
            subject = "Confirma tu email - Sistema de Encuestas"
            
            html_body = f"""
            <html dir="ltr">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4361ee; color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                        .button {{ display: inline-block; background-color: #4361ee; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                        .button:hover {{ background-color: #3a4fd8; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>✉️ Confirma tu Email</h1>
                        </div>
                        <div class="content">
                            <p>Hola <strong>{name}</strong>,</p>
                            <p>Te damos la bienvenida al Sistema de Encuestas. Para completar tu registro, necesitas confirmar tu dirección de email.</p>
                            <p>Haz clic en el siguiente botón para confirmar tu email:</p>
                            <center>
                                <a href="{confirmation_url}" class="button">Confirmar Email</a>
                            </center>
                            <p style="color: #666; font-size: 14px;">O copia este enlace en tu navegador:<br>
                            <code style="background-color: #e9ecef; padding: 5px; border-radius: 3px; word-break: break-all;">{confirmation_url}</code></p>
                            <hr>
                            <p style="font-size: 13px; color: #999;">
                                ⚠️ Este enlace expirará en 24 horas.<br>
                                Si no solicitaste este registro, ignora este email.
                            </p>
                        </div>
                        <div class="footer">
                            <p>© {datetime.utcnow().year} Sistema de Encuestas. Todos los derechos reservados.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_body
            )
            
            mail.send(msg)
            return True, "Email de confirmación enviado"
            
        except Exception as e:
            current_app.logger.error(f"Error enviando email de confirmación a {email}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_survey_invitation(participant_email, participant_name, survey_token=None):
        """
        Enviar invitación de encuesta al participante
        
        Args:
            participant_email: Email del participante
            participant_name: Nombre del participante
            survey_token: Token para validar el voto (opcional)
        """
        try:
            # Generar token si no se proporciona
            if not survey_token:
                survey_token = secrets.token_urlsafe(32)
            
            # Crear URL con parámetros seguros
            survey_url = url_for(
                'survey.vote_form',
                email=participant_email,
                token=survey_token,
                _external=True
            )
            
            subject = "Invitación a participar en la encuesta"
            
            html_body = f"""
            <html dir="ltr">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4361ee; color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                        .button {{ display: inline-block; background-color: #4361ee; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                        .button:hover {{ background-color: #3a4fd8; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🗳️ Encuesta de Votación</h1>
                        </div>
                        <div class="content">
                            <p>Hola <strong>{participant_name}</strong>,</p>
                            <p>Te invitamos a participar en nuestra encuesta de votación. Tu voto es importante para nosotros.</p>
                            <p>Haz clic en el siguiente botón para acceder a la encuesta:</p>
                            <center>
                                <a href="{survey_url}" class="button">Participar en la encuesta</a>
                            </center>
                            <p style="color: #666; font-size: 14px;">O copia este enlace en tu navegador:<br>
                            <code style="background-color: #e9ecef; padding: 5px; border-radius: 3px;">{survey_url}</code></p>
                            <hr>
                            <p style="font-size: 13px; color: #999;">
                                ⚠️ Este enlace es personal y único para ti. No lo compartas con otras personas.<br>
                                El enlace expirará en 30 días.
                            </p>
                        </div>
                        <div class="footer">
                            <p>© {datetime.utcnow().year} Sistema de Encuestas. Todos los derechos reservados.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[participant_email],
                html=html_body
            )
            
            mail.send(msg)
            return True, "Correo enviado exitosamente"
            
        except Exception as e:
            current_app.logger.error(f"Error enviando email a {participant_email}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_bulk_invitations(participants):
        """
        Enviar invitaciones en lote a participantes
        
        Args:
            participants: Lista de objetos Participant
        
        Returns:
            Tupla (success_count, failed_count, errors)
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for participant in participants:
            success, message = EmailService.send_survey_invitation(
                participant.email,
                participant.first_name
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                errors.append({
                    'email': participant.email,
                    'error': message
                })
        
        return success_count, failed_count, errors
    
    @staticmethod
    def send_results_notification(admin_email, report_summary):
        """Enviar notificación de resultados al administrador"""
        try:
            subject = "Reporte de Resultados de Encuesta"
            
            html_body = f"""
            <html dir="ltr">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4361ee; color: white; padding: 20px; border-radius: 5px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                        th {{ background-color: #f0f0f0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Reporte de Encuesta</h2>
                        </div>
                        <div style="margin-top: 20px;">
                            <p>Se adjunta el reporte de resultados de la encuesta.</p>
                            {report_summary}
                            <p style="margin-top: 30px; color: #666; font-size: 12px;">
                                Este es un email automático, por favor no responda.
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[admin_email],
                html=html_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error enviando reporte a {admin_email}: {str(e)}")
            return False
