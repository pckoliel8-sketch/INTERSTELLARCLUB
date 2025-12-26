import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import os
from pathlib import Path

# Email configuration - Load from environment or use defaults
import os
EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.gmail.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER") or "interstellarclub99@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS") or "miofeskjjleuwjam"
EMAIL_FROM = os.getenv("EMAIL_FROM") or "interstellarclub99@gmail.com"

# Check configuration
USING_PERSONAL_GMAIL = EMAIL_HOST == "smtp.gmail.com" and "gmail.com" in EMAIL_USER.lower()
UNIVERSITY_EMAIL_PATTERN = any(domain in EMAIL_FROM.lower() for domain in ['univ', 'edu', 'ac.ma', 'university'])

def test_email():
    # Test with actual French email content that would be sent from the application
    recipients = ["pckoliel8@gmail.com"]  # Test email address
    subject = "🎉 Votre demande d'inscription a été acceptée - INTERSTELLAR CLUB"

    # Use actual French email content from the application (student approval email)
    body = """Félicitations Test User !

Votre demande d'inscription a été acceptée sur la plateforme INTERSTELLAR CLUB ! 🎉

Vous pouvez désormais accéder à votre compte et bénéficier de toutes les fonctionnalités de la plateforme :
- Créer et gérer des projets
- Participer aux activités scientifiques
- Communiquer avec l'équipe

Nom d'utilisateur : testuser

Bienvenue dans notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    print("EMAIL CONFIGURATION CHECK:")
    print(f"Host: {EMAIL_HOST}")
    print(f"Port: {EMAIL_PORT}")
    print(f"User: {EMAIL_USER}")
    print(f"From: {EMAIL_FROM}")
    print(f"Using Personal Gmail: {USING_PERSONAL_GMAIL}")
    print(f"University Email Pattern: {UNIVERSITY_EMAIL_PATTERN}")
    print()

    # Check for university email restrictions
    university_emails = [email for email in recipients if any(domain in email.lower() for domain in ['univ', 'edu', 'ac.ma', 'university'])]
    if university_emails and USING_PERSONAL_GMAIL and not UNIVERSITY_EMAIL_PATTERN:
        print("WARNING: Attempting to send to university emails from personal Gmail account")
        print("This may be blocked by Gmail. Consider using university email or professional service.")
        print("University recipients:", university_emails)
        print()

    if not EMAIL_HOST or not EMAIL_USER or not EMAIL_PASS:
        print("WARNING: Email not configured - check .env file")
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        print(f"EMAIL: Attempting to send email to: {recipients}")
        print("EMAIL: Connecting to SMTP server...")

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        print("EMAIL: Starting TLS...")
        server.starttls()
        print("EMAIL: Logging in...")
        server.login(EMAIL_USER, EMAIL_PASS)
        print("EMAIL: Sending email...")
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())
        server.quit()
        print("EMAIL: Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"EMAIL ERROR: Authentication failed: {e}")
        print("TIP: For Gmail: Make sure you use App Password, not regular password")
        print("TIP: Go to https://myaccount.google.com/apppasswords")
    except smtplib.SMTPConnectError as e:
        print(f"EMAIL ERROR: Connection failed: {e}")
        print("TIP: Check your internet connection")
    except smtplib.SMTPException as e:
        error_str = str(e).lower()
        if "blocked" in error_str or "rejected" in error_str:
            print(f"EMAIL ERROR: Email blocked by Gmail: {e}")
            print("TIP: Gmail is blocking emails to university/student addresses from personal accounts")
            print("SOLUTION: Use university email or professional email service (SendGrid, Mailgun)")
            print("TIP: Create .env file with university email settings")
        elif "daily" in error_str or "limit" in error_str:
            print(f"EMAIL ERROR: Daily sending limit exceeded: {e}")
            print("TIP: Gmail daily limit exceeded. Wait 24 hours or use different account")
        else:
            print(f"EMAIL ERROR: SMTP error: {e}")
    except Exception as e:
        error_str = str(e).lower()
        if "blocked" in error_str or "rejected" in error_str or "university" in error_str:
            print(f"EMAIL ERROR: Email blocked - likely Gmail policy violation: {e}")
            print("TIP: Gmail blocks personal accounts sending to university emails")
            print("SOLUTION: Configure university email in .env file or use professional service")
        else:
            print(f"EMAIL ERROR: Unexpected error: {e}")
            print("TIP: Check your email configuration in .env file")

# Import the send_email function from main.py for comprehensive testing
def test_full_email_template():
    """Test the full HTML email template with French content"""
    print("=== TESTING FULL HTML EMAIL TEMPLATE ===")

    # Test the student approval email template
    test_body = """Félicitations Jean Dupont !

