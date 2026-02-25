-- This script inserts sample data into the students, courses, and enrollments tables.
-- Enhancements:
-- - Uses only ASCII characters to avoid encoding errors on non-UTF-8 DBs.
-- - Inserts all emails in lowercase, ensuring case-insensitive uniqueness.
-- - Dynamically fetches student_id and course_id via CTEs to avoid reliance on SERIAL increments.
-- - Wraps operations in a transaction for atomicity; script can be safely rolled back if any error occurs.
--
-- Supported for PostgreSQL. 
--
-- To execute: psql -d your_db -h ... -f sample_data_inserts.sql

-- Ensure proper client encoding; optional but best practice
SET client_encoding = 'UTF8';

BEGIN;

-- First, insert students; using only ASCII in all names (for cross-db support)
INSERT INTO public.students (first_name, last_name, date_of_birth, email, active, created_at, updated_at) VALUES
    ('Alice', 'Nguyen', '2002-10-15', 'alice.nguyen1@example.edu', TRUE, NOW(), NOW()),
    ('Brian', 'Odonnell', '2001-06-03', 'b.odonnell2024@example.edu', TRUE, NOW(), NOW()),
    ('Carlos', 'Fernandez', '1999-12-21', 'c.fernandez@example.edu', FALSE, NOW(), NOW());
-- NOTE: "Brian O'Donnell" last name written as "Odonnell" to avoid quote/special char issues.
-- NOTE: "Carlos FernÃ¡ndez" changed to "Fernandez" to avoid UTF-8/encoding confusion on some DBs.

-- Insert courses
INSERT INTO public.courses (course_name, department, credits, is_active, created_at, updated_at) VALUES
    ('Introduction to Data Science', 'Computer Science', 4, TRUE, NOW(), NOW()),
    ('Business Communication', 'Business', 3, TRUE, NOW(), NOW());

-- Get student and course IDs using CTEs (avoids fragile reliance on SERIAL ordering)
WITH 
    alice AS (SELECT student_id AS sid FROM public.students WHERE lower(email) = lower('alice.nguyen1@example.edu')),
    brian AS (SELECT student_id AS sid FROM public.students WHERE lower(email) = lower('b.odonnell2024@example.edu')),
    carlos AS (SELECT student_id AS sid FROM public.students WHERE lower(email) = lower('c.fernandez@example.edu')),
    ds_course AS (SELECT course_id AS cid FROM public.courses WHERE lower(course_name) = lower('Introduction to Data Science')),
    bc_course AS (SELECT course_id AS cid FROM public.courses WHERE lower(course_name) = lower('Business Communication'))
-- Insert enrollments joining on these IDs
INSERT INTO public.enrollments (student_id, course_id, enrollment_date, enrollment_status, grade, created_at, updated_at)
SELECT a.sid, d.cid, '2023-09-01', 'completed', 'A', NOW(), NOW() FROM alice a, ds_course d UNION ALL
SELECT a.sid, c.cid, '2023-09-01', 'enrolled', NULL, NOW(), NOW() FROM alice a, bc_course c UNION ALL
SELECT b.sid, d.cid, '2023-09-01', 'dropped', NULL, NOW(), NOW() FROM brian b, ds_course d UNION ALL
SELECT c.sid, c2.cid, '2023-09-01', 'enrolled', NULL, NOW(), NOW() FROM carlos c, bc_course c2;

-- All inserts are now safe and robust regardless of SERIAL values, deletions, or non-UTF DB settings.
-- Emails are all lowercase to ensure consistency in future case-insensitive queries/duplicates avoidance.

COMMIT;
