# Academix — Student Data Management System

A fully containerized, three-tier CRUD web application for managing student records, course catalogs, and class enrollments. Built using **Python Flask**, **SQLAlchemy ORM**, **MySQL 8.0**, and **Nginx** as a reverse proxy.

---

## 🏗️ System Architecture

The application is fully orchestrated using **Docker Compose** and consists of three isolated services:

```mermaid
graph TD
    User["User / Web Browser"] -->|HTTP (Port 80)| Nginx["Nginx Reverse Proxy"]
    
    subgraph Docker Network (frontend)
        Nginx -->|Proxy Pass (Port 5000)| Flask["Flask Web Server"]
        Nginx -.->|Serves Static Files| Static["/app/static/"]
    end
    
    subgraph Docker Network (backend)
        Flask -->|MySQL Link (Port 3306)| MySQL["MySQL 8.0 Database"]
        MySQL -.->|Volume| DBVolume["mysql_data"]
        MySQL -.->|Init Script| SQLInit["db/init.sql"]
    end
```

1.  **Nginx (Web Server & Reverse Proxy)**:
    *   Listens on port `80` (only exposed port on the host machine).
    *   Directly serves static assets (CSS, JS, images) from a shared read-only volume.
    *   Forwards dynamic web traffic to the application server.
2.  **Flask (Application Layer)**:
    *   Python-based Flask application implementing MVC patterns.
    *   SQLAlchemy ORM for database queries and transaction management.
    *   Implements full validation (e.g. GPA range checks, email format checks, unique constraint checks) and automatically calculates letter grades from numeric scores.
3.  **MySQL 8.0 (Data Layer)**:
    *   Maintains three tables (`students`, `courses`, and `enrollments`) with correct relational keys, checks, and `ON DELETE CASCADE` constraints.
    *   Initialized automatically on build using `db/init.sql`, pre-populating the database with **10 students**, **5 courses**, and **17 enrollments**.
    *   Data is persisted across container teardowns using a named Docker volume (`mysql_data`).

---

## ✨ Features

*   **Premium Web UI**: Responsive dark-glassmorphism design styled with custom color palettes, sleek tables, and hover micro-animations.
*   **Students Management**: Add, update, view, and delete student records. Tracks names, National ID, GPA, gender, major, date of birth, and status (Active/Graduated/Suspended).
*   **Courses Catalog**: Track course codes, credit hours, instructors, semester, and academic year.
*   **Enrollment Relationships**: Enroll students in courses, update decimal grades (0.00 - 100.00) with automatic letter grade calculation ('A', 'B', 'C', etc.), and drop students from classes.
*   **Safety Guards**: JavaScript confirmation prompts prevent accidental deletion of students, courses, or registrations.
*   **Cascading Integrity**: Deleting a student or course automatically purges associated enrollment records at the database level.

---

## 🛠️ Installation & Setup

### Prerequisites
*   [Docker](https://www.docker.com/products/docker-desktop) installed and running.
*   [Git](https://git-scm.com/) (optional, for version control).

### Step 1: Clone the Repository
```bash
git clone https://github.com/hazhl/Student-Data-Management-System.git
cd Student-Data-Management-System
```

### Step 2: Configure Environment Variables
Create a `.env` file in the **project root directory** (refer to `.gitignore` to ensure this is never committed):
```env
DB_NAME=student_db
DB_USER=student_user
DB_PASSWORD=student_pass
DB_ROOT_PASSWORD=student_root_pass
```

*Note: A matching `.env` is also located in `app/.env` for local (non-Docker) Flask development.*

### Step 3: Run the Stack
Run Docker Compose to build the application image and start the full orchestration in the background:
```bash
docker compose up --build -d
```

### Step 4: Access the Portal
Open your browser and navigate to:
👉 **[http://localhost](http://localhost)**

---

## 📁 Project Directory Structure

```text
├── app/
│   ├── static/
│   │   └── css/
│   │       └── style.css          # Design system & responsive styles
│   ├── template/                  # Flask Jinja2 HTML templates
│   │   ├── layout.html            # Base structural template
│   │   ├── dashboard.html         # Homepage metrics & shortcuts
│   │   ├── students.html          # Student CRUD & filter forms
│   │   ├── courses.html           # Course CRUD & catalog listing
│   │   └── enrollments.html       # Student registrations & grading
│   ├── .dockerignore              # Docker context exclusions
│   ├── .env                       # App local variables
│   ├── app.py                     # Flask models, controllers, and routing
│   ├── Dockerfile                 # Application multi-stage configuration
│   └── requirements.txt           # Python application dependencies
├── db/
│   └── init.sql                   # Database table structure & seed data
├── nginx/
│   └── nginx.conf                 # Reverse proxy & static serving config
├── .gitignore                     # Git tracking exclusions
├── docker-compose.yml             # Service orchestration manifest
└── README.md                      # Documentation
```

---

## 🧹 Stopping and Cleaning Up
To shut down the running containers:
```bash
docker compose down
```

To shut down and wipe the database volume (resetting it to the default seed data on the next launch):
```bash
docker compose down -v
```
