# Project Plan

## Basic Information
- **ID:** f1550802-5fce-4acd-aa23-cf4185c42a42
- **Name:** Lab: Spring Boot: Building Your First REST API
- **Description:** Detailed specification for generating a Project using Generative AI
- **Schema:** 2.0
- **Version:** Lab: Spring Boot: Building Your First REST API
- **Owner:** Nuvepro
- **Locale:** en_US
- **Category:** 

## Users and Dates
- **Created By:** rocky
- **Created On:** 2026-02-25T18:14:29.807440
- **Modified By:** rocky
- **Modified On:** 2026-02-25T18:15:10.468018
- **Published On:** N/A

## User prompt
- Generate lab for module: Spring Boot: Building Your First REST API
---

## Problem Statement
- Problem Statement: Building a Simple Student Management RESTful API for an Education Platform (rest_api_lab)

Scenario: Real-World Role & Problem Context

You have recently joined an educational technology startup as a Junior Backend Developer. Your team is tasked with building the foundation of a new "Student Management" module for the platform, which will eventually support teachers in managing their students’ information efficiently. As part of a phased delivery approach, you are responsible for building the first version of the backend system that will serve as a RESTful API for managing student records.

Currently, the startup wants a proof of concept that enables basic operations (Create, Read, Update, Delete) on student entities—all managed in-memory to accelerate prototyping and feedback. While future versions will adopt robust persistence solutions, the goal for this first lab is speed, simplicity, and clarity. API clients, such as web or mobile developers on your team, should be able to interact with a well-defined API to perform CRUD operations on students.

Objective

Develop a basic Spring Boot RESTful API that supports full CRUD (Create, Read, Update, Delete) for a `Student` entity using in-memory data structures. Your application will consist of a single REST controller with endpoints that allow other components in the education platform to manage student records via JSON. You will also implement straightforward error handling for common cases, ensure proper request and response formats, and (optionally) provide basic API documentation using Swagger/OpenAPI specifications.

Project Constraints & Feature Set

- Spring Boot project setup only; no database integration—the backing data is held in application memory (e.g., using a `Map` or `List`).
- Implement a single REST controller class named `StudentController`.
- CRUD operations:
  - Create a new student (POST).
  - Read/get details of all students or a single student (GET).
  - Update an existing student’s data (PUT).
  - Delete a student (DELETE).
- Basic error handling: For example, return a suitable HTTP error/status code if a requested student is not found.
- Handle JSON input and output for all endpoints; all communication is strictly via JSON.
- (Bonus) Add basic auto-generated API documentation using Swagger/OpenAPI.
- Project must be executable within a standard Spring Boot environment (Spring Initializr, Maven/Gradle).

Assumptions About Learners

- You are a beginner Java developer, a student learning web development, or in early-stage software engineering.
- You are familiar with Java syntax, basic object-oriented design, and have fundamental knowledge of web concepts (like HTTP verbs and JSON payloads).
- You have never built a Spring Boot REST API before but want hands-on experience.

Learning Outcomes Mapping

By completing this project, you will:

- Gain hands-on experience with building and configuring a REST API using Spring Boot.
- Deepen your understanding of mapping CRUD operations to RESTful services in Java.
- Become familiar with the processes of parsing and serializing JSON requests and responses with Spring Boot.
- Practice fundamental error handling techniques in a RESTful context (e.g., handling "not found" scenarios).
- Learn to test and validate API endpoints using tools like Postman, curl, or browser-based REST clients.
- Start basic troubleshooting and debugging in the Spring Boot context by solving common beginner mistakes (like handling missing fields or malformed requests).
- (Bonus) Discover the value of API documentation with Swagger/OpenAPI.

Step-by-Step Project Execution (Technical Instructions)

