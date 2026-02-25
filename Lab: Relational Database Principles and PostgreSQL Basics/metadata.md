# Project Plan

## Basic Information
- **ID:** b1de82c3-2535-42c9-a2bb-130f11c3b0a4
- **Name:** Lab: Relational Database Principles and PostgreSQL Basics
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: Relational Database Principles and PostgreSQL Basics
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-25T17:39:59.519592
- **Modified By:** rocky
- **Modified On:** 2026-02-25T17:41:14.209711
- **Published On:** N/A

## User prompt
- Generate lab for module: Relational Database Principles and PostgreSQL Basics
---

## Problem Statement
- Problem Statement: Building a Student Performance Management Database for an Educational Institution using PostgreSQL and Python

Scenario: Real-World Role

As a newly hired Data Analyst at EduPro Academy, a mid-sized educational institution, you have been tasked with improving the management and analysis of student performance data. The current process relies on scattered spreadsheets that make reporting and analytics slow and error-prone. To address this, you will lead the design and implementation of a foundational relational database system using PostgreSQL. This system will store, manipulate, and retrieve simulated student performance data, laying the groundwork for future data-driven initiatives. You will also demonstrate basic integration with Python, empowering other departments with easy data access for reporting.

Problem Context

Educational institutions increasingly rely on data-driven decisions, such as identifying students who may need academic support or tracking the effectiveness of courses over time. However, without a robust backend system, extracting insights is difficult and manual. Your challenge is to establish this backbone, ensuring the system is scalable, reliable, and accessible for future analytics and reporting.

Objective

Your objective is to:

- Set up a PostgreSQL database to manage student performance data.
- Design and implement a relational schema for students, courses, enrollments, and grades.
- Load and manipulate a sample (simulated) dataset resembling real academic records.
- Implement basic CRUD (Create, Read, Update, Delete) operations via SQL scripts.
- Execute interactive queries to retrieve actionable insights (e.g., top performers, students at risk, average grades per course).
- Apply error handling best practices in SQL and Python.
- Connect and query the database using Python (with either psycopg2 or SQLAlchemy).
- Prepare an instructor-friendly lab manual to support teaching and reproducibility of your steps.

Assumptions about Target Audience

This project is designed for beginner to intermediate learners who:
- Are familiar with basic relational database concepts (tables, keys, SQL basics).
- Have entry-level experience with Python programming.
- Have not worked with production-scale databases or advanced SQL constructs.
- Are interested in practical, hands-on database applications relevant to real-world educational institutions.

All resources and instructions are strictly limited to concepts found in relational database theory, relational modeling, SQL CRUD operations, querying fundamentals, basic error handling, and Python-PostgreSQL connectivity. No advanced database concepts, security concerns, or machine learning techniques are required.

Time Expectation

The tasks are chunked to be achievable within 4-6 hours, ideal for a lab, in-class project, or structured self-study module.

Task Breakdown and Stepwise Instructions

1. PostgreSQL Setup (30 minutes)
   - Provide clear, step-by-step instructions to install PostgreSQL and access the psql CLI or setup a GUI tool (e.g., pgAdmin).
   - Guide the learner to create a new database user and a database named student_performance.

2. Data Modeling & Schema Creation (45 minutes)
   - Outline an ER diagram (provided in lab manual) for four main entities: Students, Courses, Enrollments, and Grades.
   - Provide a complete SQL script to:
     - Create tables with appropriate primary keys, foreign keys, and basic types.
     - Insert constraints to ensure data integrity (e.g., unique email addresses, valid grade range).
   - Example snippet:
     ```sql
     CREATE TABLE students (
         student_id SERIAL PRIMARY KEY,
         first_name VARCHAR(50),
         last_name VARCHAR(50),
         email VARCHAR(100) UNIQUE NOT NULL,
         registration_date DATE
     );
     -- Similar DDL for courses, enrollments, grades...
     ```

3. Load Simulated Academic Dataset (30 minutes)
   - Supply a CSV or SQL file with sample student, course, enrollment, and grade data (non-sensitive, simulated).
   - Step-by-step instructions to bulk load data (using COPY command or INSERT scripts).

4. CRUD Operations Script (45 minutes)
   - Provide an SQL script (with explanation) performing:
     - Adding new students/courses.
     - Recording new enrollments and updating grades.
     - Deleting a student and handling cascading deletions (e.g., remove enrollments).
     - Updating courses or correcting student info.
   - Explicitly showcase integrity constraints and how they operate.
   - Emphasize and demonstrate error handling best practices for SQL (e.g., handling UNIQUE or FOREIGN KEY violations).

5. Interactive SQL Queries (45 minutes)
   - Define 4-6 common educational queries, such as:
     - Retrieve all students enrolled in a particular course.
     - Calculate average grade per course and per student.
     - List students at risk (e.g., GPA below threshold).
     - Output top 3 performing courses based on average grades.
   - Each query comes with a guided explanation.
   - Include challenges for learners: “Modify the following query to display...” and include expected result sets for validation.

6. Error Handling Best Practices (20 minutes)
   - Short documentation and code samples to:
     - Catch and interpret common SQL errors (e.g., data type mismatch, constraint violations).
     - Use TRY...EXCEPT in Python with psycopg2 or SQLAlchemy to gracefully handle database exceptions.
   - Examples of rolling back transactions when errors occur.

