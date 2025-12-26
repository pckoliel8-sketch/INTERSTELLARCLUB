from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import jinja2
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from passlib.context import CryptContext
import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from pathlib import Path

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./apmes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    gender = Column(String)
    student_id_number = Column(String)
    birth_place = Column(String)
    birth_date = Column(DateTime)
    student_card_image = Column(String)
    specialty = Column(String)
    profile_image = Column(String)  # مسار الصورة الشخصية
    approval_status = Column(String, default="approved")  # approved | pending | rejected
    approval_by_id = Column(Integer, ForeignKey("users.id"))
    approval_decision_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    approver = relationship("User", remote_side=[id], foreign_keys=[approval_by_id])

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    mission_objective = Column(Text)
    success_criteria = Column(Text)
    manager_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, default="Active")
    overall_progress = Column(Integer, default=0)  # 0-100%
    created_at = Column(DateTime, default=datetime.utcnow)
    
    phases = relationship("Phase", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")

class Phase(Base):
    __tablename__ = "phases"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    status = Column(String, default="Not Started")
    responsible = Column(String)
    validation = Column(String, default="Pending")
    notes = Column(Text)
    completed_date = Column(DateTime)
    
    project = relationship("Project", back_populates="phases")

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    description = Column(Text)
    probability = Column(String)
    severity = Column(String)
    mitigation = Column(Text)
    status = Column(String, default="Open")
    
    project = relationship("Project", back_populates="risks")

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)
    responsibilities = Column(Text)
    progress = Column(Integer, default=0)  # 0, 25, 50, 75, 100
    added_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="team_members")
    user = relationship("User")

class ProjectFile(Base):
    __tablename__ = "project_files"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    original_filename = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    
    project = relationship("Project", back_populates="files")
    uploader = relationship("User")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="messages")
    user = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)

# Ensure new user columns exist when running against an old database
def ensure_user_columns():
    with engine.begin() as conn:
        existing_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)").all()}
        columns_to_add = [
            ("first_name", "TEXT"),
            ("last_name", "TEXT"),
            ("phone_number", "TEXT"),
            ("gender", "TEXT"),
            ("student_id_number", "TEXT"),
            ("birth_place", "TEXT"),
            ("birth_date", "DATETIME"),
            ("student_card_image", "TEXT"),
            ("specialty", "TEXT"),
            ("profile_image", "TEXT"),
            ("approval_status", "TEXT"),
            ("approval_by_id", "INTEGER"),
            ("approval_decision_at", "DATETIME"),
        ]
        for col_name, ddl in columns_to_add:
            if col_name not in existing_cols:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col_name} {ddl}")
        # Backfill approval_status as approved for existing records
        if "approval_status" not in existing_cols:
            conn.exec_driver_sql("UPDATE users SET approval_status = 'approved' WHERE approval_status IS NULL")

ensure_user_columns()

# FastAPI App
app = FastAPI(title="INTERSTELLAR CLUB")

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Configure Jinja2 with UTF-8 encoding
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates", encoding='utf-8'),
    autoescape=True
)
templates = Jinja2Templates(directory="templates")
templates.env = jinja2_env

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Email config (supports .env file without extra deps)
def load_env_file(path: str = ".env"):
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())

load_env_file()

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.gmail.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER") or "interstellarclub99@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS") or "miofeskjjleuwjam"
EMAIL_FROM = os.getenv("EMAIL_FROM") or "interstellarclub99@gmail.com"

# Check for university email restrictions
USING_PERSONAL_GMAIL = EMAIL_HOST == "smtp.gmail.com" and "gmail.com" in EMAIL_USER.lower()
UNIVERSITY_EMAIL_PATTERN = any(domain in EMAIL_FROM.lower() for domain in ['univ', 'edu', 'ac.ma', 'university'])

def check_email_configuration():
    """Check email configuration and provide recommendations"""
    issues = []

    if USING_PERSONAL_GMAIL and not UNIVERSITY_EMAIL_PATTERN:
        issues.append("WARNING: Using personal Gmail account without university email pattern")
        issues.append("Gmail may block emails to university addresses from personal accounts")
        issues.append("RECOMMENDATION: Use university email or professional email service")

    if not EMAIL_HOST or not EMAIL_USER or not EMAIL_PASS:
        issues.append("Email not fully configured - check .env file")

    if issues:
        print("EMAIL CONFIGURATION CHECK:")
        for issue in issues:
            print(f"  - {issue}")
        print()

check_email_configuration()

# For Gmail SMTP testing (uncomment and configure):
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USER = "your-email@gmail.com"
# EMAIL_PASS = "your-app-password"
# EMAIL_FROM = "interstellar.club@university.edu"

# Alternative Gmail settings (try these if the above doesn't work):
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 465  # SSL port instead of TLS
# EMAIL_USER = "interstellarclub99@gmail.com"
# EMAIL_PASS = "miofeskjjleuwjam"
# EMAIL_FROM = "interstellarclub99@gmail.com"

