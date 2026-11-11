from pathlib import Path
import sqlite3
from flask import Flask, flash, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.secret_key = 'local-class-project-change-this-secret'
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'student individual university system.db'

HTML = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>University Management System</title>
<style>
body{font-family:Arial,sans-serif;background:#f3f6fb;margin:0;color:#17243b}
main{max-width:1000px;margin:35px auto;padding:0 20px}h1{color:#173b72}
nav a{display:inline-block;padding:10px 15px;background:#e0e9f7;margin:0 8px 15px 0;border-radius:7px;text-decoration:none;color:#173b72}
section{background:white;border-radius:12px;padding:20px;margin:15px 0;box-shadow:0 2px 9px #dce3ee}
input,select,button{padding:10px;margin:5px;border:1px solid #bcc9dc;border-radius:6px}
button{background:#174b92;color:white;cursor:pointer}button.danger{background:#a52d36}
table{border-collapse:collapse;width:100%}th,td{padding:11px;text-align:left;border-bottom:1px solid #e3e8f0}th{background:#edf3fc}
.notice{padding:10px;background:#fff1cb;border-radius:6px}form.inline{display:inline}
</style></head><body><main><h1>University Management System</h1>
<nav><a href="{{ url_for('home') }}">Students</a><a href="{{ url_for('courses') }}">Courses</a><a href="{{ url_for('enrollments') }}">Enrollments</a></nav>
{% for message in get_flashed_messages() %}<p class="notice">{{ message }}</p>{% endfor %}
{% if page == 'students' %}
<section><h2>Add Student</h2><form action="{{ url_for('add_student') }}" method="post">
<input name="first_name" placeholder="First name" maxlength="50" required>
<input name="last_name" placeholder="Last name" maxlength="50" required>
<input name="email" type="email" placeholder="Email" maxlength="100" required>
<button>Add Student</button></form></section>
<section><h2>Students ({{ students|length }})</h2><table><tr><th>ID</th><th>First name</th><th>Last name</th><th>Email</th><th>Action</th></tr>
{% for s in students %}<tr><td>{{ s.StudentID }}</td><td>{{ s.FirstName }}</td><td>{{ s.LastName }}</td><td>{{ s.Email }}</td>
<td><form class="inline" method="post" action="{{ url_for('delete_student', student_id=s.StudentID) }}" onsubmit="return confirm('Delete this student?')"><button class="danger">Delete</button></form></td></tr>
{% else %}<tr><td colspan="5">No students yet. Add one above.</td></tr>{% endfor %}</table></section>
{% elif page == 'courses' %}
<section><h2>Add Course</h2><form action="{{ url_for('add_course') }}" method="post">
<input name="code" placeholder="Course code (e.g. CS101)" maxlength="10" required>
<input name="credits" type="number" min="1" max="12" placeholder="Credits" required><button>Add Course</button></form></section>
<section><h2>Courses</h2><table><tr><th>ID</th><th>Course code</th><th>Credits</th></tr>
{% for c in courses %}<tr><td>{{ c.CourseID }}</td><td>{{ c.CourseCode }}</td><td>{{ c.Credits }}</td></tr>
{% else %}<tr><td colspan="3">No courses yet.</td></tr>{% endfor %}</table></section>
{% elif page == 'enrollments' %}
<section><h2>Enroll Student in Course</h2><form method="post" action="{{ url_for('add_enrollment') }}">
<select name="student_id" required><option value="">Choose student</option>{% for s in students %}<option value="{{ s.StudentID }}">{{ s.FirstName }} {{ s.LastName }}</option>{% endfor %}</select>
<select name="course_id" required><option value="">Choose course</option>{% for c in courses %}<option value="{{ c.CourseID }}">{{ c.CourseCode }}</option>{% endfor %}</select>
<button>Enroll</button></form></section>
<section><h2>Enrollments</h2><table><tr><th>ID</th><th>Student</th><th>Course</th><th>Date</th></tr>
{% for e in enrollments %}<tr><td>{{ e.EnrollmentID }}</td><td>{{ e.FirstName }} {{ e.LastName }}</td><td>{{ e.CourseCode }}</td><td>{{ e.RegistrationDate }}</td></tr>
{% else %}<tr><td colspan="4">No enrollments yet.</td></tr>{% endfor %}</table></section>
{% endif %}
</main></body></html>'''


def verify_database():
    """Fail early instead of allowing SQLite to create a blank database."""
    if not DATABASE.is_file():
        raise FileNotFoundError(
            f"Missing database: {DATABASE}\n"
            "Make sure the database has this EXACT filename and is next to db APPS.py."
        )
    with sqlite3.connect(f"file:{DATABASE.as_posix()}?mode=ro", uri=True) as db:
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        required = {'Students', 'Courses', 'Enrollments'}
        if not required.issubset(tables):
            raise RuntimeError(
                f"Wrong database file: {DATABASE}\n"
                f"Tables found: {sorted(tables)}; required: {sorted(required)}.\n"
                "Your original data has NOT been changed."
            )
        return db.execute('SELECT COUNT(*) FROM Students').fetchone()[0]


def connect():
    verify_database()
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db


@app.route('/')
def home():
    with connect() as db:
        students = db.execute('SELECT * FROM Students ORDER BY StudentID').fetchall()
    return render_template_string(HTML, page='students', students=students)


@app.post('/students/add')
def add_student():
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    if not first or not last or not email:
        flash('Please complete all fields.')
    else:
        try:
            with connect() as db:
                db.execute('INSERT INTO Students (FirstName, LastName, Email) VALUES (?, ?, ?)', (first, last, email))
            flash('Student added successfully.')
        except sqlite3.IntegrityError:
            flash('Could not add student: email may already exist.')
    return redirect(url_for('home'))


@app.post('/students/delete/<int:student_id>')
def delete_student(student_id):
    try:
        with connect() as db:
            db.execute('DELETE FROM Students WHERE StudentID = ?', (student_id,))
        flash('Student deleted.')
    except sqlite3.IntegrityError:
        flash('Cannot delete a student who has enrollments.')
    return redirect(url_for('home'))


@app.route('/courses')
def courses():
    with connect() as db:
        rows = db.execute('SELECT * FROM Courses ORDER BY CourseID').fetchall()
    return render_template_string(HTML, page='courses', courses=rows)


@app.post('/courses/add')
def add_course():
    code = request.form.get('code', '').strip()
    try:
        credits = int(request.form.get('credits', ''))
        if not code or not 1 <= credits <= 12:
            raise ValueError()
        with connect() as db:
            db.execute('INSERT INTO Courses (CourseCode, Credits) VALUES (?, ?)', (code, credits))
        flash('Course added successfully.')
    except ValueError:
        flash('Enter a course code and credits from 1 to 12.')
    except sqlite3.IntegrityError:
        flash('That course code already exists.')
    return redirect(url_for('courses'))


@app.route('/enrollments')
def enrollments():
    with connect() as db:
        students = db.execute('SELECT * FROM Students ORDER BY FirstName').fetchall()
        course_rows = db.execute('SELECT * FROM Courses ORDER BY CourseCode').fetchall()
        rows = db.execute('''SELECT e.EnrollmentID, e.RegistrationDate,
                s.FirstName, s.LastName, c.CourseCode
                FROM Enrollments e JOIN Students s ON e.StudentID = s.StudentID
                JOIN Courses c ON e.CourseID = c.CourseID
                ORDER BY e.EnrollmentID''').fetchall()
    return render_template_string(HTML, page='enrollments', students=students, courses=course_rows, enrollments=rows)


@app.post('/enrollments/add')
def add_enrollment():
    try:
        student_id = int(request.form.get('student_id', ''))
        course_id = int(request.form.get('course_id', ''))
        with connect() as db:
            existing = db.execute('SELECT 1 FROM Enrollments WHERE StudentID=? AND CourseID=?', (student_id, course_id)).fetchone()
            if existing:
                flash('Student is already enrolled in that course.')
            else:
                db.execute("INSERT INTO Enrollments (StudentID, CourseID, RegistrationDate) VALUES (?, ?, date('now'))", (student_id, course_id))
                flash('Enrollment added successfully.')
    except (ValueError, sqlite3.IntegrityError):
        flash('Please select a valid student and course.')
    return redirect(url_for('enrollments'))


if __name__ == '__main__':
    print('Using database:', DATABASE)
    count = verify_database()
    print(f'Database verified. Student records: {count}')
    app.run(debug=True)
