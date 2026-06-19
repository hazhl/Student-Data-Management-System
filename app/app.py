from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='template')
app.secret_key = os.getenv("SECRET_KEY", "academix-secure-session-key-2026")

# Database configuration from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================================================
# Grading Helper Function
# =========================================================================

def calculate_letter_grade(grade_val):
    if grade_val is None:
        return None
    try:
        g = float(grade_val)
        if g >= 90:
            return 'A'
        elif g >= 80:
            return 'B'
        elif g >= 70:
            return 'C'
        elif g >= 60:
            return 'D'
        elif g >= 0:
            return 'F'
        else:
            return 'Incomplete'
    except (ValueError, TypeError):
        return 'Incomplete'

# =========================================================================
# Database Models
# =========================================================================

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    gpa = db.Column(db.Numeric(4, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default='Active')

    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')

    def __init__(self, first_name, last_name, national_id, email, date_of_birth, gender, department, enrollment_date, gpa=0.00, status='Active'):
        self.first_name = first_name
        self.last_name = last_name
        self.national_id = national_id
        self.email = email
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.department = department
        self.enrollment_date = enrollment_date
        self.gpa = gpa
        self.status = status


class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    credit_hours = db.Column(db.Integer, nullable=False)
    instructor_name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)

    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

    def __init__(self, course_code, course_name, credit_hours, instructor_name, department, semester, academic_year):
        self.course_code = course_code
        self.course_name = course_name
        self.credit_hours = credit_hours
        self.instructor_name = instructor_name
        self.department = department
        self.semester = semester
        self.academic_year = academic_year


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    grade = db.Column(db.Numeric(5, 2), nullable=True)
    letter_grade = db.Column(db.String(15), nullable=True)
    enrolled_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __init__(self, student_id, course_id, grade=None, letter_grade=None):
        self.student_id = student_id
        self.course_id = course_id
        self.grade = grade
        self.letter_grade = letter_grade

# =========================================================================
# Controllers & Routes
# =========================================================================

# --- Dashboard Home ---
@app.route("/")
def home():
    try:
        student_count = Student.query.count()
        course_count = Course.query.count()
        enrollment_count = Enrollment.query.count()
    except Exception as e:
        student_count = 0
        course_count = 0
        enrollment_count = 0
        flash(f"Database connection error: {str(e)}", "error")
        
    return render_template(
        "dashboard.html", 
        student_count=student_count, 
        course_count=course_count, 
        enrollment_count=enrollment_count
    )


# --- Students CRUD ---
@app.route("/students")
def list_students():
    search = request.args.get("search", "")
    department = request.args.get("department", "")
    status = request.args.get("status", "")
    
    query = Student.query
    
    if search:
        query = query.filter(
            (Student.first_name.like(f"%{search}%")) |
            (Student.last_name.like(f"%{search}%")) |
            (db.cast(Student.student_id, db.String).like(f"%{search}%")) |
            (Student.national_id.like(f"%{search}%")) |
            (Student.email.like(f"%{search}%"))
        )
    if department:
        query = query.filter(Student.department == department)
    if status:
        query = query.filter(Student.status == status)
        
    students = query.order_by(Student.student_id.desc()).all()
    departments = [d[0] for d in db.session.query(Student.department).distinct().all() if d[0]]
    
    return render_template("students.html", students=students, departments=departments)


@app.route("/students/new", methods=["POST"])
def create_student():
    try:
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        national_id = request.form.get("national_id")
        email = request.form.get("email")
        date_of_birth = datetime.strptime(request.form.get("date_of_birth"), "%Y-%m-%d").date()
        gender = request.form.get("gender")
        department = request.form.get("department")
        enrollment_date = datetime.strptime(request.form.get("enrollment_date"), "%Y-%m-%d").date()
        gpa = float(request.form.get("gpa", 0.00))
        status = request.form.get("status", "Active")
        
        # Validations for uniqueness
        if Student.query.filter_by(national_id=national_id).first():
            flash("Error: National ID already exists!", "error")
            return redirect(url_for("list_students"))
        if Student.query.filter_by(email=email).first():
            flash("Error: Email address already exists!", "error")
            return redirect(url_for("list_students"))
            
        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            email=email,
            date_of_birth=date_of_birth,
            gender=gender,
            department=department,
            enrollment_date=enrollment_date,
            gpa=gpa,
            status=status
        )
        db.session.add(new_student)
        db.session.commit()
        flash("Student registered successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding student: {str(e)}", "error")
    return redirect(url_for("list_students"))