# For SSL connection instead of TLS (alternative method):
# import smtplib
# server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
# server.login(EMAIL_USER, EMAIL_PASS)

def create_beautiful_email_html(subject, body, email_type="general"):
    """Create a beautiful HTML email template based on email type"""

    # Determine styling based on email type
    if "accept" in email_type.lower() or "approuv" in email_type.lower() or "félicitations" in email_type.lower():
        hero_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
        accent_color = "#667eea"
        badge_text = "✨ Félicitations !"
        title_emoji = "🎉"
    elif "reject" in email_type.lower() or "refus" in email_type.lower():
        hero_gradient = "linear-gradient(135deg, #ff6b6b 0%, #ee5a52 50%, #f093fb 100%)"
        accent_color = "#ee5a52"
        badge_text = "ℹ️ Information"
        title_emoji = "📋"
    elif "verification" in email_type.lower() or "code" in email_type.lower():
        hero_gradient = "linear-gradient(135deg, #4ecdc4 0%, #44a08d 50%, #096e5c 100%)"
        accent_color = "#4ecdc4"
        badge_text = "🔐 Vérification"
        title_emoji = "🔑"
    else:
        hero_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
        accent_color = "#667eea"
        badge_text = "📧 Message"
        title_emoji = "💫"

    beautiful_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title_emoji} INTERSTELLAR CLUB - {subject.replace('🎉', '').replace('📧', '').strip()}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
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
                background: {hero_gradient};
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

            .logo-section {{
                margin-bottom: 30px;
            }}

            .club-title {{
                font-size: 42px;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 10px;
                text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                letter-spacing: -1px;
            }}

            .club-subtitle {{
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

            .message-content {{
                font-size: 16px;
                line-height: 1.7;
                color: #4b5563;
                white-space: pre-line;
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

                .club-title {{
                    font-size: 32px;
                }}

                .content-section {{
                    padding: 30px 25px;
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
                    <div class="logo-section">
                        <img src="cid:logo_main" alt="INTERSTELLAR CLUB" style="height: 70px; margin: 0 15px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                        <img src="cid:logo_secondary" alt="Second Logo" style="height: 55px; margin: 0 15px; border-radius: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    </div>
                    <h1 class="club-title">{title_emoji} INTERSTELLAR CLUB</h1>
                    <p class="club-subtitle">Club Universitaire d'Innovation Scientifique</p>
                    <div class="celebration-badge">{badge_text}</div>
                </div>
            </div>

            <!-- Content Section -->
            <div class="content-section">
                <div class="message-content">
                    {body}
                </div>

                <div class="signature">
                    <div class="signature-name">Cordialement,</div>
                    <div class="signature-role">L'équipe INTERSTELLAR CLUB</div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-title">INTERSTELLAR CLUB</div>
                <div class="footer-subtitle">Club Universitaire d'Innovation Scientifique</div>

                <div class="contact-info">
                    Cet email a été envoyé automatiquement depuis notre plateforme.<br>
                    Pour toute question, contactez-nous à l'adresse universitaire.
                </div>

                <div class="disclaimer">
                    🔒 Cet email contient des informations confidentielles.<br>
                    INTERSTELLAR CLUB - Tous droits réservés © 2025
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return beautiful_html

def send_email(recipients, subject, body, attachments=None, email_type="general"):
    """Send a plain text email with INTERSTELLAR CLUB logos; logs to console if SMTP not configured."""
    if isinstance(recipients, str):
        recipients = [recipients]
    if not recipients:
        return

    # Check for university email restrictions
    university_emails = [email for email in recipients if any(domain in email.lower() for domain in ['univ', 'edu', 'ac.ma', 'university'])]
    if university_emails and USING_PERSONAL_GMAIL and not UNIVERSITY_EMAIL_PATTERN:
        print("WARNING: Attempting to send to university emails from personal Gmail account")
        print("This may be blocked by Gmail. Consider using university email or professional service.")
        print("University recipients:", university_emails)

    if not EMAIL_HOST or not EMAIL_USER or not EMAIL_PASS:
        # Fallback: log to console
        print("WARNING: Email not sent (SMTP not configured). To:", recipients)
        print("Subject:", subject)
        print("Body:\n", body)
        return

    # Create HTML email with embedded logos
    msg = MIMEMultipart("related")
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # Use the beautiful HTML template
    html_body = create_beautiful_email_html(subject, body, email_type)

    # Attach HTML content
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(html_part)

    # Attach logos as inline images
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
            print(f"Logo attachment failed ({logo_path}):", e)

    # Attach additional files if provided
    attachments = attachments or []
    for path in attachments:
        try:
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)
        except Exception as e:
            print(f"Attachment failed ({path}):", e)

    try:
        print(f"EMAIL: Attempting to send email to: {recipients}")
        print(f"EMAIL: Subject: {subject}")

        # Send via Gmail - Try TLS first, then SSL if it fails
        print("EMAIL: Connecting to SMTP server...")
        success = False

        # Try TLS first (port 587)
        if EMAIL_PORT == 587:
            try:
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
                print("EMAIL: Starting TLS...")
                server.starttls()
                print("EMAIL: Logging in...")
                server.login(EMAIL_USER, EMAIL_PASS)
                print("EMAIL: Sending email...")
                server.sendmail(EMAIL_FROM, recipients, msg.as_string())
                server.quit()
                print("EMAIL: Email sent successfully!")
                success = True
            except Exception as tls_error:
                print(f"EMAIL: TLS failed, trying SSL: {tls_error}")
                success = False

        # If TLS failed or using SSL port, try SSL (port 465)
        if not success:
            try:
                print("EMAIL: Trying SSL connection...")
                server = smtplib.SMTP_SSL(EMAIL_HOST, 465, timeout=10)
                print("EMAIL: Logging in...")
                server.login(EMAIL_USER, EMAIL_PASS)
                print("EMAIL: Sending email...")
                server.sendmail(EMAIL_FROM, recipients, msg.as_string())
                server.quit()
                print("EMAIL: Email sent successfully!")
                success = True
            except Exception as ssl_error:
                print(f"EMAIL: SSL also failed: {ssl_error}")
                raise ssl_error

        if not success:
            raise Exception("Both TLS and SSL failed")

    except smtplib.SMTPAuthenticationError as e:
        print(f"EMAIL ERROR: Authentication failed: {e}")
        print("TIP: For Gmail: Make sure you use App Password, not regular password")
        print("TIP: Generate App Password at: https://myaccount.google.com/apppasswords")
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

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple session management
current_user_id = None

# Verification codes storage (temporary - in production use database)
current_user_verification_codes = {}

def get_current_user(db: Session):
    if not current_user_id:
        return None
    return db.query(User).filter(User.id == current_user_id).first()

def require_prof_or_admin(user: User):
    return user and user.role in ["Professor", "Admin"]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    global current_user_id
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        # Block login for students not yet approved
        if user.role.lower() == "student":
            if user.approval_status == "pending":
                return RedirectResponse(url="/?error=pending", status_code=303)
            if user.approval_status == "rejected":
                return RedirectResponse(url="/?error=rejected", status_code=303)
        current_user_id = user.id
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/?error=1", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    first_name: str = Form(default=None),
    last_name: str = Form(default=None),
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(default=None),
    password: str = Form(...),
    role: str = Form(...),
    gender: str = Form(default=None),
    student_id_number: str = Form(default=None),
    birth_place: str = Form(default=None),
    birth_date: str = Form(default=None),
    student_card: UploadFile = File(default=None),
    accept_rules: str = Form(default=None),
    verification_code: str = Form(default=None),
    specialty: str = Form(default=None),
    db: Session = Depends(get_db)
):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    is_student = role.lower() == "student"

    # Check if user accepted the rules
    if not accept_rules:
        return RedirectResponse(url="/register?error=accept_rules", status_code=303)

    # Check professor email format and verification code
    is_professor = role.lower() == "professor"
    if is_professor:
        if not email or "univ" not in email.lower():
            return RedirectResponse(url="/register?error=invalid_prof_email", status_code=303)

        # Check verification code for professors
        if not verification_code:
            return RedirectResponse(url="/register?error=missing_verification_code", status_code=303)

        # Verify the code (this would normally check against a stored code)
        # For now, we'll use a simple session-based approach
        stored_code = current_user_verification_codes.get(email, {}).get('code')
        code_timestamp = current_user_verification_codes.get(email, {}).get('timestamp')

        if not stored_code or stored_code != verification_code:
            return RedirectResponse(url="/register?error=invalid_verification_code", status_code=303)

        # Check if code is expired (10 minutes)
        if code_timestamp and (datetime.utcnow() - code_timestamp).seconds > 600:
            return RedirectResponse(url="/register?error=expired_verification_code", status_code=303)

        # Clear the used code
        if email in current_user_verification_codes:
            del current_user_verification_codes[email]

    # Check duplicates early to avoid IntegrityError
    existing_username = db.query(User).filter(User.username == username).first()
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_username or existing_email:
        return RedirectResponse(url="/register?error=duplicate", status_code=303)

    if is_student:
        required_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "student_id_number": student_id_number,
            "birth_place": birth_place,
            "birth_date": birth_date,
            "student_card": student_card,
            "specialty": specialty,
        }
        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            return RedirectResponse(url="/register?error=missing_fields", status_code=303)

    card_path = None
    if is_student and student_card and student_card.filename:
        allowed_card_ext = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        file_ext = os.path.splitext(student_card.filename)[1].lower()
        if file_ext not in allowed_card_ext:
            return RedirectResponse(url="/register?error=invalid_card", status_code=303)

        card_dir = "uploads/student_cards"
        os.makedirs(card_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{student_card.filename}"
        card_path = os.path.join(card_dir, safe_name)
        with open(card_path, "wb") as buffer:
            shutil.copyfileobj(student_card.file, buffer)

    birth_date_value = None
    if birth_date:
        try:
            birth_date_value = datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            birth_date_value = None

    hashed_password = pwd_context.hash(password)
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        phone_number=phone_number,
        hashed_password=hashed_password,
        role=role,
        gender=gender,
        student_id_number=student_id_number if is_student else None,
        birth_place=birth_place,
        birth_date=birth_date_value,
        student_card_image=card_path if is_student else None,
        specialty=specialty,
        approval_status="pending" if is_student else "approved",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(url="/register?error=duplicate", status_code=303)

    # Notify professors of new student registration
    if is_student:
        profs = db.query(User).filter(User.role == "Professor").all()
        prof_emails = [p.email for p in profs if p.email]
        student_info = [
            f"Nom: {first_name} {last_name}",
            f"Nom d'utilisateur: {username}",
            f"Email: {email}",
            f"Numéro de téléphone: {phone_number or 'Non spécifié'}",
            f"Genre: {gender}",
            f"Numéro de carte d'étudiant: {student_id_number}",
            f"Lieu de naissance: {birth_place}",
            f"Date de naissance: {birth_date}",
            f"Chemin de l'image de la carte: {card_path or 'Non attachée'}",
        ]
        # Get base URL from environment or use default
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        body = "Nouvelle demande d'inscription d'étudiant:\n" + "\n".join(student_info) + f"\n\nPour approuver: {base_url}/students/{user.id}/approve\nPour refuser: {base_url}/students/{user.id}/reject"
        send_email(prof_emails, "Nouvelle demande d'inscription d'étudiant", body, attachments=[card_path] if card_path else None, email_type="notification")

        # Send confirmation email to student
        if email:
            confirmation_body = f"""Bonjour {first_name} {last_name},

Votre demande d'inscription a été enregistrée avec succès sur la plateforme INTERSTELLAR CLUB !

Informations d'inscription :
- Nom d'utilisateur : {username}
- Adresse e-mail : {email}

Votre demande est en cours de révision par les professeurs. Vous recevrez une notification lorsque votre demande sera traitée.

Merci de rejoindre notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""
            send_email(email, "Confirmation de votre demande d'inscription - INTERSTELLAR CLUB", confirmation_body, email_type="confirmation")
    else:
        # Welcome email for professor
        if email:
            professor_welcome_body = f"""Bonjour Professeur {first_name} {last_name},

Vous avez été enregistré avec succès en tant que professeur sur la plateforme INTERSTELLAR CLUB ! 🎓

Informations de connexion :
- Nom d'utilisateur : {username}
- Adresse e-mail : {email}

En tant que professeur, vous pouvez désormais :
- Réviser les demandes d'inscription des étudiants
- Approuver ou refuser les demandes d'inscription
- Créer et gérer des projets
- Superviser les activités des étudiants
- Accéder à tous les outils de la plateforme

Bienvenue dans notre équipe éducative !

Cordialement,
L'équipe INTERSTELLAR CLUB"""
            send_email(email, "🎓 Vous avez été enregistré en tant que professeur - INTERSTELLAR CLUB", professor_welcome_body, email_type="welcome")

    return RedirectResponse(url="/", status_code=303)

@app.get("/club-card")
async def club_card(request: Request, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)

    user = get_current_user(db)

    # Only approved students can see their club card
    if user.role.lower() != "student" or user.approval_status != "approved":
        return RedirectResponse(url="/dashboard", status_code=303)

    # Generate card number (format: YYYY + random 4 digits)
    current_year = datetime.utcnow().year
    card_number = f"{current_year}{user.id:04d}"

    # Academic year
    academic_year = f"{current_year}/{current_year + 1}"

    return templates.TemplateResponse("club_card.html", {
        "request": request,
        "user": user,
        "card_number": card_number,
        "academic_year": academic_year
    })

@app.post("/send-verification-code")
async def send_verification_code(email: str = Form(...)):
    """Send verification code to professor email"""
    import random

    # Send email
    try:
        # Validate email format
        if not email or "univ" not in email.lower():
            return {"success": False, "message": "Adresse email universitaire invalide"}

        # Generate 6-digit code
        verification_code = str(random.randint(100000, 999999))

        # Store code with timestamp
        current_user_verification_codes[email] = {
            'code': verification_code,
            'timestamp': datetime.utcnow()
        }

        subject = "Code de vérification - INTERSTELLAR CLUB"

        # HTML body with embedded logos - Professional Design for verification code
        html_body = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code de vérification - INTERSTELLAR CLUB</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); min-height: 100vh;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background: rgba(255,255,255,0.95); border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); overflow: hidden;">
                        <!-- Header with logos -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #06b6d4 0%, #4f46e5 100%); padding: 30px 20px; text-align: center;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center">
                                            <img src="cid:logo_main" alt="INTERSTELLAR CLUB" style="height: 70px; margin: 0 15px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                                            <img src="cid:logo_secondary" alt="Second Logo" style="height: 55px; margin: 0 15px; border-radius: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="padding-top: 15px;">
                                            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                                INTERSTELLAR CLUB
                                            </h1>
                                            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 16px; font-weight: 300;">
                                                Code de vérification
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Main content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td style="color: #1f2937; font-size: 16px; line-height: 1.8; text-align: center;">
                                            <h2 style="color: #06b6d4; margin-bottom: 20px;">🔐 Code de vérification</h2>
                                            <p style="margin-bottom: 30px;">Bonjour,</p>
                                            <p>Votre code de vérification pour l'inscription à <strong>INTERSTELLAR CLUB</strong> est :</p>

                                            <!-- Verification Code Box -->
                                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 30px 0;">
                                                <tr>
                                                    <td align="center">
                                                        <div style="background: linear-gradient(135deg, #06b6d4 0%, #4f46e5 100%); color: white; padding: 20px; border-radius: 12px; font-size: 32px; font-weight: bold; letter-spacing: 8px; box-shadow: 0 8px 20px rgba(6, 182, 212, 0.3);">
                                                            {verification_code}
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>

                                            <p style="color: #64748b; font-size: 14px; margin-top: 20px;">
                                                ⏰ <strong>Ce code est valable pendant 10 minutes.</strong>
                                            </p>
                                            <p style="color: #64748b; font-size: 14px;">
                                                Veuillez entrer ce code dans le formulaire d'inscription pour compléter votre enregistrement.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background: #f8fafc; padding: 30px; border-top: 2px solid #e2e8f0;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center" style="color: #64748b; font-size: 14px; line-height: 1.6;">
                                            <p style="margin: 0 0 10px 0;">
                                                <strong style="color: #06b6d4;">INTERSTELLAR CLUB</strong><br>
                                                Club Universitaire d'Innovation Scientifique
                                            </p>
                                            <p style="margin: 0; font-size: 12px; color: #94a3b8;">
                                                Cet email a été envoyé automatiquement depuis notre plateforme.<br>
                                                Pour toute question, contactez-nous à l'adresse universitaire.
                                            </p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="padding-top: 20px;">
                                            <div style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #06b6d4 0%, #4f46e5 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);">
                                                🌟 Explorez l'Innovation Scientifique
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <!-- Disclaimer -->
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="margin-top: 20px;">
                        <tr>
                            <td align="center" style="color: rgba(255,255,255,0.7); font-size: 11px; line-height: 1.4;">
                                <p style="margin: 0;">
                                    🔒 Cet email contient des informations confidentielles.<br>
                                    INTERSTELLAR CLUB - Tous droits réservés © 2025
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

        # Send HTML email
        # Create HTML email with embedded logos
        msg = MIMEMultipart("related")
        msg["From"] = EMAIL_FROM
        msg["To"] = email
        msg["Subject"] = subject

        # Attach HTML content
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)

        # Attach logos as inline images
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
                print(f"Logo attachment failed ({logo_path}):", e)

        # Send via Gmail
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, email, msg.as_string())
        server.quit()

        return {"success": True, "message": "Code envoyé avec succès"}

    except Exception as e:
        print(f"Error sending verification code: {e}")
        return {"success": False, "message": "Erreur lors de l'envoi du code"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    
    # Get all projects count for statistics (exclude the general team members project)
    total_projects_count = db.query(Project).filter(Project.name != "Membres d'équipe").count()

    # Get projects based on role (exclude the general team members project)
    if user.role in ['Admin', 'Professor']:
        projects = db.query(Project).filter(Project.name != "Membres d'équipe").all()
    else:
        managed_projects = db.query(Project).filter(Project.manager_id == user.id, Project.name != "Membres d'équipe").all()
        team_projects_ids = [tm.project_id for tm in db.query(TeamMember).filter(TeamMember.user_id == user.id).all()]
        team_projects = db.query(Project).filter(Project.id.in_(team_projects_ids), Project.name != "Membres d'équipe").all() if team_projects_ids else []
        projects = list({p.id: p for p in (managed_projects + team_projects)}.values())

    pending_students = []
    approved_students = []
    rejected_students = []
    approver_map = {}
    team_members = []
    total_team_members = 0

    # Get approved students for all users (to show team members count and section)
    approved_students = db.query(User).filter(User.role == "Student", User.approval_status == "approved").order_by(User.approval_decision_at.desc().nullslast()).all()
    total_team_members = len(approved_students)

    if user.role in ['Admin', 'Professor']:
        pending_students = db.query(User).filter(User.role == "Student", User.approval_status == "pending").all()
        rejected_students = db.query(User).filter(User.role == "Student", User.approval_status == "rejected").order_by(User.approval_decision_at.desc().nullslast()).all()
        approver_ids = {s.approval_by_id for s in approved_students + rejected_students if s.approval_by_id}
        if approver_ids:
            approver_map = {u.id: u for u in db.query(User).filter(User.id.in_(approver_ids)).all()}
        # Get all team members with their project info (excluding the general team members project)
        team_members = db.query(TeamMember).join(Project).filter(Project.name != "Membres d'équipe").all()
    else:
        # Limit team list to projects the user manages or belongs to
        project_ids = [p.id for p in projects]
        if project_ids:
            team_members = (
                db.query(TeamMember)
                .join(Project)
                .filter(TeamMember.project_id.in_(project_ids))
                .all()
            )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "projects": projects,
        "total_projects_count": total_projects_count,
        "pending_students": pending_students,
        "approved_students": approved_students,
        "rejected_students": rejected_students,
        "approver_map": approver_map,
        "team_members": team_members,
        "total_team_members": total_team_members
    })