Votre demande d'inscription a été acceptée sur la plateforme INTERSTELLAR CLUB ! 🎉

Vous pouvez désormais accéder à votre compte et bénéficier de toutes les fonctionnalités de la plateforme :
- Créer et gérer des projets
- Participer aux activités scientifiques
- Communiquer avec l'équipe

Nom d'utilisateur : jeandupont

Bienvenue dans notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    # Create the HTML email manually (similar to main.py send_email function)
    msg = MIMEMultipart("related")
    msg["From"] = EMAIL_FROM
    msg["To"] = "pckoliel8@gmail.com"
    msg["Subject"] = "🎉 Test d'acceptation d'inscription - INTERSTELLAR CLUB"

    # HTML body with embedded logos - Ultra Professional Design (French version)
    html_body = f"""
    <!DOCTYPE html>
    <html lang="fr" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎉 INTERSTELLAR CLUB - Félicitations !</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: #1f2937;
            }}

            .container {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 32px 64px rgba(0, 0, 0, 0.12), 0 16px 32px rgba(0, 0, 0, 0.08);
            }}

            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                padding: 50px 40px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="60" cy="80" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="30" cy="70" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>');
                opacity: 0.3;
            }}

            .logo-section {{
                position: relative;
                z-index: 2;
            }}

            .club-title {{
                font-size: 36px;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 8px;
                text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                letter-spacing: -0.5px;
            }}

            .club-subtitle {{
                font-size: 18px;
                font-weight: 400;
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 20px;
            }}

            .success-badge {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 50px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                margin-top: 20px;
            }}

            .content {{
                padding: 60px 50px 40px;
                background: #ffffff;
            }}

            .greeting {{
                font-size: 28px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 20px;
                line-height: 1.3;
            }}

            .congratulations {{
                font-size: 20px;
                font-weight: 600;
                color: #059669;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .message {{
                font-size: 16px;
                line-height: 1.8;
                color: #4b5563;
                margin-bottom: 35px;
            }}

            .features {{
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-radius: 16px;
                padding: 30px;
                margin: 30px 0;
                border: 1px solid #e2e8f0;
            }}

            .features-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .feature-list {{
                list-style: none;
                padding: 0;
            }}

            .feature-item {{
                padding: 12px 0;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 15px;
                color: #374151;
            }}

            .feature-item:last-child {{
                border-bottom: none;
            }}

            .feature-icon {{
                width: 20px;
                height: 20px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 12px;
                flex-shrink: 0;
            }}

            .username-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin: 30px 0;
                border: 2px solid transparent;
                background-clip: padding-box;
            }}

            .username-label {{
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 8px;
                font-weight: 500;
            }}

            .username {{
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}

            .welcome-message {{
                font-size: 18px;
                font-weight: 600;
                color: #059669;
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-radius: 12px;
                border: 1px solid #a7f3d0;
            }}

            .signature {{
                text-align: center;
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #e5e7eb;
            }}

            .signature-title {{
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 5px;
            }}

            .signature-subtitle {{
                font-size: 14px;
                color: #6b7280;
            }}

            .footer {{
                background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                color: #ffffff;
                padding: 40px 50px 30px;
                text-align: center;
            }}

            .footer-content {{
                font-size: 14px;
                line-height: 1.6;
                opacity: 0.9;
            }}

            .footer-highlight {{
                color: #60a5fa;
                font-weight: 600;
            }}

            .disclaimer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 12px;
                opacity: 0.7;
            }}

            @media (max-width: 600px) {{
                .container {{
                    margin: 10px;
                    border-radius: 16px;
                }}

                .header {{
                    padding: 40px 30px 30px;
                }}

                .club-title {{
                    font-size: 28px;
                }}

                .content {{
                    padding: 40px 30px 30px;
                }}

                .greeting {{
                    font-size: 24px;
                }}

                .footer {{
                    padding: 30px 30px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 40px 20px; min-height: 100vh;">
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo-section">
                        <h1 class="club-title">🎓 INTERSTELLAR CLUB</h1>
                        <p class="club-subtitle">Club Universitaire d'Innovation Scientifique</p>
                        <div class="success-badge">✨ Félicitations !</div>
                    </div>
                </div>

                <!-- Main Content -->
                <div class="content">
                    <h2 class="greeting">Félicitations Jean Dupont !</h2>

                    <div class="congratulations">
                        🎉 Votre demande d'inscription a été acceptée !
                    </div>

                    <div class="message">
                        Vous pouvez désormais accéder à votre compte et bénéficier de toutes les fonctionnalités
                        de notre plateforme innovante dédiée à l'excellence scientifique et technique.
                    </div>

                    <div class="features">
                        <h3 class="features-title">🚀 Fonctionnalités disponibles :</h3>
                        <ul class="feature-list">
                            <li class="feature-item">
                                <span class="feature-icon">📋</span>
                                Créer et gérer des projets innovants
                            </li>
                            <li class="feature-item">
                                <span class="feature-icon">🔬</span>
                                Participer aux activités scientifiques
                            </li>
                            <li class="feature-item">
                                <span class="feature-icon">👥</span>
                                Collaborer avec l'équipe technique
                            </li>
                            <li class="feature-item">
                                <span class="feature-icon">📚</span>
                                Accéder aux ressources pédagogiques
                            </li>
                        </ul>
                    </div>

                    <div class="username-box">
                        <div class="username-label">Votre nom d'utilisateur :</div>
                        <div class="username">jeandupont</div>
                    </div>

                    <div class="welcome-message">
                        🌟 Bienvenue dans notre communauté scientifique d'excellence !
                    </div>

                    <div class="signature">
                        <div class="signature-title">Cordialement,</div>
                        <div class="signature-subtitle">L'équipe INTERSTELLAR CLUB</div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <div class="footer-content">
                        <p>
                            <strong class="footer-highlight">INTERSTELLAR CLUB</strong><br>
                            Club Universitaire d'Innovation Scientifique
                        </p>
                        <p style="margin-top: 15px; font-size: 13px;">
                            Cet email a été envoyé automatiquement depuis notre plateforme.<br>
                            Pour toute question, contactez-nous à l'adresse universitaire.
                        </p>

                        <div class="disclaimer">
                            🔒 Cet email contient des informations confidentielles.<br>
                            INTERSTELLAR CLUB - Tous droits réservés © 2025
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Attach HTML content
    from email.mime.text import MIMEText
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(html_part)

    # Try to attach logos if they exist
    logo_paths = ["static/logo.png", "static/logo1.png"]
    logo_cids = ["logo_main", "logo_secondary"]

    for i, logo_path in enumerate(logo_paths):
        try:
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_part = MIMEImage(f.read())
                    logo_part.add_header('Content-ID', f'<{logo_cids[i]}>')
                    logo_part.add_header('Content-Disposition', 'inline')
                    msg.attach(logo_part)
                    print(f"Logo {logo_path} attached successfully")
        except Exception as e:
            print(f"Logo attachment failed ({logo_path}): {e}")

    try:
        print("EMAIL: Attempting to send HTML email with French content...")
        print("EMAIL: Connecting to SMTP server...")

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        print("EMAIL: Starting TLS...")
        server.starttls()
        print("EMAIL: Logging in...")
        server.login(EMAIL_USER, EMAIL_PASS)
        print("EMAIL: Sending HTML email...")
        server.sendmail(EMAIL_FROM, ["pckoliel8@gmail.com"], msg.as_string())
        server.quit()
        print("EMAIL: HTML email with French content sent successfully!")

    except Exception as e:
        print(f"EMAIL ERROR: {e}")

def send_beautiful_email_test():
    """Test sending a beautiful, professional HTML email"""
    print("=== TESTING BEAUTIFUL PROFESSIONAL HTML EMAIL ===")

    # Create a stunning professional email
    msg = MIMEMultipart("related")
    msg["From"] = EMAIL_FROM
    msg["To"] = "pckoliel8@gmail.com"
    msg["Subject"] = "🎉 Bienvenue chez INTERSTELLAR CLUB - Félicitations !"

    # Ultra-modern and beautiful HTML template
    beautiful_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎉 INTERSTELLAR CLUB - Bienvenue !</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .email-container {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 40px 80px rgba(0, 0, 0, 0.15);
            }}

            .hero-section {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                padding: 60px 40px;
                text-align: center;
                position: relative;
            }}

            .hero-section::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="stars" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="5" cy="15" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23stars)"/></svg>');
                opacity: 0.6;
            }}

            .hero-content {{
                position: relative;
                z-index: 2;
            }}

            .main-title {{
                font-size: 42px;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 10px;
                text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                letter-spacing: -1px;
            }}

            .subtitle {{
                font-size: 20px;
                font-weight: 400;
                color: rgba(255, 255, 255, 0.95);
                margin-bottom: 30px;
            }}

            .celebration-badge {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 50px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            }}

            .content-section {{
                padding: 50px 40px;
                background: #ffffff;
            }}

            .welcome-title {{
                font-size: 32px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 15px;
                line-height: 1.2;
            }}

            .success-message {{
                font-size: 22px;
                font-weight: 600;
                color: #059669;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .description {{
                font-size: 16px;
                line-height: 1.7;
                color: #4b5563;
                margin-bottom: 35px;
            }}

            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 35px 0;
            }}

            .feature-card {{
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                transition: transform 0.3s ease;
            }}

            .feature-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
            }}

            .feature-icon {{
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 15px;
                font-size: 24px;
                box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
            }}

            .feature-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 8px;
            }}

            .feature-description {{
                font-size: 14px;
                color: #6b7280;
                line-height: 1.5;
            }}

            .credentials-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                margin: 35px 0;
                color: white;
                position: relative;
                overflow: hidden;
            }}

            .credentials-box::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
            }}

            .credentials-content {{
                position: relative;
                z-index: 2;
            }}

            .credentials-title {{
                font-size: 16px;
                opacity: 0.9;
                margin-bottom: 10px;
                font-weight: 500;
            }}

            .username {{
                font-size: 20px;
                font-weight: 700;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }}

            .password-hint {{
                font-size: 14px;
                opacity: 0.8;
            }}

            .welcome-banner {{
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 2px solid #a7f3d0;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                margin: 35px 0;
            }}

            .welcome-text {{
                font-size: 20px;
                font-weight: 600;
                color: #065f46;
                margin-bottom: 10px;
            }}

            .community-description {{
                font-size: 16px;
                color: #047857;
                line-height: 1.6;
            }}

            .signature {{
                text-align: center;
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #e5e7eb;
            }}

            .signature-name {{
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 5px;
            }}

            .signature-role {{
                font-size: 14px;
                color: #6b7280;
            }}

            .footer {{
                background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                padding: 40px 40px 30px;
                text-align: center;
                color: #ffffff;
            }}

            .footer-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            }}

            .footer-subtitle {{
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 20px;
            }}

            .contact-info {{
                font-size: 14px;
                line-height: 1.6;
                opacity: 0.8;
            }}

            .social-links {{
                margin: 25px 0;
            }}

            .social-button {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 50px;
                padding: 12px 20px;
                margin: 0 5px;
                color: #ffffff;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
            }}

            .social-button:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }}

            .disclaimer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 12px;
                opacity: 0.6;
                line-height: 1.5;
            }}

            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 16px;
                }}

                .hero-section {{
                    padding: 40px 30px;
                }}

                .main-title {{
                    font-size: 32px;
                }}

                .content-section {{
                    padding: 30px 25px;
                }}

                .welcome-title {{
                    font-size: 26px;
                }}

                .features-grid {{
                    grid-template-columns: 1fr;
                }}

                .footer {{
                    padding: 30px 25px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Hero Section -->
            <div class="hero-section">
                <div class="hero-content">
                    <h1 class="main-title">🎓 INTERSTELLAR CLUB</h1>
                    <p class="subtitle">Club Universitaire d'Innovation Scientifique</p>
                    <div class="celebration-badge">✨ Félicitations - Bienvenue !</div>
                </div>
            </div>

            <!-- Content Section -->
            <div class="content-section">
                <h2 class="welcome-title">Félicitations Jean Dupont !</h2>

                <div class="success-message">
                    🎉 Votre inscription a été approuvée avec succès !
                </div>

                <p class="description">
                    Vous faites désormais partie de notre prestigieuse communauté scientifique.
                    Découvrez toutes les possibilités qui s'offrent à vous pour innover et exceller
                    dans le domaine scientifique et technique.
                </p>

                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🚀</div>
                        <h3 class="feature-title">Projets Innovants</h3>
                        <p class="feature-description">
                            Créez et participez à des projets technologiques de pointe
                        </p>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🔬</div>
                        <p class="feature-description">
                            Accédez à des équipements et ressources scientifiques avancées
                        </p>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">👥</div>
                        <h3 class="feature-title">Collaboration</h3>
                        <p class="feature-description">
                            Travaillez avec des experts et des passionnés de la science
                        </p>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">📚</div>
                        <h3 class="feature-title">Formation</h3>
                        <p class="feature-description">
                            Bénéficiez de formations spécialisées et d'ateliers pratiques
                        </p>
                    </div>
                </div>

                <div class="credentials-box">
                    <div class="credentials-content">
                        <div class="credentials-title">Vos identifiants de connexion :</div>
                        <div class="username">📧 jeandupont@university.edu</div>
                        <div class="password-hint">Mot de passe : envoyé séparément pour sécurité</div>
                    </div>
                </div>

                <div class="welcome-banner">
                    <div class="welcome-text">🌟 Bienvenue dans l'excellence scientifique !</div>
                    <p class="community-description">
                        Rejoignez une communauté dynamique d'étudiants et de chercheurs
                        passionnés par l'innovation et la découverte scientifique.
                    </p>
                </div>

                <div class="signature">
                    <div class="signature-name">Cordialement,</div>
                    <div class="signature-role">L'équipe INTERSTELLAR CLUB</div>
                    <div style="margin-top: 15px; font-size: 12px; color: #9ca3af;">
                        Club Universitaire d'Innovation Scientifique<br>
                        Université [Votre Université] - 2025
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-title">INTERSTELLAR CLUB</div>
                <div class="footer-subtitle">Club Universitaire d'Innovation Scientifique</div>

                <div class="contact-info">
                    Pour toute question ou assistance, n'hésitez pas à nous contacter.<br>
                    Cet email a été envoyé automatiquement depuis notre plateforme sécurisée.
                </div>

                <div class="social-links">
                    <a href="#" class="social-button">🌐 Site Web</a>
                    <a href="#" class="social-button">📧 Contact</a>
                    <a href="#" class="social-button">📱 Réseaux Sociaux</a>
                </div>

                <div class="disclaimer">
                    🔒 Cet email contient des informations confidentielles destinées uniquement à son destinataire.<br>
                    Si vous n'êtes pas le destinataire prévu, merci de le supprimer immédiatement.<br>
                    INTERSTELLAR CLUB - Tous droits réservés © 2025
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Attach HTML content
    from email.mime.text import MIMEText
    html_part = MIMEText(beautiful_html, "html", "utf-8")
    msg.attach(html_part)

    # Try to attach logos
    logo_paths = ["static/logo.png", "static/logo1.png"]
    logo_cids = ["logo_main", "logo_secondary"]

    for i, logo_path in enumerate(logo_paths):
        try:
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_part = MIMEImage(f.read())
                    logo_part.add_header('Content-ID', f'<{logo_cids[i]}>')
                    logo_part.add_header('Content-Disposition', 'inline')
                    msg.attach(logo_part)
                    print(f"Logo {logo_path} attached successfully")
        except Exception as e:
            print(f"Logo attachment failed ({logo_path}): {e}")

    try:
        print("Sending beautiful professional HTML email...")
        print("Connecting to SMTP server...")

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(EMAIL_USER, EMAIL_PASS)
        print("Sending beautiful email...")
        server.sendmail(EMAIL_FROM, ["pckoliel8@gmail.com"], msg.as_string())
        server.quit()
        print("Beautiful professional HTML email sent successfully!")

    except Exception as e:
        print(f"EMAIL ERROR: {e}")

def test_all_email_types():
    """Test all types of emails that the system sends"""
    print("=== TESTING ALL EMAIL TYPES WITH BEAUTIFUL TEMPLATES ===")

    # Test student registration notification to professors
    print("1. Testing student registration notification to professors...")
    professor_notification_body = """Nouvelle demande d'inscription d'étudiant:

