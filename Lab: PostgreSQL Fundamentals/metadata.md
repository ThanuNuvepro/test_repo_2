# Project Plan

## Basic Information
- **ID:** 596a626a-1a77-4f82-8ca3-6b286ebd810c
- **Name:** Lab: PostgreSQL Fundamentals
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: PostgreSQL Fundamentals
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-26T03:15:21.434301
- **Modified By:** rocky
- **Modified On:** 2026-02-26T03:16:41.362461
- **Published On:** N/A

## User prompt
- Generate lab for module: PostgreSQL Fundamentals
---

## Problem Statement
- Project Problem Statement: Education Enrollment Database Lab Scenario

Scenario: 

Role and Real-World Context  
You are a Junior Database Developer working for EdTech Solutions, a company that provides technology support to local educational institutions. The company has tasked you with creating and managing a relational database to streamline student enrollment, course registrations, and faculty assignments for a university. Recently, the university’s administration realized that many processes are handled manually using spreadsheets, which causes errors and data loss. Your project will lay the groundwork for a more robust, accurate, and retrievable system by leveraging PostgreSQL.

Project Objective  
Your goal is to design, create, and administer a PostgreSQL-based relational database to manage student enrollments, course details, and faculty assignments. You will practice and reinforce database fundamentals by performing all operations in a hands-on lab environment using a pre-configured PostgreSQL instance. This project will involve creating tables, performing CRUD (Create, Read, Update, Delete) operations, importing and modifying sample datasets, performing simple basic administration tasks such as backups and restores, and responding to guided self-assessment questions after each module section.

Project Tasks and Features (to be completed in 2 hours)

1. Hands-On Lab Setup  
   - Access a hands-on lab environment with a pre-configured PostgreSQL instance.  
   - Familiarize yourself with the environment’s login process and basic command line tools.

2. Step-by-Step Database Creation and Manipulation  
   - Follow detailed, scaffolded instructions to:
     - Create a new database called university_enrollment.
     - Define and create tables: students, courses, faculty, enrollments, and course_assignments.  
     - Specify primary keys, foreign keys, and column data types aligning with beginner-level best practices. All scripts and schema definitions are provided as templates.

3. Sample Dataset for Experimentation  
   - Load provided sample CSV files or SQL inserts for each table:
     - Students: ID, name, email, date of birth.
     - Courses: ID, title, credits.
     - Faculty: ID, name, department.
     - Enrollments: enrollment_id, student_id, course_id, enrollment_date.
     - Course_assignments: assignment_id, faculty_id, course_id, assignment_date.
   - Verify data using SELECT queries.

4. Practice Exercises for CRUD Operations  
   - Complete practical exercise scripts to:
     - Add new students, courses, and faculty using INSERT.  
     - Query enrollment information to find which students are in which courses.
     - Update student or course information using UPDATE.  
     - Delete enrollments or courses using DELETE, observing referential integrity constraints.  
   - Each operation comes with stepwise instructions and example queries.

5. Self-Assessment Questions After Every Module Section  
   - After finishing each module (database/table creation, data import, CRUD operations), answer a small set of self-assessment questions to verify your comprehension (e.g., "What command did you use to add a new student?").

6. Scaffolded SQL Scripts for Guided Learning  
   - Utilize provided starter SQL script templates for all steps.  
   - Complete scripts by filling in specified sections throughout the hands-on exercises.

7. Manual and Script-Based Data Backup/Restore Steps  
   - Perform a basic manual backup of your university_enrollment database using pg_dump, following guided instructions.  
   - Restore the backup into a new database named university_enrollment_backup using psql.

Learning Outcomes  
By the end of this project, you will be able to:

- Gain hands-on experience with PostgreSQL fundamentals by designing and interacting with a real database for educational data.
- Confidently execute SQL commands for database setup, querying, updates, deletions, and data integrity enforcement.
- Demonstrate your grasp of basic database administration by performing both script-based and manual backup and restoration procedures.
- Self-assess and explain your process and reasoning at every stage, reinforcing learning and practical confidence.

Target Audience Alignment and Assumptions  
This project is specifically designed for Beginner database learners: students, junior developers, and those with little or no experience with PostgreSQL. All terminology, sample data, and instructions assume no prior exposure to advanced database concepts or administrative tasks. The language is clear and direct, avoiding jargon beyond the fundamental SQL and PostgreSQL functions taught in introductory curriculum.

