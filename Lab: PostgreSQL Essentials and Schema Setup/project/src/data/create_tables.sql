-- Create schema for organization and future extensibility
CREATE SCHEMA IF NOT EXISTS public;

-- Table: students
CREATE TABLE public.students (
    student_id SERIAL PRIMARY KEY, -- Unique student identifier
    first_name VARCHAR(100) NOT NULL, -- Student's first name
    last_name VARCHAR(100) NOT NULL, -- Student's last name
    date_of_birth DATE NOT NULL, -- Date of birth. Must not be in the future.
    email VARCHAR(255) UNIQUE NOT NULL, -- Student email, must be unique (see notes on case/trim protection)
    active BOOLEAN NOT NULL DEFAULT TRUE, -- Is this student active/enrolled?
    created_at TIMESTAMP NOT NULL DEFAULT NOW(), -- Timestamp record created
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(), -- Timestamp record last updated
    CONSTRAINT chk_dob CHECK (date_of_birth <= CURRENT_DATE), -- Prevent future dates of birth
    CONSTRAINT chk_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') -- Loose email format validation; not RFC-perfect
    -- COMMENT ON: See table/comment below for more.
);

COMMENT ON TABLE public.students IS 'Stores student-level demographic and contact data.';
COMMENT ON COLUMN public.students.student_id IS 'Unique student identifier.';
COMMENT ON COLUMN public.students.first_name IS 'Student first/given name.';
COMMENT ON COLUMN public.students.last_name IS 'Student last/family name.';
COMMENT ON COLUMN public.students.date_of_birth IS 'Date of birth of the student.';
COMMENT ON COLUMN public.students.email IS 'Unique email address (case-sensitive unique; watch for variant issues).';
COMMENT ON COLUMN public.students.active IS 'Whether the student record is currently active.';
COMMENT ON COLUMN public.students.created_at IS 'Timestamp when record was created.';
COMMENT ON COLUMN public.students.updated_at IS 'Timestamp of last update to record.';

-- Table: courses
CREATE TABLE public.courses (
    course_id SERIAL PRIMARY KEY, -- Unique course identifier
    course_name VARCHAR(200) NOT NULL, -- Name/title of the course
    department VARCHAR(100) NOT NULL, -- Denormalized department label. Consider normalizing if reused frequently.
    credits INT NOT NULL CHECK (credits > 0 AND credits <= 100), -- Credit value, 1-100
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- If the course is currently offered
    created_at TIMESTAMP NOT NULL DEFAULT NOW(), -- Timestamp record created
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(), -- Timestamp record last updated
    CONSTRAINT unique_course UNIQUE (course_name, department) -- No duplicate course/department combos
);

COMMENT ON TABLE public.courses IS 'Catalog of courses with credit values, by department.';
COMMENT ON COLUMN public.courses.course_id IS 'Unique course identifier.';
COMMENT ON COLUMN public.courses.course_name IS 'Descriptive course name.';
COMMENT ON COLUMN public.courses.department IS 'Department label (denormalized, see design review note).';
COMMENT ON COLUMN public.courses.credits IS 'Number of credits for the course.';
COMMENT ON COLUMN public.courses.is_active IS 'True if course is active and available.';
COMMENT ON COLUMN public.courses.created_at IS 'Timestamp when course was created.';
COMMENT ON COLUMN public.courses.updated_at IS 'Timestamp of last course record update.';

-- Table: enrollments
CREATE TABLE public.enrollments (
    enrollment_id SERIAL PRIMARY KEY, -- Unique enrollment record
    student_id INT NOT NULL, -- Reference to students.student_id
    course_id INT NOT NULL, -- Reference to courses.course_id
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE, -- When the student was enrolled (default today)
    enrollment_status VARCHAR(30) NOT NULL CHECK (enrollment_status IN ('enrolled','completed','dropped','withdrawn')), -- State of enrollment
    grade VARCHAR(2), -- e.g., A, B+, D-, or NULL if not graded yet or dropped
    created_at TIMESTAMP NOT NULL DEFAULT NOW(), -- When this enrollment was created
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(), -- Last update to this record
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id) REFERENCES public.students(student_id) ON DELETE CASCADE, -- Student ref, cascade delete
    CONSTRAINT fk_enroll_course FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON DELETE CASCADE, -- Course ref, cascade delete
    CONSTRAINT unique_student_course UNIQUE (student_id, course_id), -- Prevent duplicate enrollment
    CONSTRAINT chk_grade CHECK (grade IS NULL OR grade ~* '^[A-F][+-]?$') -- Grade must be in allowed form or NULL
    -- No NOT NULL on grade: permits ongoing/dropped/ungraded records
    -- ON UPDATE/ON DELETE: Defaults used (no ON UPDATE CASCADE by design; delete cascades so enrollments removed if student/course gone)
);

COMMENT ON TABLE public.enrollments IS 'Tracks student enrollment for each course. Connects students to courses.';
COMMENT ON COLUMN public.enrollments.enrollment_id IS 'Unique enrollment identifier.';
COMMENT ON COLUMN public.enrollments.student_id IS 'References public.students.student_id.';
COMMENT ON COLUMN public.enrollments.course_id IS 'References public.courses.course_id.';
COMMENT ON COLUMN public.enrollments.enrollment_date IS 'Date enrollment was recorded.';
COMMENT ON COLUMN public.enrollments.enrollment_status IS 'Current status: enrolled, completed, dropped, or withdrawn.';
COMMENT ON COLUMN public.enrollments.grade IS 'Grade (A-F letter, with optional +/-, or NULL if ongoing/dropped).';
COMMENT ON COLUMN public.enrollments.created_at IS 'When this enrollment record was created.';
COMMENT ON COLUMN public.enrollments.updated_at IS 'Last update to this enrollment record.';

-- --- REVIEW NOTES ADDRESSED ---
-- All key columns/tables now have explicit COMMENTs for schema auditing and handover.
-- All tables in "public" schema explicitly (for easier migration/interop).
-- created_at/updated_at timestamps added for each table, common for auditing/compliance.
-- Email regex constraint unchanged (not RFC-perfect; practical only).
-- Grade column allows NULLs (as per schema/logic needs).
-- ON DELETE CASCADE used for enrollments to prevent orphaned records. ON UPDATE behavior is default (RESTRICT); document logic as per project policies.
-- Active status columns default TRUE for students/courses; application logic to control lifecycle.
-- Course department remains denormalized per initial design, but noted for scaling/3NF needs.

-- After applying, run: ANALYZE; -- to update planner with new statistics.