Nom: Ahmed Mohamed
Nom d'utilisateur: ahmedmohamed
Email: ahmed.mohamed@university.edu
Numéro de téléphone: +212 6 12 34 56 78
Genre: Masculin
Numéro de carte d'étudiant: STU2024001
Lieu de naissance: Casablanca
Date de naissance: 2000-05-15
Chemin de l'image de la carte: uploads/student_cards/timestamp_card.jpg

Pour approuver: http://localhost:8000/students/1/approve
Pour refuser: http://localhost:8000/students/1/reject"""

    test_email_with_type("pckoliel8@gmail.com", "Nouvelle demande d'inscription d'étudiant", professor_notification_body, "notification")
    print()

    # Test student confirmation email
    print("2. Testing student confirmation email...")
    confirmation_body = """Bonjour Ahmed Mohamed,

Votre demande d'inscription a été enregistrée avec succès sur la plateforme INTERSTELLAR CLUB !

Informations d'inscription :
- Nom d'utilisateur : ahmedmohamed
- Adresse e-mail : ahmed.mohamed@university.edu

Votre demande est en cours de révision par les professeurs. Vous recevrez une notification lorsque votre demande sera traitée.

Merci de rejoindre notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    test_email_with_type("pckoliel8@gmail.com", "Confirmation de votre demande d'inscription - INTERSTELLAR CLUB", confirmation_body, "confirmation")
    print()

    # Test professor welcome email
    print("3. Testing professor welcome email...")
    professor_body = """Bonjour Professeur Sarah Johnson,

