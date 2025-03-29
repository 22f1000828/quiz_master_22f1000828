from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from .models import User, Subject, Chapter, Quiz, Question, Score
from . import db

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('routes.admin_dashboard'))
            return redirect(url_for('routes.user_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('routes.register'))

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
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.home'))

@bp.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('routes.home'))

    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@bp.route('/admin/subject', methods=['POST'])
def create_subject():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    subject = Subject(
        name=request.form.get('name'),
        description=request.form.get('description')
    )
    db.session.add(subject)
    db.session.commit()
    flash('Subject created successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/chapter/<int:subject_id>', methods=['POST'])
def create_chapter(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    chapter = Chapter(
        name=request.form.get('name'),
        description=request.form.get('description'),
        subject_id=subject_id
    )
    db.session.add(chapter)
    db.session.commit()
    flash('Chapter created successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/quiz/<int:chapter_id>', methods=['POST'])
def create_quiz(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    quiz = Quiz(
        chapter_id=chapter_id,
        date_of_quiz=datetime.strptime(request.form.get('date_of_quiz'), '%Y-%m-%dT%H:%M'),
        time_duration=int(request.form.get('time_duration')),
        remarks=request.form.get('remarks')
    )
    db.session.add(quiz)
    db.session.commit()
    flash('Quiz created successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/question/<int:quiz_id>', methods=['POST'])
def create_question(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    question = Question(
        quiz_id=quiz_id,
        question_text=request.form.get('question_text'),
        option1=request.form.get('option1'),
        option2=request.form.get('option2'),
        option3=request.form.get('option3'),
        option4=request.form.get('option4'),
        correct_option=int(request.form.get('correct_option'))
    )
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    subjects = Subject.query.all()
    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template('user/dashboard.html', subjects=subjects, scores=scores)

@bp.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if not session.get('user_id'):
        return redirect(url_for('routes.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    if not session.get('user_id'):
        return redirect(url_for('routes.login'))

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
    return redirect(url_for('routes.user_dashboard'))

@bp.route('/admin/subject/<int:subject_id>/delete', methods=['POST'])
def delete_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/subject/<int:subject_id>/edit', methods=['POST'])
def edit_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form.get('name')
    subject.description = request.form.get('description')
    db.session.commit()
    flash('Subject updated successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/chapter/<int:chapter_id>/edit', methods=['POST'])
def edit_chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = request.form.get('name')
    chapter.description = request.form.get('description')
    db.session.commit()
    flash('Chapter updated successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

@bp.route('/admin/chapter/<int:chapter_id>/delete', methods=['POST'])
def delete_chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))