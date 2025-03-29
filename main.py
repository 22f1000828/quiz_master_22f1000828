
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # in minutes
    remarks = db.Column(db.Text)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='admin@admin.com').first():
        admin = User(
            username='admin@admin.com',
            password='admin123',  # In production, use proper password hashing
            full_name='Administrator',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form.get('username'),
            password=request.form.get('password'),
            full_name=request.form.get('full_name'),
            qualification=request.form.get('qualification'),
            dob=datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        return redirect(url_for('home'))
    
    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@app.route('/admin/subject', methods=['POST'])
def create_subject():
    if request.method == 'POST':
        subject = Subject(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    subjects = Subject.query.all()
    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template('user/dashboard.html', subjects=subjects, scores=scores)

@app.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = session['user_id']
    score = 0
    
    for question in quiz.questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and int(user_answer) == question.correct_option:
            score += 1
    
    quiz_score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        score=score
    )
    db.session.add(quiz_score)
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {score}/{len(quiz.questions)}', 'success')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
