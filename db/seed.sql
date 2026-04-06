USE academic_db;

INSERT INTO users (username, password, role) VALUES
('admin1',    '$2b$12$OI.Z0UiJ55JB4WmVIPRpQegTyeZ2On09zsEjrbr8/Va31b5DMr7Z6', 'admin'),
('Bala',      '$2b$12$OI.Z0UiJ55JB4WmVIPRpQegTyeZ2On09zsEjrbr8/Va31b5DMr7Z6', 'professor'),
('Nayar',     '$2b$12$OI.Z0UiJ55JB4WmVIPRpQegTyeZ2On09zsEjrbr8/Va31b5DMr7Z6', 'student'),
('etudiant2', '$2b$12$OI.Z0UiJ55JB4WmVIPRpQegTyeZ2On09zsEjrbr8/Va31b5DMr7Z6', 'student');

INSERT INTO classes (name) VALUES
('GCS2-A'),
('GCS2-B');

-- Étudiants dans GCS2-A
INSERT INTO class_students (class_id, student_id) VALUES
(1, 3),
(1, 4);

-- ✅ Prof Bala assigné à GCS2-A
INSERT INTO class_professors (class_id, professor_id) VALUES
(1, 2);

INSERT INTO evaluations (name, class_id, professor_id) VALUES
('Projet Flask', 1, 2),
('Examen Sécu',  1, 2);
