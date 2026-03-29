from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Course, Lesson, Enrollment, LessonProgress
import io, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'learntech-secret-change-in-production')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///learntech.db')
# Render gives postgres:// but SQLAlchemy needs postgresql://
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def seed_data():
    if Course.query.count() > 0:
        return
    courses = [
        {
            'title': 'Cybersecurity',
            'icon': '🔐',
            'description': 'Learn ethical hacking, network security, threat analysis, and how to protect systems from cyber attacks.',
            'lessons': [
                ('Introduction to Cybersecurity', 'Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. In this lesson, we cover the CIA Triad: Confidentiality, Integrity, and Availability — the three pillars of information security.\n\nKey concepts:\n- Threats vs Vulnerabilities\n- Types of attackers (black hat, white hat, grey hat)\n- Common attack vectors'),
                ('Network Security Basics', 'Networks are the backbone of modern communication. Securing them is critical.\n\nTopics covered:\n- Firewalls and how they work\n- VPNs (Virtual Private Networks)\n- Intrusion Detection Systems (IDS)\n- Common network attacks: DDoS, Man-in-the-Middle, Packet Sniffing'),
                ('Ethical Hacking & Penetration Testing', 'Ethical hackers (penetration testers) are hired to find vulnerabilities before malicious hackers do.\n\nYou will learn:\n- Phases of penetration testing: Reconnaissance, Scanning, Exploitation, Reporting\n- Tools: Nmap, Metasploit, Wireshark\n- Writing a penetration test report'),
                ('Cryptography Fundamentals', 'Cryptography is the art of securing information.\n\nCovered topics:\n- Symmetric vs Asymmetric encryption\n- SSL/TLS protocols\n- Hashing algorithms: MD5, SHA-256\n- Public Key Infrastructure (PKI)'),
                ('Incident Response & Recovery', 'When a breach happens, how you respond matters.\n\nLearn:\n- Incident response lifecycle\n- Digital forensics basics\n- Creating an incident response plan\n- Business continuity and disaster recovery'),
            ]
        },
        {
            'title': 'Graphic Design',
            'icon': '🎨',
            'description': 'Master visual communication, typography, color theory, and design tools to create stunning graphics.',
            'lessons': [
                ('Design Principles & Elements', 'Great design starts with understanding the fundamentals.\n\nCore principles:\n- Balance, Contrast, Alignment, Repetition, Proximity\n- Elements: Line, Shape, Color, Texture, Space\n- Visual hierarchy and how the eye moves across a design'),
                ('Color Theory', 'Color is one of the most powerful tools in a designer\'s toolkit.\n\nTopics:\n- The color wheel: primary, secondary, tertiary colors\n- Color harmonies: complementary, analogous, triadic\n- Psychology of color in branding\n- Working with hex codes and RGB/CMYK'),
                ('Typography', 'Typography is the art of arranging type to make written language legible and appealing.\n\nLearn:\n- Serif vs Sans-serif fonts\n- Font pairing techniques\n- Kerning, leading, and tracking\n- Choosing fonts for different contexts'),
                ('Logo & Brand Identity Design', 'A logo is the face of a brand.\n\nCovered:\n- Logo design process: brief, research, sketching, digitizing\n- Types of logos: wordmark, lettermark, icon, combination\n- Creating brand guidelines\n- File formats: SVG, PNG, PDF'),
                ('Digital Tools: Canva & Figma', 'Get hands-on with industry-standard design tools.\n\nYou will learn:\n- Canva for quick social media graphics\n- Figma for UI/UX and collaborative design\n- Exporting assets for web and print\n- Building a design portfolio'),
            ]
        },
        {
            'title': 'Web Development',
            'icon': '💻',
            'description': 'Build modern websites and web apps using HTML, CSS, JavaScript, and backend technologies.',
            'lessons': [
                ('HTML Fundamentals', 'HTML (HyperText Markup Language) is the skeleton of every webpage.\n\nLearn:\n- Document structure: DOCTYPE, html, head, body\n- Semantic elements: header, nav, main, footer, article\n- Forms, tables, and media elements\n- Accessibility best practices'),
                ('CSS Styling & Layouts', 'CSS brings your HTML to life with styles and layouts.\n\nTopics:\n- Selectors, specificity, and the cascade\n- Box model: margin, border, padding, content\n- Flexbox and CSS Grid\n- Responsive design with media queries'),
                ('JavaScript Essentials', 'JavaScript makes websites interactive.\n\nCovered:\n- Variables, data types, functions\n- DOM manipulation\n- Events and event listeners\n- Fetch API and working with JSON'),
                ('Backend with Python & Flask', 'Build server-side applications with Python.\n\nLearn:\n- Setting up a Flask application\n- Routes and templates (Jinja2)\n- Working with databases using SQLAlchemy\n- User authentication and sessions'),
                ('Deploying Your Website', 'Get your website live on the internet.\n\nTopics:\n- Hosting options: shared hosting, VPS, cloud\n- Deploying to platforms like Render or Railway\n- Domain names and DNS\n- SSL certificates and HTTPS'),
            ]
        },
        {
            'title': 'Computer Basic Skills',
            'icon': '🖥️',
            'description': 'Build a solid foundation in computer usage, Microsoft Office, internet safety, and digital literacy.',
            'lessons': [
                ('Introduction to Computers', 'Understand how computers work and the key components.\n\nTopics:\n- Hardware vs Software\n- Input and output devices\n- CPU, RAM, Storage explained simply\n- Operating systems: Windows, macOS, Linux'),
                ('File Management & Organization', 'Stay organized and productive on your computer.\n\nLearn:\n- Creating, moving, copying, and deleting files\n- Folder structures and naming conventions\n- Using search to find files quickly\n- Cloud storage: Google Drive, OneDrive'),
                ('Microsoft Office Essentials', 'Office tools are used in almost every workplace.\n\nCovered:\n- Word: formatting documents, tables, mail merge\n- Excel: formulas, charts, data sorting\n- PowerPoint: creating professional presentations\n- Outlook: email management and calendar'),
                ('Internet & Email Safety', 'Stay safe online in today\'s connected world.\n\nLearn:\n- How the internet works\n- Identifying phishing emails and scams\n- Strong passwords and two-factor authentication\n- Safe browsing habits'),
                ('Introduction to AI Tools', 'AI tools are transforming how we work.\n\nTopics:\n- What is Artificial Intelligence?\n- Using ChatGPT and AI assistants productively\n- AI tools for writing, images, and productivity\n- Ethical use of AI'),
            ]
        },
    ]
    for c in courses:
        course = Course(title=c['title'], icon=c['icon'], description=c['description'])
        db.session.add(course)
        db.session.flush()
        for i, (title, content) in enumerate(c['lessons']):
            lesson = Lesson(course_id=course.id, title=title, content=content, order=i+1)
            db.session.add(lesson)
    # Create admin user
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            name='Gideon Marvin',
            email='admin@learntech.co.ke',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
    else:
        admin = User.query.filter_by(is_admin=True).first()
        admin.name = 'Gideon Marvin'
        admin.email = 'admin@learntech.co.ke'
        admin.password = generate_password_hash('admin123')
        db.session.add(admin)
    db.session.commit()

