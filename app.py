from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------
# Database Models
# -------------------------
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), nullable=False)  # "Present" or "Absent"

# -------------------------
# Create tables automatically
# -------------------------
with app.app_context():
    db.create_all()

# -------------------------
# Routes
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
    for entry in data['attendance']:
        new_attendance = Attendance(
            student_id=entry['student_id'],
            date=date.today(),
            status=entry['status']
        )
        db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance recorded successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