@app.route("/students/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    try:
        national_id = request.form.get("national_id")
        email = request.form.get("email")
        
        # Uniqueness checks
        dup_nat = Student.query.filter(Student.national_id == national_id, Student.student_id != student_id).first()
        if dup_nat:
            flash("Error: National ID belongs to another student!", "error")
            return redirect(url_for("list_students"))
            
        dup_email = Student.query.filter(Student.email == email, Student.student_id != student_id).first()
        if dup_email:
            flash("Error: Email belongs to another student!", "error")
            return redirect(url_for("list_students"))
            
        student.first_name = request.form.get("first_name")
        student.last_name = request.form.get("last_name")
        student.national_id = national_id
        student.email = email
        student.date_of_birth = datetime.strptime(request.form.get("date_of_birth"), "%Y-%m-%d").date()
        student.gender = request.form.get("gender")
        student.department = request.form.get("department")
        student.enrollment_date = datetime.strptime(request.form.get("enrollment_date"), "%Y-%m-%d").date()
        student.gpa = float(request.form.get("gpa", 0.00))
        student.status = request.form.get("status")
        
        db.session.commit()
        flash("Student profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating student: {str(e)}", "error")
    return redirect(url_for("list_students"))


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash(f"Student {student.first_name} {student.last_name} deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting student: {str(e)}", "error")
    return redirect(url_for("list_students"))


# --- Courses CRUD ---
@app.route("/courses")
def list_courses():
    search = request.args.get("search", "")
    department = request.args.get("department", "")
    semester = request.args.get("semester", "")
    
    query = Course.query
    if search:
        query = query.filter(
            (Course.course_name.like(f"%{search}%")) |
            (Course.course_code.like(f"%{search}%")) |
            (Course.instructor_name.like(f"%{search}%"))
        )
    if department:
        query = query.filter(Course.department == department)
    if semester:
        query = query.filter(Course.semester == semester)
        
    courses = query.order_by(Course.course_code).all()
    departments = [c[0] for c in db.session.query(Course.department).distinct().all() if c[0]]
    return render_template("courses.html", courses=courses, departments=departments)


@app.route("/courses/new", methods=["POST"])
def create_course():
    try:
        course_code = request.form.get("course_code")
        course_name = request.form.get("course_name")
        credit_hours = int(request.form.get("credit_hours"))
        instructor_name = request.form.get("instructor_name")
        department = request.form.get("department")
        semester = request.form.get("semester")
        academic_year = int(request.form.get("academic_year"))
        
        if Course.query.filter_by(course_code=course_code).first():
            flash("Error: Course code already exists!", "error")
            return redirect(url_for("list_courses"))
            
        new_course = Course(
            course_code=course_code,
            course_name=course_name,
            credit_hours=credit_hours,
            instructor_name=instructor_name,
            department=department,
            semester=semester,
            academic_year=academic_year
        )
        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding course: {str(e)}", "error")
    return redirect(url_for("list_courses"))


@app.route("/courses/edit/<int:course_id>", methods=["POST"])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        course_code = request.form.get("course_code")
        
        dup_code = Course.query.filter(Course.course_code == course_code, Course.course_id != course_id).first()
        if dup_code:
            flash("Error: Course code belongs to another course!", "error")
            return redirect(url_for("list_courses"))
            
        course.course_code = course_code
        course.course_name = request.form.get("course_name")
        course.credit_hours = int(request.form.get("credit_hours"))
        course.instructor_name = request.form.get("instructor_name")
        course.department = request.form.get("department")
        course.semester = request.form.get("semester")
        course.academic_year = int(request.form.get("academic_year"))
        
        db.session.commit()
        flash("Course updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating course: {str(e)}", "error")
    return redirect(url_for("list_courses"))


@app.route("/courses/delete/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash(f"Course {course.course_code} deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting course: {str(e)}", "error")
    return redirect(url_for("list_courses"))


# --- Enrollments CRUD ---
@app.route("/enrollments")
def list_enrollments():
    search = request.args.get("search", "")
    course_id = request.args.get("course_id", "")
    
    query = Enrollment.query.join(Student).join(Course)
    
    if search:
        query = query.filter(
            (Student.first_name.like(f"%{search}%")) |
            (Student.last_name.like(f"%{search}%")) |
            (db.cast(Student.student_id, db.String).like(f"%{search}%")) |
            (Course.course_code.like(f"%{search}%"))
        )
    if course_id:
        query = query.filter(Enrollment.course_id == int(course_id))
        
    enrollments = query.order_by(Enrollment.enrollment_id.desc()).all()
    
    students = Student.query.order_by(Student.first_name).all()
    courses = Course.query.order_by(Course.course_code).all()
    
    return render_template("enrollments.html", enrollments=enrollments, students=students, courses=courses)


@app.route("/enrollments/new", methods=["POST"])
def enroll_student():
    try:
        student_id = int(request.form.get("student_id"))
        course_id = int(request.form.get("course_id"))
        
        grade_raw = request.form.get("grade", "").strip()
        grade = float(grade_raw) if grade_raw else None
        letter_grade = calculate_letter_grade(grade)
        
        if Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first():
            flash("Error: Student is already enrolled in this course!", "error")
            return redirect(url_for("list_enrollments"))
            
        new_enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            grade=grade,
            letter_grade=letter_grade
        )
        db.session.add(new_enrollment)
        db.session.commit()
        flash("Student enrolled successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error enrolling student: {str(e)}", "error")
    return redirect(url_for("list_enrollments"))


@app.route("/enrollments/edit-grade/<int:enrollment_id>", methods=["POST"])
def edit_grade(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    try:
        grade_raw = request.form.get("grade", "").strip()
        grade = float(grade_raw) if grade_raw else None
        letter_grade = calculate_letter_grade(grade)
        
        enrollment.grade = grade
        enrollment.letter_grade = letter_grade
        db.session.commit()
        flash("Grade updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating grade: {str(e)}", "error")
    return redirect(url_for("list_enrollments"))


@app.route("/enrollments/delete/<int:enrollment_id>", methods=["POST"])
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    try:
        db.session.delete(enrollment)
        db.session.commit()
        flash("Student dropped from course successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error dropping student: {str(e)}", "error")
    return redirect(url_for("list_enrollments"))


if __name__ == "__main__":
    app.run(debug=True)