1. **Spring Boot Project Setup (15 minutes)**
   - Use Spring Initializr (https://start.spring.io/) to generate a new project.
   - Select Java, your preferred build tool (Maven or Gradle), and add the following dependencies:
     - Spring Web
     - (Optional, for bonus) Springdoc OpenAPI or Swagger (for API documentation)
   - Import the project into your IDE (e.g., IntelliJ IDEA, Eclipse, or VS Code).

2. **Define the Student Entity (10 minutes)**
   - Create a `Student` Java class to represent student records with at least the following fields:
     - `Long id`
     - `String name`
     - `String email`
     - `String course`
   - Add standard constructors, getters, and setters.

3. **In-memory Persistence Layer (10 minutes)**
   - In the controller class, store student data in a suitable data structure, like `Map<Long, Student>`.
   - Initialize the in-memory store as a class field.

4. **StudentController Implementation (35 minutes)**
   - Annotate your controller class with `@RestController` and map it to `/students`.
   - Implement endpoints for:
     - **Create (POST `/students`)**
       - Accept a JSON payload and add a new `Student` to your collection.
       - Generate an auto-incrementing ID if none is provided.
     - **Read**
       - GET `/students`: Return all students as a JSON array.
       - GET `/students/{id}`: Return a specific student by ID or proper error if not found.
     - **Update (PUT `/students/{id}`)**
       - Replace an existing student record with the new details.
       - Return appropriate status if the student doesn’t exist.
     - **Delete (DELETE `/students/{id}`)**
       - Remove a student by ID; return an error if not found.
   - Ensure all inputs and outputs are in JSON and conventional HTTP status codes are sent.

5. **Basic Error Handling (15 minutes)**
   - Return `404 Not Found` if a student ID does not exist.
   - Return `400 Bad Request` for invalid/malformed requests.
   - Use `@ResponseStatus` or appropriate exception handlers as needed.

6. **Testing & Validation (15 minutes)**
   - Test all endpoints using Postman, curl, or a similar REST client.
   - Validate well-formed request/response bodies, status codes, and error scenarios.

7. **(Bonus) API Documentation (10 minutes)**
   - Integrate OpenAPI/Swagger and expose API documentation at `/swagger-ui.html` or `/api-docs`.
   - Annotate endpoints or configure the documentation generator as needed.

8. **Troubleshooting as You Execute**
   - Log and fix common errors (e.g., null pointers, incorrect mappings, JSON parsing issues).
   - Use IDE debugging tools or console output to trace and resolve issues.

Timeline & Milestones (Total: 2 hours)

- Project Setup & Student Entity: 25 minutes
- Controller & CRUD Endpoints: 35 minutes
- Error Handling & Persistence Layer: 25 minutes
- Testing/Validation: 15 minutes
- (Bonus) API Documentation: 10 minutes
- Buffer/Troubleshooting: 10 minutes

Final Deliverables

- Complete, runnable Spring Boot application with a `StudentController` that enables CRUD operations in-memory.
- Well-structured code following Java and Spring Boot conventions.
- A short README or embedded comments explaining how to run and test the project.
- (Optional bonus) API documentation accessible via Swagger/OpenAPI.

Relevance & Practical Application

Your work forms the starting point for all future student data management features in the platform, providing a hands-on, real-world backend development scenario tailored to the education sector. By building from scratch in a controlled scope, you not only gain practical Spring Boot skills but also directly impact how teachers and staff will interact with your platform in the future. All steps, deliverables, and checks are engineered to match the skills, tools, and time constraints of a beginner learner in Java and web development.

Stay strictly within the documented feature set and complete your lab project in the designated two-hour slot. Good luck, Junior Backend Developer!
---

# Project Specification

## Overview
- **Tech Domain:** Backend Development
- **Tech Subdomain:** Spring Boot
- **Application Domain:** Education
- **Application Subdomain:** rest_api_lab
- **Target Audience:** Beginner Java developers, students learning web development, and software engineering learners
- **Difficulty Level:** Beginner
- **Time Constraints:** 2 hours
- **Learning Style:** guided
- **Requires Research:** False

## Global Feature Set
- Spring Boot project setup
- Single REST controller implementation
- CRUD operations for a sample entity (e.g., `User` or `Book`)
- Use in-memory data structures for persistence (no database required for first lab)
- Basic error handling (e.g., resource not found)
- JSON response and request parsing
- API documentation basics using Swagger/OpenAPI (optional for bonus)


## Global Learning Outcomes
- Hands-on experience with building and configuring REST APIs using Spring Boot
- Understanding CRUD operations and their mapping in REST
- Familiarity with testing and validating RESTful services
- Basic troubleshooting and debugging within Spring Boot context


## Acceptance Criteria
- Spring Boot project builds successfully with Maven
- All REST endpoints return correct responses (status codes, JSON structure)
- All expected CRUD operations are functional
- Unit and integration tests pass successfully
- Clear project structure as per Spring Boot conventions
- Demonstrated basic error handling (404, validation errors)
- Able to test endpoints using tools like Postman


## Deliverables
- Complete Spring Boot project source code
- README with setup and running instructions
- Unit and integration test classes
- Sample Postman collection or cURL commands for API testing
- Sample JSON payloads for input/output
- Swagger/OpenAPI configuration file (optional, if implemented)


---

# Projects

  
  ## 1. Backend Development (Spring Boot)

  ### Tech Stack
  - **Language:** Java (17)
  - **Framework:** Spring Boot (3.x)

  ### Testing
  
  - **Unit Testing:** JUnit 5 (Coverage: No)
  
  
  
  - **Integration Testing:** Spring Boot Test (Coverage: No)
  
  
  
  - **End-to-End/API Testing:**  (Coverage: No)
  

  ### Scope
  
  
  

  ### Prerequisites
  
  - Java basics
  
  - Introduction to HTTP/REST principles
  

  ### Runtime Environment
  - **Build Tool:** 
  
  - **Host:** N/A
  - **Port:** N/A
  - **Credentials:**  / 
  - **IDE:** 
  - **OS Requirements:** 

  ### Learning Outcomes
  
  - Set up and configure a Spring Boot application
  
  - Implement and document simple REST APIs
  
  - Understand Spring Boot’s request mapping and dependency injection
  
  - Test REST APIs using Postman, cURL, and unit/integration testing frameworks
  
  - Handle JSON data with Java and Spring Boot
  
  - Understand Spring Boot’s project structure
  

  ### Feature Set
  
  - Create a Spring Boot project
  
  - Define an entity and REST controller
  
  - Expose endpoints for CRUD operations
  
  - Simple in-memory persistence
  
  - Basic error handling
  
  - Unit and integration testing of endpoints
  
  - API testing via external tools
  

  ### API Documentation
  
  - **Endpoint:** 
  - **Method:** 
  - **Request Body:** 
  - **Response:** 
  
  

  ### Output Resource Type
  - code

  
