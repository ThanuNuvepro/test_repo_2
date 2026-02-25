## What you will do:

**Problem Statement**  
Scenario-Based Problem Statement for Beginner PostgreSQL Developers: Student Course Management System

Scenario Description:
You are a Junior Database Developer at an EdTech startup that is building a platform for managing students, courses, and enrollments in coding bootcamps. The engineering team is in the early stages of system development and needs an efficient relational database schema for the core data. As someone new to PostgreSQL, you are tasked with setting up the foundation for this system using PostgreSQL essentials.

Your supervisor expects you to deliver a fully functioning schema with practical demonstrations of fundamental database concepts. Your contribution will serve as a base for future application developers and data analysts in the company.

Project Objective:
Design and implement the initial PostgreSQL database for the Student Course Management System, covering essential database management skills. This project includes: installing PostgreSQL, creating a normalized schema, demonstrating various data types, enforcing constraints for data integrity, inserting representative sample records, and crafting SELECT queries that verify your design.

Project Details & Requirements:

1. PostgreSQL Installation Steps (30 minutes)
   - Download and install the latest stable version of PostgreSQL on your development machine.
   - Document each step taken, including initializing a database cluster and accessing the PostgreSQL prompt.
   - Create a new database student_course_db dedicated to this project.

2. Schema and Table Creation Scripts (30 minutes)
   - Design the schema to represent the following entities:
     - Students (basic personal info)
     - Courses (offered by the platform)
     - Enrollments (which students enroll in which courses)
   - Write PostgreSQL SQL scripts to create the following tables:
     - students
     - courses
     - enrollments
   - Ensure your scripts are clean, formatted, and ready to execute in psql or any PostgreSQL client.

3. Data Types Demonstration (15 minutes)
   - Appropriately select native PostgreSQL data types for each column according to the data stored (e.g., VARCHAR, INTEGER, DATE, BOOLEAN).
   - Include at least one example of a numeric, character, date, and boolean type across your tables.
   - Comment your CREATE TABLE scripts to explain your data type choices.

4. Defining and Enforcing Constraints (15 minutes)
   - In your CREATE TABLE statements, apply the following constraints:
     - Primary keys for each table (e.g., student_id, course_id, enrollment_id)
     - Foreign key constraints in enrollments to reference students and courses
     - NOT NULL on fields that must always contain values (e.g., student names, course titles)
     - UNIQUE constraint on student email in the students table
     - CHECK constraint on course credits column (e.g., credits must be between 1 and 10)
   - Comment on each constraint to clarify its purpose.

5. Sample Data Insertion (15 minutes)
   - Provide INSERT INTO scripts that add at least:
     - Three students (varying personal data)
     - Two courses (distinct course properties)
     - Four enrollments (ensuring at least one student is enrolled in multiple courses and one course has multiple students)
   - Ensure all constraints are respected in your sample data.

6. Sample SELECT Queries Verifying Schema (15 minutes)
   - Write SELECT statements that:
     - Retrieve all students and their enrolled courses (using JOINs)
     - List all courses with the number of students enrolled in each
     - Verify that constraints work (e.g., attempt to insert an invalid record, comment on the expected failure)
   - Document the output/expected results for each query.

Deliverables:
- A single SQL file (or set of files) with:
  - All CREATE TABLE statements
  - Inline comments explaining schema choices, data types, and constraints
  - All sample INSERT INTO statements
  - All SELECT queries as described
- A brief install-and-execution guide summarizing how to set up PostgreSQL and run your scripts from scratch.

Learning Outcomes Alignment:
- You will demonstrate understanding of basic relational database design, normalization, and entity relationships.
- You will gain hands-on experience with PostgreSQL installation and command-line utilities.
- You will learn how to define schemas, select appropriate data types, and enforce real-world data integrity constraints.
- You will practice data insertion and querying basics with sample business-like data.

Target Audience & Assumptions:
- This project is tailored for beginner developers and students with little to no prior exposure to PostgreSQL or relational databases.
- Assumes familiarity with fundamental programming concepts but limited SQL experience.
- All tasks and expectations are appropriate for a 2–3 hour beginner hands-on learning session.

Time Constraints:
- PostgreSQL installation and initial setup: 30 minutes
- Schema, data types, and constraint scripting: 1 hour
- Sample data entry and query writing: 30 minutes
- Documentation and submission: 30 minutes