Vous avez été enregistré avec succès en tant que professeur sur la plateforme INTERSTELLAR CLUB ! 🎓

Informations de connexion :
- Nom d'utilisateur : sarahjohnson
- Adresse e-mail : sarah.johnson@university.edu

En tant que professeur, vous pouvez désormais :
- Réviser les demandes d'inscription des étudiants
- Approuver ou refuser les demandes d'inscription
- Créer et gérer des projets
- Superviser les activités des étudiants
- Accéder à tous les outils de la plateforme

Bienvenue dans notre équipe éducative !

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    test_email_with_type("pckoliel8@gmail.com", "🎓 Vous avez été enregistré en tant que professeur - INTERSTELLAR CLUB", professor_body, "welcome")
    print()

    # Test student approval email
    print("4. Testing student approval email...")
    approval_body = """Félicitations Ahmed Mohamed !

Votre demande d'inscription a été acceptée sur la plateforme INTERSTELLAR CLUB ! 🎉

Vous pouvez désormais accéder à votre compte et bénéficier de toutes les fonctionnalités de la plateforme :
- Créer et gérer des projets
- Participer aux activités scientifiques
- Communiquer avec l'équipe

Nom d'utilisateur : ahmedmohamed

Bienvenue dans notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    test_email_with_type("pckoliel8@gmail.com", "🎉 Votre demande d'inscription a été acceptée - INTERSTELLAR CLUB", approval_body, "acceptance")
    print()

    # Test student rejection email
    print("5. Testing student rejection email...")
    rejection_body = """Cher/Chère Ahmed Mohamed,