# ─── Auth Routes ────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Browse our courses below.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ─── Public Routes ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

# ─── Student Routes ──────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id, paid=True).all()
    courses = Course.query.all()
    enrolled_ids = [e.course_id for e in enrollments]
    return render_template('dashboard.html', enrollments=enrollments, courses=courses, enrolled_ids=enrolled_ids)

@app.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if existing and existing.paid:
        return redirect(url_for('learn', course_id=course_id))
    if request.method == 'POST':
        try:
            from pesapal import submit_order, register_ipn

            # Register IPN once and cache it — re-register if not set
            ipn_id = os.environ.get('PESAPAL_IPN_ID', '')
            if not ipn_id:
                ipn_id = register_ipn()
                os.environ['PESAPAL_IPN_ID'] = ipn_id  # cache for this session

            reference = f'LT-{course_id}-{current_user.id}-{int(datetime.utcnow().timestamp())}'
            name_parts = current_user.name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else 'N/A'

            redirect_url, tracking_id = submit_order(
                amount=500,
                description=f'LearnTech: {course.title}',
                reference=reference,
                email=current_user.email,
                phone=request.form.get('phone', ''),
                first_name=first_name,
                last_name=last_name,
                ipn_id=ipn_id
            )
            if existing:
                existing.payment_ref = tracking_id
            else:
                enrollment = Enrollment(
                    user_id=current_user.id,
                    course_id=course_id,
                    paid=False,
                    payment_ref=tracking_id
                )
                db.session.add(enrollment)
            db.session.commit()
            return redirect(redirect_url)

        except Exception as e:
            flash(f'Payment initiation failed: {str(e)}', 'error')
    return render_template('enroll.html', course=course)


