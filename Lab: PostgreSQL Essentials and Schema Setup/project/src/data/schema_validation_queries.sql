-- 1. SELECT query joining students and enrollments to retrieve each student's enrolled courses
SELECT s.student_id, s.first_name, s.last_name, s.email, c.course_name, c.department, e.enrollment_status, e.grade
FROM public.students s
JOIN public.enrollments e ON s.student_id = e.student_id
JOIN public.courses c ON e.course_id = c.course_id
ORDER BY s.student_id, c.course_name;

-- 2. SELECT query listing all courses and counting the number of students enrolled in each
SELECT c.course_id, c.course_name, c.department, COUNT(e.enrollment_id) AS student_count
FROM public.courses c
LEFT JOIN public.enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name, c.department
ORDER BY c.course_id;

-- 3. Attempt to perform an insert that violates a defined constraint (duplicate email)
-- This should fail due to unique constraint on students.email
INSERT INTO public.students (first_name, last_name, date_of_birth, email, active, created_at, updated_at)
VALUES ('Deborah', 'Adams', '2000-01-01', 'alice.nguyen1@example.edu', TRUE, NOW(), NOW());

-- 4. Attempt to perform an insert that violates a defined constraint (out-of-bounds course credits)
-- This should fail due to CHECK constraint on courses.credits (must be >0 and <=100)
INSERT INTO public.courses (course_name, department, credits, is_active, created_at, updated_at)
VALUES ('Intro to Impossible Math', 'Mathematics', 150, TRUE, NOW(), NOW());

-- 5. Observed/Expected Output Explanation --
-- 1. Students and their enrolled courses:
-- +------------+------------+-----------+----------------------------+------------------------------+-------------------+-------------------+-------+
-- | student_id | first_name | last_name | email                      | course_name                  | department        | enrollment_status | grade |
-- |------------|------------|-----------|----------------------------|------------------------------|-------------------|-------------------|-------|
-- | 1          | Alice      | Nguyen    | alice.nguyen1@example.edu  | Introduction to Data Science | Computer Science  | completed         | A     |
-- | 1          | Alice      | Nguyen    | alice.nguyen1@example.edu  | Business Communication       | Business          | enrolled          | NULL  |
-- | 2          | Brian      | Odonnell  | b.odonnell2024@example.edu | Introduction to Data Science | Computer Science  | dropped           | NULL  |
-- | 3          | Carlos     | Fernandez | c.fernandez@example.edu    | Business Communication       | Business          | enrolled          | NULL  |
-- +------------+------------+-----------+----------------------------+------------------------------+-------------------+-------------------+-------+
--
-- 2. Courses and student counts:
-- +-----------+------------------------------+-------------------+---------------+
-- | course_id | course_name                  | department        | student_count |
-- |-----------|------------------------------|-------------------|---------------|
-- | 1         | Introduction to Data Science | Computer Science  | 2             |
-- | 2         | Business Communication       | Business          | 2             |
-- +-----------+------------------------------+-------------------+---------------+
--
-- 3. Attempted duplicate email insert error (PostgreSQL example):
-- ERROR:  duplicate key value violates unique constraint "students_email_key"
-- DETAIL:  Key (email)=(alice.nguyen1@example.edu) already exists.
--
-- 4. Attempted out-of-bounds course credits insert error:
-- ERROR:  new row for relation "courses" violates check constraint "courses_credits_check"
-- DETAIL:  Failing row contains (Intro to Impossible Math, Mathematics, 150, ...)
--
-- Explanation:
-- - The joins correctly relate students to their enrollments and courses, as demonstrated by expected outputs.
-- - Aggregation over enrollments counts students for each course.
-- - Constraint violations are promptly caught by the RDBMS, with specific error messages, demonstrating schema enforcement.
-- - These queries and violations are shown in a simple, stepwise manner suitable for beginners to understand.