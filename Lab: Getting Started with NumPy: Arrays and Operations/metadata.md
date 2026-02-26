# Project Plan

## Basic Information
- **ID:** 24982a13-09f4-438d-aa2a-fbf50be1041e
- **Name:** Lab: Getting Started with NumPy: Arrays and Operations
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: Getting Started with NumPy: Arrays and Operations
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-26T16:00:43.062349
- **Modified By:** rocky
- **Modified On:** 2026-02-26T16:02:08.563176
- **Published On:** N/A

## User prompt
- Generate lab for module: Getting Started with NumPy: Arrays and Operations
---

## Problem Statement
- Problem Statement: Enhancing School Attendance Analysis Using NumPy Arrays

Scenario (Real-World Role-Based Project for Education Context):

You are a Junior Data Analyst working for a district education board. The district has been tasked with improving student attendance tracking across several schools. Consistent attendance is a major indicator of student engagement and educational outcomes. Currently, data is collected daily across schools in CSV files and needs to be processed and analyzed to spot trends, identify anomalies, and generate actionable insights for school administrators.

Your project is to build, document, and test a set of Jupyter Notebook-based tools using NumPy arrays for efficient data manipulation—and to support the district’s ongoing commitment to data-driven improvement.

Objective:

Develop an interactive Jupyter Notebook that guides users step-by-step through key NumPy array operations relevant to analyzing school attendance data. You will demonstrate the collection, cleaning, analysis, and basic reporting of attendance data from multiple schools and grades over a month using only NumPy arrays. By the end of the lab, you should deliver self-contained, executable examples, inline documentation, and automatically checked exercises that give beginners confidence in core NumPy skills and data analysis.

Project Details & Instructions:

Target Audience & Assumptions:
- This project is for beginners in data science and Python programming.
- You’ve completed basic Python tutorials but are new to NumPy and array operations.
- The environment is Jupyter Notebook.
- Expected completion time: About 2 hours.

Strict Feature Set:
- Hands-on lab in Jupyter Notebook.
- Step-by-step instructions and explanations for each operation.
- Self-contained, directly runnable examples.
- Practice exercises with instant, automatic answer checks.
- All documentation and explanations must be inline with the code.

Learning Outcomes Addressed:
- Ability to create and manipulate NumPy arrays.
- Understanding of broadcasting and advanced indexing to extract or summarize data.
- Confidence in using NumPy for basic educational data analysis.

Project Breakdown & Step-by-Step Guidance

Section 1: Getting Started and Data Preparation (20 minutes)
- Install and import NumPy.
- Generate synthetic attendance data for 5 schools, each with 4 classes, for 20 days (NumPy arrays of shape [5, 4, 20], values represent number of students present).
- Inline: Explain array creation (arange, random, reshape), data types, and dimensions.
- Exercise: Create an array representing attendance for a new school using np.ones or np.zeros and fill in data.

Section 2: Fundamental Array Operations (20 minutes)
- Demonstrate selecting data by school, class, and day using standard and advanced indexing (integer, slicing, boolean).
- Inline: Step-by-step explanations and code examples.
- Exercise: Extract data for Class 2 in School 3 for days 5–10. Automatic answer check compares against the correct slice.

Section 3: Data Cleaning and Broadcasting (20 minutes)
- Show how to simulate and detect missing data (e.g., some entries are -1 for absent data).
- Demonstrate replacement using boolean masking (set -1 to np.nan or a fill value).
- Use broadcasting to convert student counts to attendance rates as percentages (dividing by class size).
- Inline: Describe how shapes match up and broadcasting rules.
- Exercise: Replace all -1 values with the average for that class. Answers are auto-checked.

Section 4: Aggregate Analysis with NumPy (20 minutes)
- Calculate daily, class-wise, or school-wise attendance averages using axis arguments with np.mean, np.sum.
- Identify the day with the lowest overall attendance for each school.
- Inline: Explain each aggregation, include plotted charts using matplotlib (optional extension for visualization).
- Exercise: Find the highest average attendance class in School 4, checked by an assertion.

Section 5: Advanced Indexing & Reporting (20 minutes)
- Use advanced indexing to select all days where any class had <50% attendance.
- Sort and rank schools/classes by monthly average attendance.
- Inline: Explain difference between basic and advanced indexing.
- Document all findings with narrative text in markdown and code comments.
- Exercise: Write a function to return the lowest attendance day for any school. Provide a code cell for learners to fill in, with auto-check feedback.