@app.route('/pesapal/callback')
def pesapal_callback():
    """Pesapal redirects here after payment."""
    tracking_id = request.args.get('OrderTrackingId')

    if not tracking_id:
        flash('Payment verification failed.', 'error')
        return redirect(url_for('dashboard'))

    try:
        from pesapal import get_transaction_status
        status = get_transaction_status(tracking_id)
        payment_status = status.get('payment_status_description', '').lower()

        enrollment = Enrollment.query.filter_by(payment_ref=tracking_id).first()
        if enrollment and payment_status == 'completed':
            enrollment.paid = True
            db.session.commit()
            flash('Payment successful! You can now access the course.', 'success')
            return redirect(url_for('learn', course_id=enrollment.course_id))
        else:
            flash(f'Payment not completed (status: {payment_status}). Try again.', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Could not verify payment: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/learn/<int:course_id>')
@login_required
def learn(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id, paid=True).first()
    if not enrollment:
        flash('Please enroll and pay to access this course.', 'error')
        return redirect(url_for('enroll', course_id=course_id))
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    completed_ids = [lp.lesson_id for lp in LessonProgress.query.filter_by(user_id=current_user.id, completed=True).all()]
    lesson_id = request.args.get('lesson', lessons[0].id if lessons else None, type=int)
    current_lesson = Lesson.query.get(lesson_id) if lesson_id else (lessons[0] if lessons else None)
    return render_template('course.html', course=course, lessons=lessons, current_lesson=current_lesson,
                           completed_ids=completed_ids, enrollment=enrollment)

@app.route('/complete-lesson/<int:lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=lesson.course_id, paid=True).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled'}), 403
    lp = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not lp:
        lp = LessonProgress(user_id=current_user.id, lesson_id=lesson_id, completed=True)
        db.session.add(lp)
    else:
        lp.completed = True
    # Update progress
    total = Lesson.query.filter_by(course_id=lesson.course_id).count()
    done = LessonProgress.query.join(Lesson).filter(
        LessonProgress.user_id == current_user.id,
        Lesson.course_id == lesson.course_id,
        LessonProgress.completed == True
    ).count()
    enrollment.progress = int((done / total) * 100)
    if enrollment.progress == 100:
        enrollment.completed = True
        enrollment.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'progress': enrollment.progress, 'completed': enrollment.completed})

@app.route('/certificate/<int:course_id>')
@login_required
def certificate(course_id):
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id, paid=True, completed=True).first()
    if not enrollment:
        flash('Complete the course first to get your certificate.', 'error')
        return redirect(url_for('learn', course_id=course_id))
    course = Course.query.get_or_404(course_id)
    return render_template('certificate.html', user=current_user, course=course, enrollment=enrollment)