@app.get("/projects/new", response_class=HTMLResponse)
async def new_project_page(request: Request, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    return templates.TemplateResponse("new_project.html", {"request": request, "user": user})

@app.post("/projects/new")
async def create_project(
    name: str = Form(...),
    type: str = Form(...),
    mission_objective: str = Form(...),
    success_criteria: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    project = Project(
        name=name,
        type=type,
        mission_objective=mission_objective,
        success_criteria=success_criteria,
        manager_id=current_user_id,
        start_date=datetime.fromisoformat(start_date),
        end_date=datetime.fromisoformat(end_date)
    )
    db.add(project)
    db.commit()
    
    # Create default phases
    phases = ["Analyse du besoin & Cahier des charges", "Conception", "Simulation & Validation virtuelle", "Fabrication & Intégration", "Tests & Expérimentation", "Analyse des résultats & Optimisation", "Documentation & Présentation"]
    for phase_name in phases:
        phase = Phase(project_id=project.id, name=phase_name)
        db.add(phase)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project.id}", status_code=303)

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to this project
    is_manager = project.manager_id == user.id
    is_team_member = db.query(TeamMember).filter(
        TeamMember.project_id == project_id,
        TeamMember.user_id == user.id
    ).first() is not None
    is_admin_or_prof = user.role in ['Admin', 'Professor']
    
    if not (is_manager or is_team_member or is_admin_or_prof):
        return RedirectResponse(url="/dashboard", status_code=303)
    
    phases = db.query(Phase).filter(Phase.project_id == project_id).all()
    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    team_members = db.query(TeamMember).filter(TeamMember.project_id == project_id).all()
    files = db.query(ProjectFile).filter(ProjectFile.project_id == project_id).order_by(ProjectFile.uploaded_at.desc()).all()
    messages = db.query(Message).filter(Message.project_id == project_id).order_by(Message.created_at.asc()).all()
    
    # Get all users for adding members
    all_users = db.query(User).filter(
        (User.role.in_(['Member', 'Project Manager'])) |
        ((User.role == 'Student') & (User.approval_status == 'approved'))
    ).all()
    team_user_ids = [tm.user_id for tm in team_members]
    available_users = [u for u in all_users if u.id not in team_user_ids and u.id != project.manager_id]
    
    return templates.TemplateResponse("project.html", {
        "request": request,
        "user": user,
        "project": project,
        "phases": phases,
        "risks": risks,
        "team_members": team_members,
        "files": files,
        "messages": messages,
        "available_users": available_users,
        "is_manager": is_manager,
        "is_admin_or_prof": is_admin_or_prof
    })

@app.post("/projects/{project_id}/add-member")
async def add_team_member(
    project_id: int,
    user_id: int = Form(...),
    role: str = Form(...),
    responsibilities: str = Form(default=""),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not (user.role in ['Admin', 'Professor'] or project.manager_id == user.id):
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    
    team_member = TeamMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
        responsibilities=responsibilities
    )
    db.add(team_member)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.post("/projects/{project_id}/remove-member/{member_id}")
async def remove_team_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not (user.role in ['Admin', 'Professor'] or project.manager_id == user.id):
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if member:
        db.delete(member)
        db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.post("/projects/{project_id}/update-progress")
async def update_project_progress(
    project_id: int,
    overall_progress: int = Form(...),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not (user.role in ['Admin', 'Professor'] or project.manager_id == user.id):
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    
    project.overall_progress = overall_progress
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.post("/members/{member_id}/update-progress")
async def update_member_progress(
    member_id: int,
    progress: int = Form(...),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    project = db.query(Project).filter(Project.id == member.project_id).first()
    
    if not (user.role in ['Admin', 'Professor'] or project.manager_id == user.id):
        return RedirectResponse(url=f"/projects/{member.project_id}", status_code=303)
    
    member.progress = progress
    db.commit()
    
    return RedirectResponse(url=f"/projects/{member.project_id}", status_code=303)

def get_or_create_team_members_project(db: Session):
    """Get or create the general team members project"""
    project = db.query(Project).filter(Project.name == "Membres d'équipe").first()
    if not project:
        # Create the general team members project
        project = Project(
            name="Membres d'équipe",
            type="Équipe générale",
            mission_objective="Gestion des membres de l'équipe étudiante approuvés",
            success_criteria="Tous les étudiants approuvés sont membres actifs",
            manager_id=1,  # Default admin/professor ID - will be updated
            start_date=datetime.utcnow().date(),
            end_date=datetime.utcnow().date().replace(year=datetime.utcnow().year + 1),
            status="Active"
        )
        db.add(project)
        db.commit()
        # Create default phases
        phases = ["Inscription", "Formation", "Participation", "Évaluation"]
        for phase_name in phases:
            phase = Phase(project_id=project.id, name=phase_name)
            db.add(phase)
        db.commit()
    return project

@app.get("/students/{student_id}/approve")
async def approve_student(student_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    user = get_current_user(db)
    if not require_prof_or_admin(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    student = db.query(User).filter(User.id == student_id, User.role == "Student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.approval_status = "approved"
    student.approval_by_id = user.id
    student.approval_decision_at = datetime.utcnow()
    db.commit()

    # Notify student
    if student.email:
        approval_body = f"""Félicitations {student.first_name} {student.last_name} !

Votre demande d'inscription a été acceptée sur la plateforme INTERSTELLAR CLUB ! 🎉

Vous pouvez désormais accéder à votre compte et bénéficier de toutes les fonctionnalités de la plateforme :
- Créer et gérer des projets
- Participer aux activités scientifiques
- Communiquer avec l'équipe

Nom d'utilisateur : {student.username}

Bienvenue dans notre communauté scientifique !

Cordialement,
L'équipe INTERSTELLAR CLUB"""
        send_email(student.email, "🎉 Votre demande d'inscription a été acceptée - INTERSTELLAR CLUB", approval_body, email_type="acceptance")
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/students/{student_id}/reject")
async def reject_student(student_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    user = get_current_user(db)
    if not require_prof_or_admin(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    student = db.query(User).filter(User.id == student_id, User.role == "Student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.approval_status = "rejected"
    student.approval_by_id = user.id
    student.approval_decision_at = datetime.utcnow()
    db.commit()
    # Notify student
    if student.email:
        rejection_body = f"""Cher/Chère {student.first_name} {student.last_name},

Nous regrettons de ne pas pouvoir accepter votre demande d'inscription sur la plateforme INTERSTELLAR CLUB pour le moment.

Vous pouvez :
1. Réviser les informations fournies et vous assurer de leur exactitude
2. Contacter les professeurs pour obtenir des conseils
3. Réessayer ultérieurement

Nous vous remercions pour votre intérêt à rejoindre notre communauté scientifique.

Cordialement,
L'équipe INTERSTELLAR CLUB"""
        send_email(student.email, "Demande d'inscription - INTERSTELLAR CLUB", rejection_body, email_type="rejection")
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/projects/{project_id}/upload")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    is_manager = project.manager_id == user.id
    is_team_member = db.query(TeamMember).filter(
        TeamMember.project_id == project_id,
        TeamMember.user_id == user.id
    ).first() is not None
    is_admin_or_prof = user.role in ['Admin', 'Professor']
    
    if not (is_manager or is_team_member or is_admin_or_prof):
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    
    allowed_extensions = ['.pdf', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt', '.zip']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return RedirectResponse(url=f"/projects/{project_id}?error=invalid_file", status_code=303)
    
    project_upload_dir = f"uploads/project_{project_id}"
    os.makedirs(project_upload_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(project_upload_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    project_file = ProjectFile(
        project_id=project_id,
        filename=safe_filename,
        original_filename=file.filename,
        file_type=file_ext,
        file_path=file_path,
        uploaded_by=user.id,
        description=description
    )
    db.add(project_file)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.get("/files/{file_id}/download")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    file = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == file.project_id).first()
    is_manager = project.manager_id == user.id
    is_team_member = db.query(TeamMember).filter(
        TeamMember.project_id == file.project_id,
        TeamMember.user_id == user.id
    ).first() is not None
    is_admin_or_prof = user.role in ['Admin', 'Professor']
    
    if not (is_manager or is_team_member or is_admin_or_prof):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=file.file_path,
        filename=file.original_filename,
        media_type='application/octet-stream'
    )

@app.post("/files/{file_id}/delete")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    file = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    project = db.query(Project).filter(Project.id == file.project_id).first()
    
    is_owner = file.uploaded_by == user.id
    is_manager = project.manager_id == user.id
    is_admin_or_prof = user.role in ['Admin', 'Professor']
    
    if not (is_owner or is_manager or is_admin_or_prof):
        return RedirectResponse(url=f"/projects/{file.project_id}", status_code=303)
    
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    db.delete(file)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{file.project_id}", status_code=303)

@app.post("/projects/{project_id}/messages")
async def send_message(
    project_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = get_current_user(db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    is_manager = project.manager_id == user.id
    is_team_member = db.query(TeamMember).filter(
        TeamMember.project_id == project_id,
        TeamMember.user_id == user.id
    ).first() is not None
    is_admin_or_prof = user.role in ['Admin', 'Professor']
    
    if not (is_manager or is_team_member or is_admin_or_prof):
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    
    message = Message(
        project_id=project_id,
        user_id=user.id,
        content=content
    )
    db.add(message)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}#chat", status_code=303)

@app.post("/phases/{phase_id}/update")
async def update_phase(
    phase_id: int,
    status: str = Form(...),
    validation: str = Form(...),
    db: Session = Depends(get_db)
):
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    if phase:
        phase.status = status
        phase.validation = validation
        if status == "Completed":
            phase.completed_date = datetime.utcnow()
        db.commit()
    
    return RedirectResponse(url=f"/projects/{phase.project_id}", status_code=303)

@app.post("/risks/new")
async def create_risk(
    project_id: int = Form(...),
    description: str = Form(...),
    probability: str = Form(...),
    severity: str = Form(...),
    mitigation: str = Form(...),
    db: Session = Depends(get_db)
):
    risk = Risk(
        project_id=project_id,
        description=description,
        probability=probability,
        severity=severity,
        mitigation=mitigation
    )
    db.add(risk)
    db.commit()
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.get("/logout")
async def logout():
    global current_user_id
    current_user_id = None
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-profile-image")
async def update_profile_image(
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not current_user_id:
        return {"success": False, "message": "Utilisateur non connecté"}

    user = get_current_user(db)
    if not user:
        return {"success": False, "message": "Utilisateur non trouvé"}

    try:
        # التحقق من صيغة الملف
        allowed_ext = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        file_ext = os.path.splitext(profile_image.filename)[1].lower()
        if file_ext not in allowed_ext:
            return {"success": False, "message": "Format d'image non pris en charge"}

        # إنشاء المجلد إذا لم يكن موجوداً
        profile_dir = "uploads/profile_images"
        os.makedirs(profile_dir, exist_ok=True)

        # حذف الصورة القديمة إذا كانت موجودة
        if user.profile_image and os.path.exists(user.profile_image):
            os.remove(user.profile_image)

        # حفظ الصورة الجديدة
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{profile_image.filename}"
        profile_path = os.path.join(profile_dir, safe_name)

        with open(profile_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

        # تحديث قاعدة البيانات - حفظ المسار النسبي للويب
        web_path = f"uploads/profile_images/{safe_name}"
        user.profile_image = web_path
        db.commit()

        return {"success": True, "message": "Photo de profil mise à jour avec succès"}

    except Exception as e:
        print(f"Erreur lors de la mise à jour de la photo: {e}")
        return {"success": False, "message": "Erreur lors de la mise à jour"}

@app.post("/projects/{project_id}/delete")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    if not current_user_id:
        return RedirectResponse(url="/", status_code=303)

    user = get_current_user(db)
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Only Admin and Professor can delete projects
    if user.role not in ['Admin', 'Professor']:
        return RedirectResponse(url="/dashboard", status_code=303)

    # Delete project files from filesystem
    project_upload_dir = f"uploads/project_{project_id}"
    if os.path.exists(project_upload_dir):
        shutil.rmtree(project_upload_dir)

    # Delete project from database (will cascade delete related records)
    db.delete(project)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)

if __name__ == "__main__":
    import uvicorn
    import os
    import subprocess
    import sys

    # استخدام منفذ مختلف إذا كان المنفذ 8000 مشغولاً
    port = int(os.getenv("PORT", "8000"))

    print("INTERSTELLAR CLUB Starting...")
    print(f"Checking port {port}...")

    # التحقق من العمليات التي تستخدم المنفذ وإنهاؤها
    try:
        if sys.platform == "win32":
            # Windows - استخدام cp1252 encoding لتجنب مشاكل Unicode
            result = subprocess.run(['netstat', '-ano'], capture_output=True, encoding='cp1252', errors='ignore')
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            pid_int = int(pid)
                            print(f"Found process {pid} using port {port}, terminating...")
                            subprocess.run(['taskkill', '/PID', str(pid_int), '/F'], capture_output=True)
                            print(f"Process {pid} terminated.")
                            # انتظار قليل للتأكد من إنهاء العملية
                            import time
                            time.sleep(1)
                        except ValueError:
                            pass  # PID غير صحيح
    except Exception as e:
        print(f"Warning: Could not check/kill existing processes: {e}")

    print(f"Open: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=port)