Summary:
You are to set up a core student-course-enrollment schema in PostgreSQL, fully documenting your reasoning. You will apply and demonstrate key PostgreSQL features through scripts and queries that model actual developer education data and workflows. No steps go beyond essential schema setup or conceptual boundaries. This practical assignment will equip you with foundational PostgreSQL and database design skills directly applicable to developer education and system initialization.

Completion within the 2–3 hour timeframe will provide a solid introduction to PostgreSQL’s essentials, preparing you for more advanced database development scenarios.

---

## What you will learn:

- Install and configure PostgreSQL locally

- Create and manage schemas and tables

- Apply data types and integrity constraints

- Populate tables with sample data

- Validate schema with SQL queries


---

## What you need to know:

- Python 3.x installed

- Basic SQL knowledge


---

## Modules and Activities:


### 📦 Relational Modeling and Schema Design for Student Course Management


#### ✅ Analyze Requirements and Normalize Core Entities

**🎯 Goal:**  
Define and normalize tables for students, courses, and enrollments to ensure an efficient relational schema.

**🛠 Instructions:**  

- Review the given scenario and list the essential data fields for students, courses, and enrollments.

- Determine relationships between entities and decide the best way to normalize the schema to avoid redundancy.

- Map out the tables and their relationships, noting which fields should be primary keys and where foreign keys are required.

- Choose the most appropriate data types (numeric, character, date, boolean) for each field to demonstrate a broad range of PostgreSQL types.


**📤 Expected Output:**  
A clearly defined list of tables, fields (with chosen data types), and their relationships, reflecting a normalized design suited for the scenario.

---

#### ✅ Cheat Sheet Creation: Essential PostgreSQL Commands

**🎯 Goal:**  
Prepare a quick-reference cheat sheet featuring PostgreSQL commands relevant for schema setup and data management.

**🛠 Instructions:**  

- List the minimal but essential PostgreSQL commands for database, table, and data management relevant to the student course management system.

- Include example syntax for CREATE DATABASE, CREATE TABLE (with constraints), INSERT, SELECT, and simple JOINs.

- Summarize usage tips for each command for a beginner audience.


**📤 Expected Output:**  
A concise, beginner-friendly cheat sheet listing and briefly explaining necessary PostgreSQL commands for the given project.

---



### 📦 Schema Implementation: Table Creation and Constraints


#### ✅ Write Scripts to Create Schema and Tables with Constraints

**🎯 Goal:**  
Translate the normalized data model into CREATE TABLE statements with appropriate data types and constraints.

**🛠 Instructions:**  

- Using your schema design, write out the CREATE TABLE statements for students, courses, and enrollments.

- Apply a PRIMARY KEY for each table and foreign keys in the enrollments table.

- Add NOT NULL, UNIQUE, and CHECK constraints as required for each column to enforce business rules and data integrity.

- Ensure that each column’s data type aligns with the expected data and scenario requirements.

- Comment your choices, especially on constraints and data types, for clarity.


**📤 Expected Output:**  
A set of clean, commented table creation scripts reflecting an optimized, constraint-driven PostgreSQL schema suitable for the use case.

---



### 📦 Sample Data Insertion and Query Validation


#### ✅ Insert Representative Sample Data

**🎯 Goal:**  
Populate the students, courses, and enrollments tables with realistic sample records respecting all constraints.

**🛠 Instructions:**  

- Prepare three unique student records capturing a variety of data points.

- Create two distinct courses with valid, realistic properties.

- Insert at least four enrollments, ensuring one student is enrolled in multiple courses and one course includes multiple students.

- Double-check that all input values adhere to the defined primary, foreign key, unique, not null, and check constraints.


**📤 Expected Output:**  
Sample insert statements for each table that successfully execute and populate the schema with meaningful data, without causing constraint errors.

---

#### ✅ Formulate and Execute Schema Validation Queries

**🎯 Goal:**  
Demonstrate schema correctness and relational integrity through SELECT queries.

**🛠 Instructions:**  

- Write a SELECT query joining students and enrollments to retrieve each student's enrolled courses.

- Write a SELECT query listing all courses and counting the number of students enrolled in each.

- Attempt to perform an insert that violates a defined constraint (such as a duplicate email or out-of-bounds course credits) and observe the error message.

- Record the actual or expected query outputs and explain the results briefly.

- Ensure your queries and observations are clear for a beginner to understand.


**📤 Expected Output:**  
A set of SELECT query results showing correct joins and aggregations, as well as at least one observed error from a constraint violation, demonstrating schema enforcement.

---


