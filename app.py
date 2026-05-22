from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'learnhub-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learnhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'


# ─── Models ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_color  = db.Column(db.String(20), default='#2563eb')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments   = db.relationship('Enrollment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.name.strip().split()
        return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()


class Category(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(80), unique=True, nullable=False)
    icon    = db.Column(db.String(10), default='📚')
    courses = db.relationship('Course', backref='category_obj', lazy=True)


class Course(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    slug          = db.Column(db.String(200), unique=True, nullable=False)
    description   = db.Column(db.Text, nullable=False)
    long_desc     = db.Column(db.Text)
    category_id   = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    level         = db.Column(db.String(30), nullable=False)
    duration      = db.Column(db.String(50), nullable=False)
    lessons       = db.Column(db.Integer, default=0)
    instructor    = db.Column(db.String(120), nullable=False)
    instructor_bio= db.Column(db.String(300))
    price         = db.Column(db.Float, default=0.0)
    color         = db.Column(db.String(20), default='#2563eb')
    icon          = db.Column(db.String(10), default='📘')
    rating        = db.Column(db.Float, default=4.5)
    featured      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments   = db.relationship('Enrollment', backref='course', lazy=True)

    @property
    def enrolled_count(self):
        return len(self.enrollments)


class Enrollment(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress    = db.Column(db.Integer, default=0)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(200), nullable=False)
    subject    = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Seed ──────────────────────────────────────────────────────────────────────

def seed_data():
    if Category.query.count() > 0:
        return

    cats = [
        Category(name='Web Development',   icon='🌐'),
        Category(name='Data Science',      icon='📊'),
        Category(name='Design',            icon='🎨'),
        Category(name='Machine Learning',  icon='🤖'),
        Category(name='Mobile Dev',        icon='📱'),
        Category(name='Cybersecurity',     icon='🔒'),
    ]
    for c in cats: db.session.add(c)
    db.session.flush()

    courses = [
        Course(title='Full-Stack Web Development Bootcamp',
               slug='full-stack-bootcamp',
               description='Master HTML, CSS, JavaScript, React, Node.js, and databases from scratch.',
               long_desc='Go from zero to full-stack developer. You will build real projects every week, covering frontend with React, backend with Node/Express, and database design with PostgreSQL. Includes deployment on cloud platforms.',
               category_id=cats[0].id, level='Beginner', duration='48 hrs', lessons=120,
               instructor='Sarah Chen', instructor_bio='Senior engineer at Google with 10 years experience.',
               price=89.99, color='#2563eb', icon='🌐', rating=4.9, featured=True),

        Course(title='Python for Data Science',
               slug='python-data-science',
               description='Learn Python, Pandas, NumPy, and data visualization to analyze real datasets.',
               long_desc='A hands-on data science course using Python. You will learn Pandas for data manipulation, NumPy for numerical computing, Matplotlib and Seaborn for visualization, and how to work with real-world messy datasets.',
               category_id=cats[1].id, level='Beginner', duration='32 hrs', lessons=88,
               instructor='Dr. James Park', instructor_bio='Data scientist with PhD in Statistics.',
               price=79.99, color='#7c3aed', icon='📊', rating=4.8, featured=True),

        Course(title='UI/UX Design Masterclass',
               slug='ui-ux-design',
               description='Design beautiful, user-centered products with Figma and design thinking.',
               long_desc='Learn the full product design process: research, wireframing, prototyping, and high-fidelity design in Figma. You will build a portfolio of 5 real projects and learn how to present your work to stakeholders.',
               category_id=cats[2].id, level='Intermediate', duration='24 hrs', lessons=64,
               instructor='Maya Patel', instructor_bio='Lead designer at Figma.',
               price=69.99, color='#db2777', icon='🎨', rating=4.7, featured=True),

        Course(title='Machine Learning A–Z',
               slug='machine-learning-az',
               description='Master supervised, unsupervised learning, and neural networks with scikit-learn.',
               long_desc='A comprehensive machine learning course covering the theory and practice of ML algorithms. Build real models with scikit-learn and TensorFlow, and deploy them as web APIs.',
               category_id=cats[3].id, level='Intermediate', duration='40 hrs', lessons=104,
               instructor='Prof. Alex Kim', instructor_bio='AI researcher and university professor.',
               price=99.99, color='#059669', icon='🤖', rating=4.9, featured=True),

        Course(title='React Native Mobile Development',
               slug='react-native',
               description='Build cross-platform iOS and Android apps with React Native and Expo.',
               long_desc='Learn React Native from the ground up. Build production-ready apps with navigation, state management, native device APIs, and publish to both the App Store and Google Play.',
               category_id=cats[4].id, level='Intermediate', duration='30 hrs', lessons=80,
               instructor='Carlos Rivera', instructor_bio='Mobile lead at a top fintech startup.',
               price=84.99, color='#ea580c', icon='📱', rating=4.6, featured=False),

        Course(title='Ethical Hacking & Cybersecurity',
               slug='ethical-hacking',
               description='Learn penetration testing, network security, and how to protect systems.',
               long_desc='Master the tools and techniques used by real security professionals. Covers reconnaissance, exploitation, web app vulnerabilities (OWASP Top 10), cryptography, and building a security mindset.',
               category_id=cats[5].id, level='Advanced', duration='36 hrs', lessons=96,
               instructor='Nina Torres', instructor_bio='CISSP-certified security consultant.',
               price=94.99, color='#dc2626', icon='🔒', rating=4.8, featured=False),

        Course(title='Advanced CSS & Animations',
               slug='advanced-css',
               description='Go deep with CSS Grid, Flexbox, custom properties, and keyframe animations.',
               long_desc='Take your CSS skills to the next level. You will master layout systems, custom properties, CSS animations, scroll-driven animations, and performance techniques used by top frontend developers.',
               category_id=cats[0].id, level='Intermediate', duration='18 hrs', lessons=52,
               instructor='Tom Nguyen', instructor_bio='Frontend specialist and open-source contributor.',
               price=49.99, color='#0891b2', icon='✨', rating=4.7, featured=False),

        Course(title='Deep Learning with PyTorch',
               slug='deep-learning-pytorch',
               description='Build CNNs, RNNs, and Transformers from scratch using PyTorch.',
               long_desc='Go deep into neural networks with PyTorch. You will implement convolutional networks for image recognition, recurrent networks for sequence tasks, and the Transformer architecture from scratch.',
               category_id=cats[3].id, level='Advanced', duration='44 hrs', lessons=112,
               instructor='Dr. Yuki Tanaka', instructor_bio='Deep learning researcher at a top AI lab.',
               price=109.99, color='#4f46e5', icon='🧠', rating=4.9, featured=False),
    ]
    for c in courses: db.session.add(c)
    db.session.commit()


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    featured = Course.query.filter_by(featured=True).all()
    categories = Category.query.all()
    total_courses = Course.query.count()
    total_users   = User.query.count()
    return render_template('home.html', featured=featured, categories=categories,
                           total_courses=total_courses, total_users=total_users)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    category_filter = request.args.get('category', '')
    level_filter    = request.args.get('level', '')
    search          = request.args.get('q', '')

    query = Course.query
    if category_filter:
        query = query.join(Category).filter(Category.name == category_filter)
    if level_filter:
        query = query.filter(Course.level == level_filter)
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%'))

    courses    = query.order_by(Course.featured.desc(), Course.rating.desc()).all()
    categories = Category.query.all()
    return render_template('services.html', courses=courses, categories=categories,
                           selected_category=category_filter,
                           selected_level=level_filter, search=search)


@app.route('/course/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    enrolled = False
    if current_user.is_authenticated:
        enrolled = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first() is not None
    related = Course.query.filter(Course.category_id == course.category_id, Course.id != course.id).limit(3).all()
    return render_template('course_detail.html', course=course, enrolled=enrolled, related=related)


@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not existing:
        enroll_obj = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(enroll_obj)
        db.session.commit()
        flash(f'You are now enrolled in "{course.title}"!', 'success')
    else:
        flash('You are already enrolled in this course.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if not all([name, email, subject, message]):
            flash('All fields are required.', 'error')
            return render_template('contact.html')
        msg = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(msg)
        db.session.commit()
        flash('Message sent! We will get back to you within 24 hours.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name.split()[0]}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm', '')

        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return render_template('register.html')

        colors = ['#2563eb','#7c3aed','#db2777','#059669','#ea580c','#0891b2']
        import random
        user = User(name=name, email=email, avatar_color=random.choice(colors))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome to LearnHub, {name.split()[0]}! 🎉', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    all_courses = Course.query.order_by(Course.rating.desc()).limit(4).all()
    return render_template('dashboard.html', enrollments=enrollments, all_courses=all_courses)


@app.route('/dashboard/progress/<int:enrollment_id>', methods=['POST'])
@login_required
def update_progress(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    progress = int(request.form.get('progress', 0))
    enrollment.progress = max(0, min(100, progress))
    db.session.commit()
    flash('Progress updated!', 'success')
    return redirect(url_for('dashboard'))


# ─── Portfolio (keep existing) ─────────────────────────────────────────────────

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