Timeline  
• 0–10 min: Lab environment orientation and database creation  
• 10–30 min: Table creation with scaffolded scripts  
• 30–50 min: Sample data import and verification  
• 50–90 min: Structured practice exercises (CRUD operations, referential integrity)  
• 90–110 min: Manual/script-based backup and restore procedures  
• 110–120 min: Complete final self-assessment and submit results

Actionable Steps for Project Execution  
1. Log into your pre-configured PostgreSQL lab environment.
2. Follow written instructions to create the database and tables.
3. Use scaffolded scripts to import and manipulate the sample dataset.
4. Work through guided CRUD exercises with real data.
5. Periodically answer comprehension and reflection questions embedded in instructions.
6. Perform and verify database backup/restore procedures as instructed.
7. Confirm your learning by reviewing self-assessment results.
8. Submit your completed lab logs as project documentation.

Strict Feature and Learning Outcome Adherence  
Every element of the project strictly follows these features:

- Lab environment with pre-configured PostgreSQL instance
- Step-by-step instructions for database creation and manipulation
- Practice exercises for CRUD tasks
- Experimentation with a sample education-related dataset
- Section-by-section self-assessment questions
- Scaffolded SQL scripts to guide and reinforce learning
- Both manual and script-based backup/restore demonstrations

And directly leads to:

- Hands-on experience with PostgreSQL fundamentals
- Confidence using SQL in a real-world context
- Foundational understanding of core administration tasks

Project Relevance  
This project provides practical, resume-ready experience in using PostgreSQL to address real problems in educational data management, ensuring learners not only know what to do, but why and how, all within a focused, scaffolded, and achievable laboratory timeframe.

End of Problem Statement.
---

# Project Specification

## Overview
- **Tech Domain:** Database Fundamentals
- **Tech Subdomain:** PostgreSQL
- **Application Domain:** education
- **Application Subdomain:** postgresql_fundamentals_lab
- **Target Audience:** Beginner database learners, students, and junior developers
- **Difficulty Level:** Beginner
- **Time Constraints:** 2 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- Hands-on lab environment with pre-configured PostgreSQL instance
- Step-by-step lab instructions for database creation and manipulation
- Practice exercises for CRUD operations
- Sample dataset for experimentation
- Self-assessment questions after every module section
- Scaffolded SQL scripts for guided learning
- Manual and script-based data backup/restore steps


## Global Learning Outcomes
- Hands-on experience with PostgreSQL fundamentals
- Confidence in executing SQL commands in a real-world system
- Understanding basic database administration tasks


## Acceptance Criteria
- Learner can set up and connect to a local PostgreSQL server using testuser/Testuser123$
- All CRUD operations function correctly on example tables
- Primary and foreign key constraints are properly implemented
- User management steps (grant/revoke permissions) are followed and verified
- Backups can be created and restored successfully using lab scripts
- Self-assessment questions are attempted and sample solutions provided


## Deliverables
- Lab manual with step-by-step instructions (Markdown or PDF)
- Sample SQL scripts for each exercise
- Pre-populated database dump for practice
- Answers or hints for scenario-based self-assessment questions


---

# Projects

  
  ## 1. Database Fundamentals (PostgreSQL)

  ### Tech Stack
  - **Language:**  ()
  - **Framework:**  ()

  ### Testing
  
  - **Unit Testing:**  (Coverage: No)
  
  
  
  - **Integration Testing:**  (Coverage: No)
  
  
  
  - **End-to-End/API Testing:** Not Specified
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Understanding of what a database is
  
  - Access to a computer capable of running PostgreSQL
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Ability to set up and connect to a PostgreSQL database server
  
  - Skills in creating and managing tables/schemas
  
  - Proficiency in performing CRUD operations using SQL in PostgreSQL
  
  - Understanding constraints and their importance
  
  - Being able to back up and restore a PostgreSQL database
  
  - Basic user administration in PostgreSQL
  

  ### Feature Set
  
  - Guided lab exercises
  
  - Practice SQL scripts
  
  - Realistic scenario-based tasks
  
  - Step-by-step instructions for backup/restore and permission management
  

  ### API Documentation
  
  - **API Documentation:** Not Specified
  

  ### Output Resource Type
  - code

  
