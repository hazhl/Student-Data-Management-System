-- Create Database
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Drop existing tables to ensure a clean start
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

-- Create students table
CREATE TABLE students (
    student_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    national_id VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male','Female','Other') NOT NULL,
    department VARCHAR(100) NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    gpa DECIMAL(4,2) DEFAULT 0.00 CHECK (gpa >= 0.00 AND gpa <= 4.00),
    status ENUM('Active','Graduated','Suspended') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create courses table
CREATE TABLE courses (
    course_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    credit_hours TINYINT UNSIGNED NOT NULL CHECK (credit_hours >= 1 AND credit_hours <= 6),
    instructor_name VARCHAR(120) NOT NULL,
    department VARCHAR(100) NOT NULL,
    semester ENUM('Fall','Spring','Summer') NOT NULL,
    academic_year YEAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create enrollments table (Junction Table)
CREATE TABLE enrollments (
    enrollment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    student_id INT UNSIGNED NOT NULL,
    course_id INT UNSIGNED NOT NULL,
    grade DECIMAL(5,2) NULL CHECK (grade >= 0.00 AND grade <= 100.00),
    letter_grade ENUM('A','B','C','D','F','Incomplete') NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id)
) ENGINE=InnoDB;

-- Seed data for students (10 records)
INSERT INTO students (first_name, last_name, national_id, email, date_of_birth, gender, department, enrollment_date, gpa, status) VALUES
('Alice', 'Smith', 'NAT001', 'alice.smith@example.com', '2004-05-15', 'Female', 'Computer Science', '2023-09-01', 3.85, 'Active'),
('Bob', 'Jones', 'NAT002', 'bob.jones@example.com', '2003-11-22', 'Male', 'Computer Science', '2022-09-01', 3.12, 'Active'),
('Charlie', 'Brown', 'NAT003', 'charlie.brown@example.com', '2004-02-10', 'Male', 'Information Systems', '2023-09-01', 2.95, 'Active'),
('Diana', 'Prince', 'NAT004', 'diana.prince@example.com', '2002-08-04', 'Female', 'Computer Science', '2021-09-01', 3.98, 'Graduated'),
('Evan', 'Wright', 'NAT005', 'evan.wright@example.com', '2003-01-30', 'Male', 'Information Technology', '2022-09-01', 3.40, 'Active'),
('Fiona', 'Gallagher', 'NAT006', 'fiona.gallagher@example.com', '2004-07-21', 'Female', 'Computer Science', '2023-09-01', 2.10, 'Suspended'),
('George', 'Brooks', 'NAT007', 'george.brooks@example.com', '2003-03-18', 'Male', 'Computer Science', '2022-09-01', 3.25, 'Active'),
('Hannah', 'Abbott', 'NAT008', 'hannah.abbott@example.com', '2004-12-12', 'Female', 'Information Technology', '2023-09-01', 3.65, 'Active'),
('Ian', 'Malcolm', 'NAT009', 'ian.malcolm@example.com', '2002-10-05', 'Male', 'Information Systems', '2021-09-01', 3.50, 'Graduated'),
('Julia', 'Roberts', 'NAT010', 'julia.roberts@example.com', '2003-06-25', 'Female', 'Computer Science', '2022-09-01', 3.70, 'Active');

-- Seed data for courses (5 records)
INSERT INTO courses (course_code, course_name, credit_hours, instructor_name, department, semester, academic_year) VALUES
('CS101', 'Introduction to Computer Science', 4, 'Dr. John Doe', 'Computer Science', 'Fall', 2026),
('CS202', 'Data Structures & Algorithms', 4, 'Dr. Alan Turing', 'Computer Science', 'Spring', 2026),
('CS303', 'Database Management Systems', 3, 'Dr. Grace Hopper', 'Information Systems', 'Fall', 2026),
('CS404', 'Software Engineering', 3, 'Prof. Ada Lovelace', 'Computer Science', 'Spring', 2026),
('CS505', 'Cloud Computing & Virtualization', 3, 'Dr. Tim Berners-Lee', 'Information Technology', 'Fall', 2026);

-- Seed data for enrollments (17 records)
INSERT INTO enrollments (student_id, course_id, grade, letter_grade) VALUES
(1, 1, 95.00, 'A'),
(1, 3, 91.50, 'A'),
(2, 1, 88.00, 'B'),
(2, 2, 82.50, 'B'),
(3, 2, 79.00, 'C'),
(3, 4, 94.00, 'A'),
(4, 1, 98.00, 'A'),
(4, 5, 96.50, 'A'),
(5, 3, 85.00, 'B'),
(5, 5, 89.00, 'B'),
(6, 4, 72.00, 'C'),
(6, 1, 65.00, 'D'),
(7, 2, 84.00, 'B'),
(7, 3, 78.50, 'C'),
(8, 5, 90.00, 'A'),
(9, 3, 88.00, 'B'),
(10, 4, 95.00, 'A');
