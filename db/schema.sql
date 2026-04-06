CREATE DATABASE IF NOT EXISTS academic_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE academic_db;

-- Table des utilisateurs (tous rôles confondus)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) DEFAULT '',
    last_name VARCHAR(100) DEFAULT '',
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'professor', 'student') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des classes
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rattachement étudiant <-> classe
CREATE TABLE IF NOT EXISTS class_students (
    class_id INT NOT NULL,
    student_id INT NOT NULL,
    PRIMARY KEY (class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Rattachement professeur <-> classe
CREATE TABLE IF NOT EXISTS class_professors (
    class_id INT NOT NULL,
    professor_id INT NOT NULL,
    PRIMARY KEY (class_id, professor_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Évaluations créées par un prof dans une classe
CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    class_id INT NOT NULL,
    professor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Notes : une note par étudiant par évaluation
CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    evaluation_id INT NOT NULL,
    grade DECIMAL(5,2) NOT NULL CHECK (grade >= 0 AND grade <= 20),
    UNIQUE KEY unique_grade (student_id, evaluation_id),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Emplois du temps
CREATE TABLE IF NOT EXISTS schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    day_of_week ENUM('lundi','mardi','mercredi','jeudi','vendredi') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);