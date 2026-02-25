# Project Plan

## Basic Information
- **ID:** 1e36ea3e-89eb-4280-86e1-ab3961a1e305
- **Name:** Lab: Java Fundamentals and Spring Boot Initialization
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: Java Fundamentals and Spring Boot Initialization
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-25T17:03:55.440766
- **Modified By:** rocky
- **Modified On:** 2026-02-25T17:05:08.664245
- **Published On:** N/A

## User prompt
- Generate lab for module: Java Fundamentals and Spring Boot Initialization
---

## Problem Statement
- Scenario-Based Problem Statement: Spring Boot Backend for a Student Progress Tracker

Scenario:  
You are a Junior Backend Developer newly hired by EduPro Solutions, an edtech startup specializing in digital tools for classroom engagement. The company has identified that teachers frequently struggle to track and quickly access basic student progress information for classroom quizzes and assignments. EduPro needs a simple backend solution to serve as the foundation for a future full-featured application that helps educators manage student performance data.

Project Objective:  
Your task is to design and implement a minimalistic Spring Boot REST API called Student Progress Tracker. This API will allow teachers to:
- Record basic information about students.
- Add/update quiz or assignment scores for each student.
- Retrieve a summary of student performance using a REST endpoint.

You must apply basic Java fundamentals (including OOP principles), initialize and organize a properly structured Spring Boot project, and provide clear setup instructions in a README. You will also practice writing simple unit and API tests to ensure your endpoints behave as expected.

Target Audience Alignment:  
This project is aimed at beginner to intermediate Java developers starting to learn backend development and Spring Boot. You should be comfortable with Java syntax, basic OOP concepts (classes, objects, constructors, encapsulation), and have very basic awareness of the Spring ecosystem (but not deep experience). All tasks are appropriate for learners at this level; no advanced frameworks, database integrations, or security are expected.

Timeframe:  
The project is designed to be completed in 2–3 hours.

Deliverables and Feature Set:  

1. Simple Java Classes Demonstrating OOP  
    - Design at least two Java classes: Student and Assignment.
    - The Student class must have basic fields such as id, name, and a collection of Assignment objects.
    - The Assignment class must include fields like assignmentName and score.
    - Use constructors, getters/setters, and encapsulation.

2. Spring Boot Project With Proper Structure  
    - Bootstrap a new Maven or Gradle Spring Boot project (using https://start.spring.io or your IDE).
    - Adhere to conventional Spring Boot project structuring:
        - Place models/entities in a model or entity package.
        - Controllers in a controller package.
        - Application entrypoint in a root package.
    - Include the minimum dependencies to run a REST API (i.e., spring-boot-starter-web).

3. REST Controller With a Basic Endpoint  
    - Create at least one REST controller class.
    - Implement a POST endpoint (/students) to add a new student and their first assignment.
    - Implement a PUT endpoint (/students/{id}/assignments) to add or update assignments for a student.
    - Implement a GET endpoint (/students/{id}/summary) that returns a summary object: student name, number of assignments, and average score.
    - All data can be managed in-memory (use an ArrayList/Map as a “database”).
    - Make sure responses use appropriate HTTP status codes.

4. README With Setup and Run Instructions  
    - Provide a clear, concise README file with:
        - Java version and prerequisites.
        - Step-by-step instructions to build, run, and test the application.
        - Example HTTP requests and sample JSON payloads for all endpoints.

5. Basic Unit and API Testing  
    - Write at least two unit tests for business logic (e.g., verifying the average score calculation).
    - Write at least one simple integration or API test for an endpoint, using either JUnit or Spring’s MockMvc.

Learning Outcomes and Project Relevance:  
Completion of this project will demonstrate your ability to:
- Apply fundamental Java and OOP principles by modeling students and their assignments.
- Bootstrap and configure a minimal Spring Boot project using industry-standard structure.
- Understand and build REST API endpoints to manipulate and retrieve student progress data.
- Write and run unit/API tests in a Java backend environment.
- Organize and communicate technical work clearly via a README.

Strict Boundaries:  
You are strictly limited to:
- Java OOP fundamentals (classes, objects, methods, encapsulation).
- Basic Spring Boot concepts (controllers, entry point, application structuring).
- REST endpoint implementation—no authentication, no frontend, no database integration.
- Basic use of in-memory data structures only.
- Simple tests with JUnit or Spring’s built-in testing tools.
- Clear, concise documentation.

Project Execution Steps and Timeline (2–3 hours):  
1. Scaffold the Spring Boot project and set up packages – 15 min  
2. Create Student and Assignment Java classes demonstrating OOP – 20 min  
3. Implement in-memory data storage and business logic – 20 min  
4. Implement the REST controller and all specified endpoints – 30 min  
5. Write unit and simple integration/API tests – 25 min  
6. Write the README with setup instructions – 20 min  
7. Final review, local testing, and submission – 10 min

Summary:  
By the end of this challenge, you will have created a simple, well-structured, and tested Spring Boot backend service that demonstrates your understanding of Java fundamentals, OOP, and the basics of RESTful API development in an educational context. This forms a practical foundation for further backend development learning and real-world applications in the edtech space.
---

# Project Specification

## Overview
- **Tech Domain:** Backend Development
- **Tech Subdomain:** Spring Boot
- **Application Domain:** education
- **Application Subdomain:** java_fundamentals_and_spring_boot_initialization
- **Target Audience:** beginner to intermediate Java developers
- **Difficulty Level:** Beginner
- **Time Constraints:** 2-3 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- Simple Java classes demonstrating OOP
- Spring Boot project with proper structure
- REST Controller with a basic endpoint
- README with setup and run instructions


## Global Learning Outcomes
- Mastery of foundational Java and OOP principles
- Ability to bootstrap and configure a Spring Boot project
- Understanding of REST API basics within Spring Boot
- Experience with unit and API testing in a Java environment


## Acceptance Criteria
- Project builds successfully using Maven
- All test cases pass (unit, integration, and API tests)
- Spring Boot application starts without errors
- Basic REST API responds with expected result
- Documentation is clear and describes setup, execution, and endpoints


## Deliverables
- Spring Boot Java project with source code
- Sample Java classes demonstrating OOP
- REST controller with at least one endpoint
- Test cases for logic and API
- README with setup and usage instructions


---

# Projects

  
  ## 1. Backend Development (Spring Boot)

  ### Tech Stack
  - **Language:** Java (17)
  - **Framework:** Spring Boot (3.x)

  ### Testing
  
  - **Unit Testing:** JUnit 5 (Coverage: No)
  
  
  
  - **Integration Testing:** Spring Boot Test (Coverage: No)
  
  
  
  - **End-to-End/API Testing:** RestAssured (Coverage: No)
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Basic programming experience
  
  - Installed Java JDK
  
  - Familiarity with using command line
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Ability to create and organize a Java project
  
  - Understanding of OOP concepts in Java
  
  - Proficiency in initializing and configuring a Spring Boot application
  
  - Building and running RESTful services
  
  - Familiarity with project structure and dependency management
  

  ### Feature Set
  
  - Java project setup and build configuration
  
  - OOP examples
  
  - Spring Boot initialization
  
  - First REST endpoint
  
  - Unit and integration tests
  
  - Run and test application locally
  

  ### API Documentation
  
  - **API Documentation:** Not Specified
  

  ### Output Resource Type
  - code

  
