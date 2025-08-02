from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

app = Flask(__name__)

# -------------------------
# Database Configuration
# -------------------------
uri = os.environ.get('DATABASE_URL', 'sqlite:///database.db')  # fallback for local testing

# Render provides postgres:// but SQLAlchemy with psycopg3 needs postgresql+psycopg://
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql+psycopg://", 1)
elif uri.startswith("postgresql://") and "+psycopg" not in uri:
    uri = uri.replace("postgresql://", "postgresql+psycopg://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# Database Models
# -------------------------
class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), nullable=False)  # "Present" or "Absent"

# -------------------------
# Initialize Database
# -------------------------
with app.app_context():
    db.create_all()

# -------------------------
# Main Routes
# -------------------------
@app.route('/')
def index():
    classes = Class.query.all()
    return render_template('index.html', classes=classes)

@app.route('/students/<int:class_id>')
def get_students(class_id):
    students = Student.query.filter_by(class_id=class_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in students])

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    for entry in data.get('attendance', []):
        new_attendance = Attendance(
            student_id=entry['student_id'],
            date=date.today(),
            status=entry['status']
        )
        db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance recorded successfully!'})

# -------------------------
# Admin Routes
# -------------------------
@app.route('/admin', methods=['GET'])
def admin():
    classes = Class.query.all()
    return render_template('admin.html', classes=classes)

@app.route('/admin/add_class', methods=['POST'])
def add_class():
    class_name = request.form.get('class_name')
    if class_name:
        new_class = Class(name=class_name)
        db.session.add(new_class)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_student', methods=['POST'])
def add_student():
    student_name = request.form.get('student_name')
    student_email = request.form.get('student_email')
    class_id = request.form.get('class_id')

    if student_name and class_id:
        new_student = Student(name=student_name, email=student_email, class_id=class_id)
        db.session.add(new_student)
        db.session.commit()
    return redirect(url_for('admin'))

# -------------------------
# Run App
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