Wrap-up and Reflection (10 minutes)
- Recap main NumPy array operations learned.
- Self-assessment checklist: Creating arrays, slicing, cleaning, broadcasting, basic data analysis.
- Recommendations for further exploration within educational data using Numpy.

Sample Structure in Notebook (for each subsection):
------------------------------------------------------
1. Explanation in markdown.
2. Code cell with a detailed, in-line documented example.
3. Practice Exercise cell.
4. Automatic answer check with assert or equivalence checks.
------------------------------------------------------

Time Breakdown:
- Data Preparation and Array Creation: 20 min
- Basic Manipulation (Slicing, Indexing): 20 min
- Cleaning/Broadcasting: 20 min
- Aggregation/Analysis: 20 min
- Advanced Indexing/Reporting: 20 min
- Review: 10 min

Deliverable:

A single, self-contained Jupyter Notebook named School_Attendance_NumPy_Lab.ipynb, containing:
- Fully commented, runnable code for all examples and tasks.
- Markdown and inline documentation after each cell.
- Practice problems and auto-check solutions at the end of each core section.
- Clear, beginner-friendly explanations tailored for complete NumPy newcomers.

Relevance & Practical Application:

By completing the project, you’ll have used real-world data science workflows for educational improvement, mastered NumPy’s core array operations, and built an analysis-ready template you could apply to similar challenges in schools, non-profits, or basic administrative data scenarios.

Your work will empower you to:
- Confidently create and manipulate NumPy arrays.
- Apply broadcasting and advanced indexing to analyze real educational data.
- Use NumPy for meaningful data summaries and trend detection—crucial skills for any aspiring data analyst in education.

Stay strictly within the defined tasks—no advanced machine learning, external data sources, or non-NumPy operations. This project is your foundational step as a data scientist in education!
---

# Project Specification

## Overview
- **Tech Domain:** Data Science
- **Tech Subdomain:** NumPy
- **Application Domain:** education
- **Application Subdomain:** numpy_arrays_and_operations
- **Target Audience:** beginners in data science and Python programming
- **Difficulty Level:** beginner
- **Time Constraints:** 2 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- Hands-on lab environment (Jupyter Notebook)
- Step-by-step instructions for each topic
- Self-contained examples for array manipulations
- Exercises and practice problems
- Automatic answer checking for selected exercises
- Documentation and explanations inline


## Global Learning Outcomes
- Ability to create and manipulate NumPy arrays
- Understanding of broadcasting and advanced indexing
- Confidence in using NumPy for basic data analysis


## Acceptance Criteria
- Lab covers all key NumPy topics: array creation, operations, reshaping, broadcasting
- Hands-on exercises are present and solutions are available
- All code cells in the notebook run without errors
- Instructions are clear, comprehensive, and beginner-friendly
- Learning outcomes are supported by the notebook structure


## Deliverables
- A Jupyter Notebook containing instructional content, code examples, and exercises
- Solution cells (hidden or separate) for all exercises
- README with setup instructions for the lab


---

# Projects

  
  ## 1. Data Science (NumPy)

  ### Tech Stack
  - **Language:** Python (3.10+)
  - **Framework:** Jupyter Notebook ()

  ### Testing
  
  - **Unit Testing:** pytest (Coverage: No)
  
  
  
  - **Integration Testing:** Not Specified
  
  
  
  - **End-to-End/API Testing:** Not Specified
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Basic Python programming
  
  - Familiarity with running notebooks
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Understand the purpose and benefits of using NumPy arrays
  
  - Create, manipulate, and operate on NumPy arrays
  
  - Perform basic mathematical and logical operations on arrays
  
  - Effectively index, slice, and reshape arrays for data analysis tasks
  
  - Apply broadcasting rules to optimize array operations
  

  ### Feature Set
  
  - Jupyter Notebook-based guided lab
  
  - In-notebook explanations and code samples
  
  - Exercises for independent practice
  
  - Sectional checkpoints or quizzes
  
  - Solutions and hints provided for key exercises
  

  ### API Documentation
  
  - **API Documentation:** Not Specified
  

  ### Output Resource Type
  - code

  
