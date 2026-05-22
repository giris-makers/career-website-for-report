from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'career-website-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///careers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(100))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    applications = db.relationship('Application', backref='job', lazy=True)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    cover_letter = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


def seed_jobs():
    if Job.query.count() == 0:
        jobs = [
            Job(
                title="Senior Software Engineer",
                department="Engineering",
                location="New York, NY (Hybrid)",
                type="Full-time",
                salary="$140,000 – $180,000",
                description="We are looking for a Senior Software Engineer to join our growing engineering team. You will design and build scalable systems, mentor junior engineers, and contribute to our technical roadmap.",
                requirements="5+ years of software engineering experience\nProficiency in Python, Go, or Java\nExperience with cloud platforms (AWS, GCP, or Azure)\nStrong understanding of distributed systems\nExcellent communication skills"
            ),
            Job(
                title="Product Designer",
                department="Design",
                location="Remote",
                type="Full-time",
                salary="$100,000 – $130,000",
                description="Join our design team to craft intuitive, beautiful user experiences. You will work closely with product managers and engineers to bring ideas from concept to launch.",
                requirements="3+ years of product design experience\nProficiency in Figma\nPortfolio demonstrating end-to-end design process\nExperience with design systems\nAbility to translate user research into design solutions"
            ),
            Job(
                title="Data Analyst",
                department="Analytics",
                location="Austin, TX",
                type="Full-time",
                salary="$85,000 – $110,000",
                description="We are seeking a Data Analyst to help us turn raw data into actionable insights. You will build dashboards, run analyses, and partner with teams across the company.",
                requirements="2+ years of data analysis experience\nStrong SQL skills\nExperience with BI tools (Tableau, Looker, or similar)\nProficiency in Python or R\nStrong attention to detail"
            ),
            Job(
                title="Marketing Manager",
                department="Marketing",
                location="San Francisco, CA (Hybrid)",
                type="Full-time",
                salary="$95,000 – $120,000",
                description="Lead our marketing efforts to grow brand awareness and drive customer acquisition. You will own campaigns, manage budgets, and collaborate with creative and sales teams.",
                requirements="4+ years of marketing experience\nProven track record in growth marketing\nExperience with paid and organic channels\nStrong analytical mindset\nExcellent writing and communication skills"
            ),
            Job(
                title="Customer Success Manager",
                department="Customer Success",
                location="Chicago, IL (Hybrid)",
                type="Full-time",
                salary="$75,000 – $95,000",
                description="Help our customers achieve their goals and maximize the value they get from our platform. You will own a portfolio of accounts, drive retention, and identify expansion opportunities.",
                requirements="3+ years in customer success or account management\nExperience with SaaS products\nStrong relationship-building skills\nData-driven approach to success metrics\nExperience with Salesforce or HubSpot"
            ),
            Job(
                title="DevOps Engineer",
                department="Engineering",
                location="Remote",
                type="Full-time",
                salary="$120,000 – $155,000",
                description="Build and maintain the infrastructure that powers our platform. You will work on CI/CD pipelines, cloud infrastructure, monitoring, and reliability engineering.",
                requirements="3+ years of DevOps or SRE experience\nStrong knowledge of Kubernetes and Docker\nExperience with Terraform or Pulumi\nProficiency with AWS or GCP\nSecurity-first mindset"
            ),
        ]
        for job in jobs:
            db.session.add(job)
        db.session.commit()


@app.route('/')
def index():
    department = request.args.get('department', '')
    location_filter = request.args.get('location', '')
    job_type = request.args.get('type', '')

    query = Job.query.filter_by(active=True)
    if department:
        query = query.filter(Job.department == department)
    if location_filter:
        query = query.filter(Job.location.ilike(f'%{location_filter}%'))
    if job_type:
        query = query.filter(Job.type == job_type)

    jobs = query.order_by(Job.posted_date.desc()).all()
    departments = db.session.query(Job.department).distinct().all()
    departments = [d[0] for d in departments]

    return render_template('index.html', jobs=jobs, departments=departments,
                           selected_department=department,
                           selected_location=location_filter,
                           selected_type=job_type)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)


@app.route('/job/<int:job_id>/apply', methods=['GET', 'POST'])
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()

        if not name or not email:
            flash('Name and email are required.', 'error')
            return render_template('apply.html', job=job)

        application = Application(
            job_id=job_id,
            name=name,
            email=email,
            phone=phone,
            cover_letter=cover_letter
        )
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted! We will be in touch soon.', 'success')
        return redirect(url_for('index'))

    return render_template('apply.html', job=job)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_jobs()
    app.run(host='0.0.0.0', port=5000, debug=True)
