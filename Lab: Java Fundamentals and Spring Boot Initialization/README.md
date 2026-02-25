## What you will do:

**Problem Statement**  
Scenario-Based Problem Statement: Spring Boot Backend for a Student Progress Tracker

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

## What you will learn:

- Ability to create and organize a Java project

- Understanding of OOP concepts in Java

- Proficiency in initializing and configuring a Spring Boot application

- Building and running RESTful services

- Familiarity with project structure and dependency management


---

## What you need to know:

- Basic programming experience

- Installed Java JDK

- Familiarity with using command line


---

## Modules and Activities:


### 📦 Object-Oriented Programming: Modeling Students and Assignments


#### ✅ Design Student and Assignment Classes

**🎯 Goal:**  
Apply Java OOP fundamentals by creating classes to represent students and their assignments.

**🛠 Instructions:**  

- Review the requirements for the student progress tracking system.

- Create a class to represent a student, including fields for identifying information and a collection to store their assignments.

- Create a class to represent an assignment, including fields for assignment details such as name and score.

- Utilize constructors, encapsulation through private fields and public getters/setters, and demonstrate correct object composition.

- Ensure that you do not include any unnecessary complexity (such as interfaces or inheritance) at this stage.


**📤 Expected Output:**  
Student and Assignment classes that encapsulate all necessary student and assignment data, structured according to Java OOP best practices.

---



### 📦 Spring Boot Project Structure and Initialization


#### ✅ Organize Project Structure

**🎯 Goal:**  
Demonstrate understanding of conventional Spring Boot project organization.

**🛠 Instructions:**  

- Review the pre-existing project structure provided in the lab environment.

- Ensure that model or entity classes are placed within a designated model or entity package, and that the main Spring Boot application entry point is at the root or a properly named base package.

- Identify and list the location of controller and model/entity classes to confirm correct organization.


**📤 Expected Output:**  
A clearly organized project structure with separated packages for models/entities and controllers, following Spring Boot conventions.

---

#### ✅ Examine Application Entrypoint and Dependencies

**🎯 Goal:**  
Understand the purpose of the application entrypoint and included dependencies for running a REST API.

**🛠 Instructions:**  

- Locate the main application class that contains the primary method launching the Spring Boot application.

- Review the dependency configuration (such as pom.xml or build.gradle) and identify the dependency that enables REST controller functionality.

- Briefly describe the purpose of the application entrypoint and the 'spring-boot-starter-web' dependency.


**📤 Expected Output:**  
Identification of the entrypoint class and correct dependency for REST endpoints, with a short description of their roles.

---



### 📦 Spring Boot REST Controller: Implementing API Endpoints


#### ✅ Implement Student Creation Endpoint

**🎯 Goal:**  
Create a REST POST endpoint that adds a new student and their first assignment.

**🛠 Instructions:**  

- Identify or create a REST controller in the proper package.

- Implement a POST endpoint to handle requests for creating a new student, including their first assignment.

- Ensure the endpoint receives required data as input and stores it in an in-memory data structure.

- Use appropriate HTTP status codes for the response to indicate success.


**📤 Expected Output:**  
A functioning POST /students endpoint which adds a new student and their first assignment using in-memory storage, returning a successful response.

---

#### ✅ Add or Update Assignment Endpoint

**🎯 Goal:**  
Implement a REST PUT endpoint for adding or updating assignments for existing students.

**🛠 Instructions:**  

- Within the same REST controller, implement a PUT endpoint that takes a student's identifier and assignment details.

- Ensure the endpoint can either add a new assignment or update an existing one for the identified student in in-memory storage.

- Respond with an appropriate HTTP status code to signify success or failure.


**📤 Expected Output:**  
A working PUT /students/{id}/assignments endpoint that allows adding or updating student assignments, with correct status code responses.

---

#### ✅ Retrieve Student Performance Summary

**🎯 Goal:**  
Develop a REST GET endpoint that returns a summary of a student's performance.

**🛠 Instructions:**  

- Add a new GET endpoint in the controller that accepts a student's identifier.

- Implement logic to collect the student's name, count of assignments, and average score.

- Return this summary in a structured format using an appropriate HTTP status code.


**📤 Expected Output:**  
A GET /students/{id}/summary endpoint that returns the student's name, assignment count, and average score as a summary object.

---



### 📦 Testing REST API Functionality


#### ✅ Author Unit Tests for Business Logic

**🎯 Goal:**  
Validate correct calculation of business logic such as average score using unit tests.

**🛠 Instructions:**  

- Write unit tests to verify that the calculation of average assignment score works correctly for various student assignment lists.

- Use the provided testing tools and ensure each test has a clear input and expected output.

- Focus tests on methods or logic within the Student and Assignment classes.


**📤 Expected Output:**  
At least two unit tests that confirm business logic, such as score calculation, produces accurate results.

---

#### ✅ Validate REST Endpoints with Simple API Tests

**🎯 Goal:**  
Verify REST endpoint behavior through integration or API-level tests.

**🛠 Instructions:**  

- Write at least one test that sends a request to one of the REST endpoints and checks the correctness of the response.

- Use the available testing framework (such as JUnit or MockMvc) and focus on covering the main success scenario for each endpoint.

- Ensure tests run without requiring additional configuration or external setup.


**📤 Expected Output:**  
Simple API-level test(s) confirming that at least one endpoint responds correctly to valid requests.

---



### 📦 Manual Application Run and API Verification


#### ✅ Run the Application and Manually Test Endpoints

**🎯 Goal:**  
Start the Spring Boot application and demonstrate ability to manually verify REST API functionality.

**🛠 Instructions:**  

- Start the Spring Boot backend using the command line or IDE, relying only on the pre-configured environment.

- Use a tool such as curl or Postman to send HTTP requests to each implemented endpoint (POST, PUT, GET).

- Record and review the API responses to confirm correct behavior and data structure.


**📤 Expected Output:**  
Successful manual launch and testing of application endpoints, with visible correct responses for all operations.

---