Nous regrettons de ne pas pouvoir accepter votre demande d'inscription sur la plateforme INTERSTELLAR CLUB pour le moment.

Vous pouvez :
1. Réviser les informations fournies et vous assurer de leur exactitude
2. Contacter les professeurs pour obtenir des conseils
3. Réessayer ultérieurement

Nous vous remercions pour votre intérêt à rejoindre notre communauté scientifique.

Cordialement,
L'équipe INTERSTELLAR CLUB"""

    test_email_with_type("pckoliel8@gmail.com", "Demande d'inscription - INTERSTELLAR CLUB", rejection_body, "rejection")

def test_email_with_type(recipient, subject, body, email_type):
    """Test email with specific type using the main.py send_email function"""
    try:
        # Import the function from main.py
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        # We'll simulate the email creation and sending
        msg = MIMEMultipart("related")
        msg["From"] = EMAIL_FROM
        msg["To"] = recipient
        msg["Subject"] = subject

        # Use the beautiful template from main.py
        # Since we can't import it directly, we'll create a simplified version
        beautiful_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>INTERSTELLAR CLUB - {subject}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); min-height: 100vh; padding: 20px; }}
                .email-container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 40px 80px rgba(0, 0, 0, 0.15); }}
                .hero-section {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 60px 40px; text-align: center; position: relative; }}
                .hero-content {{ position: relative; z-index: 2; }}
                .club-title {{ font-size: 42px; font-weight: 800; color: #ffffff; margin-bottom: 10px; text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); letter-spacing: -1px; }}
                .club-subtitle {{ font-size: 20px; font-weight: 400; color: rgba(255, 255, 255, 0.95); margin-bottom: 30px; }}
                .celebration-badge {{ display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 50px; padding: 15px 30px; font-size: 16px; font-weight: 600; color: #ffffff; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }}
                .content-section {{ padding: 50px 40px; background: #ffffff; }}
                .message-content {{ font-size: 16px; line-height: 1.7; color: #4b5563; white-space: pre-line; }}
                .signature {{ text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #e5e7eb; }}
                .signature-name {{ font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 5px; }}
                .signature-role {{ font-size: 14px; color: #6b7280; }}
                .footer {{ background: linear-gradient(135deg, #1f2937 0%, #374151 100%); padding: 40px 40px 30px; text-align: center; color: #ffffff; }}
                .footer-title {{ font-size: 18px; font-weight: 600; margin-bottom: 10px; }}
                .footer-subtitle {{ font-size: 14px; opacity: 0.9; margin-bottom: 20px; }}
                .contact-info {{ font-size: 14px; line-height: 1.6; opacity: 0.8; }}
                .disclaimer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1); font-size: 12px; opacity: 0.6; line-height: 1.5; }}
                @media (max-width: 600px) {{ .email-container {{ margin: 10px; border-radius: 16px; }} .hero-section {{ padding: 40px 30px; }} .club-title {{ font-size: 32px; }} .content-section {{ padding: 30px 25px; }} .footer {{ padding: 30px 25px 20px; }} }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="hero-section">
                    <div class="hero-content">
                        <h1 class="club-title">🎓 INTERSTELLAR CLUB</h1>
                        <p class="club-subtitle">Club Universitaire d'Innovation Scientifique</p>
                        <div class="celebration-badge">{get_badge_text(email_type)}</div>
                    </div>
                </div>
                <div class="content-section">
                    <div class="message-content">{body}</div>
                    <div class="signature">
                        <div class="signature-name">Cordialement,</div>
                        <div class="signature-role">L'équipe INTERSTELLAR CLUB</div>
                    </div>
                </div>
                <div class="footer">
                    <div class="footer-title">INTERSTELLAR CLUB</div>
                    <div class="footer-subtitle">Club Universitaire d'Innovation Scientifique</div>
                    <div class="contact-info">Cet email a été envoyé automatiquement depuis notre plateforme.<br>Pour toute question, contactez-nous à l'adresse universitaire.</div>
                    <div class="disclaimer">🔒 Cet email contient des informations confidentielles.<br>INTERSTELLAR CLUB - Tous droits réservés © 2025</div>
                </div>
            </div>
        </body>
        </html>
        """

        # Attach HTML content
        from email.mime.text import MIMEText
        html_part = MIMEText(beautiful_html, "html", "utf-8")
        msg.attach(html_part)

        # Attach logos
        logo_paths = ["static/logo.png", "static/logo1.png"]
        logo_cids = ["logo_main", "logo_secondary"]

        for i, logo_path in enumerate(logo_paths):
            try:
                if os.path.exists(logo_path):
                    with open(logo_path, "rb") as f:
                        logo_part = MIMEImage(f.read())
                        logo_part.add_header('Content-ID', f'<{logo_cids[i]}>')
                        logo_part.add_header('Content-Disposition', 'inline')
                        msg.attach(logo_part)
            except Exception as e:
                pass

        # Send the email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, [recipient], msg.as_string())
        server.quit()

        print(f"✓ {email_type.upper()} email sent successfully!")

    except Exception as e:
        print(f"Failed to send {email_type} email: {e}")

def get_badge_text(email_type):
    """Get appropriate badge text based on email type"""
    badges = {
        "acceptance": "✨ Félicitations !",
        "rejection": "ℹ️ Information",
        "confirmation": "📧 Confirmation",
        "welcome": "🎓 Bienvenue !",
        "notification": "📋 Notification"
    }
    return badges.get(email_type, "💫 Message")

if __name__ == "__main__":
    print("Testing basic email...")
    test_email()
    print("\n" + "="*50 + "\n")
    print("Testing full HTML email template...")
    test_full_email_template()
    print("\n" + "="*50 + "\n")
    print("Testing BEAUTIFUL professional email...")
    send_beautiful_email_test()
    print("\n" + "="*50 + "\n")
    print("Testing ALL EMAIL TYPES with beautiful templates...")
    test_all_email_types()