7. Python Integration (psycopg2/SQLAlchemy) (1 hour)
   - Detailed steps to:
     - Install necessary Python libraries.
     - Connect to the PostgreSQL database.
     - Execute and fetch query results.
     - Perform simple data inserts and updates through Python scripts.
     - Handle exceptions, print informative messages.
     - (Optional) Use Pandas for result display.
   - Provide clean, annotated script templates for both psycopg2 and SQLAlchemy approaches.

8. Lab Environment/Manual for Instructors (30 minutes)
   - Dedicated instructor’s guide with:
     - Learning objectives mapped to each phase of the project.
     - Troubleshooting common issues (e.g., connection problems, constraint errors).
     - Sample solutions and expected outputs.
     - Suggestions for assessment, extension ideas, and formative feedback.
   - Checklist for completion and student self-evaluation prompts.

Learning Outcomes Addressed

Upon completing this project, learners will:
- Acquire foundational knowledge in relational database theory by designing a normalized schema for academic data and understanding its real-world application.
- Apply practical SQL and data modeling skills by authoring and executing table creation, data manipulation, and analytical queries on educational data.
- Develop confidence in basic database programming using Python by building scripts that interact with PostgreSQL, demonstrating CRUD operations, data retrieval, and robust error handling.

Clarity and Relevance

All steps and documentation are tailored for database beginners and early-career developers, with real-world relevance to education. No advanced features (like triggers, complex stored procedures, or advanced analytics) are required—ensuring a focus on essential, practical skills. All instructions, examples, and the simulated dataset remain strictly within the required scope (see Feature Set above). Provided tasks and queries are actionable, unambiguous, and build sequentially, culminating in a working, demonstrable education data management system.

Summary Table of Deliverables

| Task                                  | Learner Output                                              |
|----------------------------------------|------------------------------------------------------------|
| PostgreSQL Setup                       | Working local database and user account                     |
| Schema Creation                        | Script generating normalized tables and relationships       |
| Data Loading                           | Populated tables with realistic sample educational data     |
| CRUD SQL Script                        | File with documented Create/Read/Update/Delete examples     |
| Interactive Exercises                  | List of queries with learner-generated result screenshots   |
| Error Handling Practice                | Notes and code samples handling SQL and Python exceptions   |
| Python Integration                     | Python script(s) performing database access and updates     |
| Lab Manual (for instructors)           | PDF or doc with instructions, tips, and assessment rubrics  |

Estimated Completion Time: 4-6 hours.

All project assets (scripts, dataset, instructions) to be bundled for easy classroom or remote learning deployment.

By the end of this project, each learner will have implemented a functional foundation for student data management in education—building job-ready skills in relational database modeling, SQL, and Python-based database programming, strictly within the defined scope.
---

# Project Specification

## Overview
- **Tech Domain:** Database Systems
- **Tech Subdomain:** Relational Databases & PostgreSQL
- **Application Domain:** education
- **Application Subdomain:** relational_database_principles_postgresql_basics
- **Target Audience:** beginner to intermediate learners in database concepts, students or early-career developers
- **Difficulty Level:** Beginner
- **Time Constraints:** 4-6 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- PostgreSQL setup instructions
- Sample healthcare/finance dataset (simulated, not real domain files)
- SQL script for schema and CRUD sample
- Interactive exercises and queries
- Error handling best practices in SQL
- Instructions for connecting and querying with Python (psycopg2/SQLAlchemy)
- Lab environment/manual for instructors


## Global Learning Outcomes
- Acquire foundational knowledge in relational database theory
- Apply practical SQL and data modeling skills
- Develop confidence in basic database programming using Python


## Acceptance Criteria
- PostgreSQL can be installed and run on a local environment
- Learners can define and create a normalized schema (with at least two related tables)
- Demonstrate CRUD operations via SQL scripts and verify results using SELECT statements
- Sample Python script successfully connects and queries the local database
- Provided test cases for the SQL queries and data integrity pass successfully


## Deliverables
- Step-by-step PostgreSQL setup guide
- Sample database schema and SQL scripts
- Practice exercise scripts (SQL and Python)
- Automated test scripts for database setup and queries
- Instructor solution set


---

# Projects

  
  ## 1. Database Systems (Relational Databases & PostgreSQL)

  ### Tech Stack
  - **Language:**  ()
  - **Framework:**  ()

  ### Testing
  
  - **Unit Testing:** pytest (Coverage: No)
  
  
  
  - **Integration Testing:** pytest (Coverage: No)
  
  
  
  - **End-to-End/API Testing:** Not Specified
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Python 3.x installed
  
  - Basic understanding of shell/command line
  
  - No prior database experience required
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Understand database normalization and schema design
  
  - Execute core SQL statements in PostgreSQL
  
  - Manage basic data operations (CRUD) in a PostgreSQL environment
  
  - Connect Python applications to PostgreSQL databases
  
  - Translate simple business rules into database tables and queries
  
  - Troubleshoot typical SQL errors
  

  ### Feature Set
  
  - End-to-end walkthrough of setting up PostgreSQL locally
  
  - Schema and data definition examples for a simple scenario (non-domain specific)
  
  - Practice queries for data manipulation and retrieval
  
  - Python examples for executing SQL against PostgreSQL
  
  - Instructor solutions and test scripts
  

  ### API Documentation
  
  - **API Documentation:** Not Specified
  

  ### Output Resource Type
  - code

  