@app.route('/certificate/<int:course_id>/download')
@login_required
def download_certificate(course_id):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, mm

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id, paid=True, completed=True
    ).first()
    if not enrollment:
        flash('Complete the course first.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get_or_404(course_id)

    # Generate a unique certificate number
    cert_number = f'LT-{course_id:02d}-{current_user.id:04d}-{enrollment.completed_at.strftime("%Y%m%d")}'

    page_w, page_h = landscape(A4)  # 841.89 x 595.28 pts
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ── Background ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#f8fafc'))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Outer border ────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#4f46e5'))
    c.setLineWidth(6)
    c.rect(18, 18, page_w - 36, page_h - 36, fill=0, stroke=1)

    # ── Inner border ────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#a5b4fc'))
    c.setLineWidth(1.5)
    c.rect(28, 28, page_w - 56, page_h - 56, fill=0, stroke=1)

    # ── Top accent bar ───────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.rect(18, page_h - 90, page_w - 36, 72, fill=1, stroke=0)

    # ── Logo image in accent bar ─────────────────────────────────────────────
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, page_w / 2 - 160, page_h - 84, width=44, height=44,
                    mask='auto', preserveAspectRatio=True)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 26)
        c.drawString(page_w / 2 - 110, page_h - 58, 'LearnTech Kenya')
        c.setFont('Helvetica', 11)
        c.drawString(page_w / 2 - 110, page_h - 76, 'Building Skills, Building Futures')
    else:
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(page_w / 2, page_h - 62, 'LearnTech Kenya')
        c.setFont('Helvetica', 12)
        c.drawCentredString(page_w / 2, page_h - 80, 'Building Skills, Building Futures')

    # ── Certificate of Completion ────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1e293b'))
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(page_w / 2, page_h - 130, 'CERTIFICATE OF COMPLETION')

    # ── Decorative line ──────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#4f46e5'))
    c.setLineWidth(1)
    c.line(page_w * 0.2, page_h - 140, page_w * 0.8, page_h - 140)

    # ── "This is to certify that" ────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#64748b'))
    c.setFont('Helvetica', 13)
    c.drawCentredString(page_w / 2, page_h - 170, 'This is to certify that')

    # ── Student Name ─────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1a1a2e'))
    c.setFont('Helvetica-Bold', 34)
    c.drawCentredString(page_w / 2, page_h - 215, current_user.name.upper())

    # ── Underline below name ─────────────────────────────────────────────────
    name_width = c.stringWidth(current_user.name.upper(), 'Helvetica-Bold', 34)
    line_x1 = (page_w - name_width) / 2 - 10
    line_x2 = (page_w + name_width) / 2 + 10
    c.setStrokeColor(colors.HexColor('#4f46e5'))
    c.setLineWidth(1.5)
    c.line(line_x1, page_h - 222, line_x2, page_h - 222)

    # ── "has successfully completed" ─────────────────────────────────────────
    c.setFillColor(colors.HexColor('#64748b'))
    c.setFont('Helvetica', 13)
    c.drawCentredString(page_w / 2, page_h - 250, 'has successfully completed the course')

    # ── Course Name ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(page_w / 2, page_h - 285, course.title.upper())

    # ── Student details row ──────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#f1f5f9'))
    c.roundRect(page_w * 0.15, page_h - 340, page_w * 0.7, 36, 6, fill=1, stroke=0)

    c.setFillColor(colors.HexColor('#475569'))
    c.setFont('Helvetica', 10)
    c.drawCentredString(page_w * 0.33, page_h - 318,
        f'Email: {current_user.email}')
    c.drawCentredString(page_w * 0.67, page_h - 318,
        f'Completed: {enrollment.completed_at.strftime("%B %d, %Y")}')

    # ── Certificate number ───────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#94a3b8'))
    c.setFont('Helvetica', 9)
    c.drawCentredString(page_w / 2, page_h - 355, f'Certificate No: {cert_number}')

    # ── Signature ────────────────────────────────────────────────────────────
    sig_y = 80
    sig_img = os.path.join(os.path.dirname(__file__), 'static', 'signature.png')
    if os.path.exists(sig_img):
        # Draw signature image centered above the line
        c.drawImage(sig_img, page_w * 0.5 - 60, sig_y + 18, width=120, height=50,
                    mask='auto', preserveAspectRatio=True)

    c.setStrokeColor(colors.HexColor('#1e293b'))
    c.setLineWidth(1)
    c.line(page_w * 0.35, sig_y + 16, page_w * 0.65, sig_y + 16)
    c.setFillColor(colors.HexColor('#1e293b'))
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(page_w * 0.5, sig_y + 4, 'Gideon Marvin')
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.HexColor('#64748b'))
    c.drawCentredString(page_w * 0.5, sig_y - 8, 'Director, LearnTech Kenya')

    # ── Bottom seal text ─────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#94a3b8'))
    c.setFont('Helvetica', 8)
    c.drawCentredString(page_w / 2, 38,
        'This certificate is issued by LearnTech Kenya and is valid proof of course completion.')

    c.save()
    buffer.seek(0)

    filename = f'LearnTech_Certificate_{current_user.name.replace(" ", "_")}_{course.title.replace(" ", "_")}.pdf'
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# ─── Admin Routes ────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    enrollments = Enrollment.query.filter_by(paid=True).all()
    courses = Course.query.all()
    total_revenue = len(enrollments) * 500
    return render_template('admin.html', users=users, enrollments=enrollments, courses=courses, total_revenue=total_revenue)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
else:
    # For Render / gunicorn
    with app.app_context():
        db.create_all()
        seed_data()
