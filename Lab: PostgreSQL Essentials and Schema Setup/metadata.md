# Project Plan

## Basic Information
- **ID:** 099b4ae2-3d40-44c4-86b1-8d847a054293
- **Name:** Lab: PostgreSQL Essentials and Schema Setup
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: PostgreSQL Essentials and Schema Setup
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-25T17:27:39.360508
- **Modified By:** rocky
- **Modified On:** 2026-02-25T17:28:12.536392
- **Published On:** N/A

## User prompt
- Generate lab for module: PostgreSQL Essentials and Schema Setup
---

## Problem Statement
- Scenario-Based Problem Statement for Beginner PostgreSQL Developers: Student Course Management System

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

# Project Specification

## Overview
- **Tech Domain:** Database Management
- **Tech Subdomain:** PostgreSQL
- **Application Domain:** developer_education
- **Application Subdomain:** postgresql_essentials_and_schema_setup
- **Target Audience:** Beginner developers or students looking to learn PostgreSQL fundamentals and schema design
- **Difficulty Level:** Beginner
- **Time Constraints:** 2-3 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- PostgreSQL installation steps
- Schema and table creation scripts
- Data types demonstration
- Defining and enforcing constraints
- Sample data insertion
- Sample SELECT queries verifying schema


## Global Learning Outcomes
- Understand basic relational database concepts
- Gain hands-on experience with PostgreSQL
- Learn schema and table creation with constraints
- Practice SQL data insertion and querying


## Acceptance Criteria
- The user can install and launch PostgreSQL on their local machine.
- SQL scripts successfully create the intended database schema with required tables and relationships.
- Appropriate primary and foreign key constraints are in place.
- Data can be inserted without errors and queried successfully.
- Testing scripts validate schema creation and basic query results.
- Instructions are beginner-friendly and self-contained.


## Deliverables
- Step-by-step lab manual or instructions
- PostgreSQL schema creation SQL scripts
- Python script demonstrating PostgreSQL connection and schema operations
- Sample data and queries for validation
- Testing instructions and expected outputs


---

# Projects

  
  ## 1. Database Management (PostgreSQL)

  ### Tech Stack
  - **Language:** SQL (PostgreSQL 15+)
  - **Framework:** psycopg2 ()

  ### Testing
  
  - **Unit Testing:** Not Specified
  
  
  
  - **Integration Testing:**  (Coverage: No)
  
  
  
  - **End-to-End/API Testing:** Not Specified
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Python 3.x installed
  
  - Basic SQL knowledge
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Install and configure PostgreSQL locally
  
  - Create and manage schemas and tables
  
  - Apply data types and integrity constraints
  
  - Populate tables with sample data
  
  - Validate schema with SQL queries
  

  ### Feature Set
  
  - End-to-end schema setup scripts
  
  - Cheat sheet for PostgreSQL commands
  
  - Sample dataset and query samples
  

  ### API Documentation
  
  - **API Documentation:** Not Specified
  

  ### Output Resource Type
  - code

  
