"""
Email Service using Resend
Handles sending verification emails with beautiful HTML templates
"""
import resend
from typing import Optional
from config import settings

# Configure Resend with API key
resend.api_key = settings.RESEND_API_KEY

class EmailService:
    """Service for sending emails via Resend"""
    
    @staticmethod
    def send_verification_email(
        to_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """
        Send a beautiful verification email with a link
        
        Args:
            to_email: Recipient email address
            user_name: Name of the user
            verification_token: Unique verification token
            
        Returns:
            bool: True if email sent successfully
        """
        # Build verification URL (will work for both web and mobile via deep links)
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token}"
        
        # Beautiful HTML template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verifica tu cuenta - nJoy</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <!-- Main Card -->
                <table role="presentation" style="max-width: 600px; width: 100%; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-radius: 20px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <!-- Header with gradient -->
                    <tr>
                        <td style="padding: 40px 40px 30px; text-align: center; background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); border-radius: 20px 20px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 32px; font-weight: 700; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
                                🎉 ¡Bienvenido a nJoy!
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; color: #1f2937; font-size: 18px; line-height: 1.6;">
                                Hola <strong style="color: #8b5cf6;">{user_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                ¡Gracias por registrarte! Para comenzar a disfrutar de los mejores eventos, 
                                necesitamos verificar tu dirección de correo electrónico.
                            </p>
                            
                            <!-- CTA Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{verification_url}" 
                                           style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); color: white; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); transition: transform 0.2s;">
                                            ✓ Verificar mi cuenta
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Alternative link -->
                            <p style="margin: 30px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
                                ¿El botón no funciona? Copia y pega este enlace en tu navegador:
                            </p>
                            <p style="margin: 10px 0 0; text-align: center;">
                                <a href="{verification_url}" style="color: #8b5cf6; font-size: 13px; word-break: break-all;">
                                    {verification_url}
                                </a>
                            </p>
                            
                            <!-- Security note -->
                            <div style="margin-top: 30px; padding: 20px; background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; border-radius: 8px;">
                                <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.6;">
                                    🔒 <strong>Nota de seguridad:</strong> Este enlace expirará en 24 horas. 
                                    Si no solicitaste esta verificación, puedes ignorar este correo.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background: #f9fafb; border-radius: 0 0 20px 20px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 10px; color: #6b7280; font-size: 14px; text-align: center;">
                                ¿Necesitas ayuda? Contáctanos en 
                                <a href="mailto:support@njoy.com" style="color: #8b5cf6; text-decoration: none;">support@njoy.com</a>
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; text-align: center;">
                                © 2024 nJoy. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        # Debug logging
        print("\n" + "="*60)
        print("📧 EMAIL SERVICE - ATTEMPTING TO SEND VERIFICATION EMAIL")
        print("="*60)
        print(f"To: {to_email}")
        print(f"User Name: {user_name}")
        print(f"Verification Token: {verification_token[:10]}...")
        print(f"Verification URL: {settings.FRONTEND_URL}/verify-email/{verification_token}")
        print(f"Email From: {settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>")
        
        # Check API key
        api_key_status = "SET" if settings.RESEND_API_KEY else "MISSING"
        api_key_preview = settings.RESEND_API_KEY[:10] + "..." if settings.RESEND_API_KEY else "None"
        print(f"API Key Status: {api_key_status} ({api_key_preview})")
        print("="*60 + "\n")
        
        try:
            params = {
                "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
                "to": [to_email],
                "subject": "✨ Verifica tu cuenta de nJoy",
                "html": html_content,
            }
            
            print("📤 Calling Resend API...")
            email = resend.Emails.send(params)
            print(f"✅ SUCCESS! Verification email sent to {to_email}")
            print(f"   Email ID: {email.get('id')}")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR SENDING EMAIL")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            print(f"   To: {to_email}")
            import traceback
            print(f"   Traceback:\n{traceback.format_exc()}")
            print("="*60 + "\n")
            return False
    
    @staticmethod
    def send_welcome_email(to_email: str, user_name: str) -> bool:
        """
        Send welcome email after successful verification (optional)
        """
        # TODO: Implement welcome email if needed
        pass
