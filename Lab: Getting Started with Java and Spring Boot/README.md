## What you will do:

**Problem Statement**  
Project Problem Statement (Scenario Style)

Title: Building the Foundation for a Digital Learning Platform with Spring Boot

Scenario

You are a Junior Backend Developer at EduLift, a fast-growing startup building online learning resources for schools. Recently, your team decided to modernize the platform's backend using Java Spring Boot, as it's known for its scalability and suitability for RESTful APIs. As part of your onboarding and to contribute immediately, you are tasked with laying down the foundational backend service of EduLift's new platform. This project is critical: it will serve as the technical baseline for all future educational modules and services.

Problem Context

EduLift’s ambition is to create modular, microservice-based backend systems for features such as student tracking, virtual classrooms, and interactive activities. However, before these advanced systems can be developed, the engineering team needs a standardized Spring Boot codebase. Your initial responsibility is to kickstart this transition by creating a minimal yet production-ready Spring Boot application that demonstrates best practices in project setup, API development, configuration management, and testing. This "Hello World" service will be a reference point for the entire engineering organization.

Objective

Your objective is to design, implement, and test a Spring Boot backend service that exposes a REST API endpoint returning a welcome message for users who wish to explore EduLift’s digital learning features. This service must be initialized properly, include clear project structure, support basic unit testing, and be fully documented on how to build and run it. Your deliverables will be reviewed by your lead engineer as the company’s reference template for all future backend modules.

Project Requirements & Tasks

1. Spring Boot Project Initialization  
   - Initialize a new Java Spring Boot project using either Spring Initializr or your IDE’s built-in tool.  
   - Set the group ID to `com.edulift`, the artifact ID to `edulift-welcome`, and ensure the Java version is compatible (Java 17+).  
   - Include minimal necessary dependencies (primarily 'spring-boot-starter-web' for REST capabilities and testing starter).  
   - Create a clean project structure following Maven (or Gradle) conventions.

2. REST Controller Creation  
   - Within the main package, create a REST controller class named `WelcomeController`.  
   - Implement a GET endpoint at `/api/welcome` responding with the string:  
     `Welcome to EduLift's Digital Learning Platform!`  
   - Ensure that the endpoint uses appropriate Spring annotations (@RestController, @GetMapping).

3. Serving a Simple Hello World Endpoint  
   - The endpoint `/api/welcome` must return the exact welcome message in the body as plain text or JSON (bonus for both, if appropriate).  
   - Document the endpoint URL and expected response in a simple markdown or text file in the project root (`README.md`).

4. Project Build and Run Configurations  
   - Ensure the project builds successfully using Maven (or Gradle) with `mvn clean package` (or equivalent).  
   - Document the exact commands used to build and run the application via the terminal (include running as an executable JAR, e.g., `java -jar`).  
   - Include sample output of a successful GET request to `/api/welcome` (use curl or Postman) in the documentation.

5. Basic Unit Testing Setup  
   - Add a basic unit test for the REST controller using JUnit and Spring Boot’s testing support.  
   - The test should perform an HTTP GET request to `/api/welcome` and assert that the response is `200 OK` and the body matches the welcome message.  
   - Ensure that all tests pass using the build tool (e.g., `mvn test`).

Learning Outcomes

By completing this project, you will:
- Demonstrate the ability to set up, structure, and configure a Spring Boot project following industry best practices.
- Understand and implement RESTful API endpoints using Java and Spring Boot.
- Gain familiarity with the project build process, command-line execution, and navigating the project lifecycle.
- Apply fundamental testing techniques to Java backend applications using Spring Boot’s test suite.
- Deliver clear and concise API documentation and developer instructions, setting a template for peer contributors.

Target Audience Alignment

This project is specifically designed for Beginner Java Developers who have foundational Java coding knowledge but are new to Spring Boot and modern backend development. All technical tasks assume familiarity with Java syntax, basic IDE use, and command-line operations, but do not require prior experience with backend frameworks.

Time Constraints

- Total estimated time: 2-4 hours
    - Project setup and initialization: 30 min
    - Controller implementation: 20 min
    - Build and run configuration: 20 min
    - Unit testing: 30 min
    - Documentation and polish: 20-30 min
    - Buffer for troubleshooting: 20-40 min

Summary Checklist

- [ ] Spring Boot project (`edulift-welcome`) initialized correctly
- [ ] REST controller `WelcomeController` exposes `/api/welcome` endpoint
- [ ] Endpoint returns required welcome message
- [ ] Project builds/runs via standard Maven/Gradle commands as documented
- [ ] Basic unit test(s) in place and passing for the welcome endpoint
- [ ] Clear README with build/run/test instructions and example output

Best Practices Reminder

Stay within the provided feature set—avoid implementing advanced features (e.g., database integration, authentication, or additional endpoints). Focus solely on initial project scaffolding, RESTful design, build/test lifecycle, and fundamental API delivery—all essential skills for backend Java development in the educational sector.

Deliverables

- Complete Java Spring Boot project directory (as a zipped file or repository).
- `README.md` containing project overview, build/run instructions, endpoint documentation, and example outputs.
- Passing unit test(s) validating the `/api/welcome` endpoint response.

This foundational project will directly contribute to EduLift’s ongoing innovation in digital education, ensuring that future backend modules for personalized learning, progress tracking, and engagement analytics all start from a robust, tested, and well-documented codebase.

---

## What you will learn:

- Understand the basics of Java and Spring Boot application development

- Initialize and configure a Spring Boot project

- Develop and expose a RESTful endpoint in Spring Boot

- Build and run a Java application using Maven

- Write and execute basic unit and integration tests


---

## What you need to know:

- Java JDK installed

- Maven installed

- IDE installed (IntelliJ IDEA or Eclipse)


---

## Modules and Activities:


### 📦 Spring Boot Project Initialization and Structure


#### ✅ Understand Project Structure in a Maven-based Spring Boot Application

**🎯 Goal:**  
Familiarize yourself with the standard Maven directory layout and identify core files within the Spring Boot project.

**🛠 Instructions:**  

- Open the provided Spring Boot project in your chosen IDE.

- Explore the folder structure under the main project directory.

- Identify core directories and files such as 'src/main/java', 'src/main/resources', and 'pom.xml'.

- Note the location and purpose of the main application class, resources, and application configuration file.


**📤 Expected Output:**  
You should be able to identify the Maven project structure and explain the purpose of key project folders and files.

---

#### ✅ Review and Interpret application.properties Configuration

**🎯 Goal:**  
Understand the role of the application properties file in Spring Boot configuration.

**🛠 Instructions:**  

- Locate the application.properties file in the project's resources directory.

- Open the file and review any existing configuration settings.

- Consider what aspects of application behavior can be controlled through this file.


**📤 Expected Output:**  
You should understand what application.properties is for and be able to list configuration items typically placed in this file.

---



### 📦 REST Endpoint Development


#### ✅ Explore and Analyze the Welcome REST Controller

**🎯 Goal:**  
Assess how a REST controller is defined and structured in Spring Boot to serve HTTP requests.

**🛠 Instructions:**  

- Locate the WelcomeController class within the main Java package.

- Examine the annotations at the class and method level that designate it as a REST controller.

- Identify the HTTP method and endpoint path mapped in the controller.


**📤 Expected Output:**  
You should be able to explain how a class is turned into a REST controller and how endpoints are mapped in Spring Boot.

---

#### ✅ Test the Welcome Endpoint in a Running Application

**🎯 Goal:**  
Interact with the live REST endpoint and verify its behavior as specified.

**🛠 Instructions:**  

- Start the Spring Boot application using your IDE’s run function or the designated run command.

- Confirm the application starts without errors by checking the IDE's console for a 'Started' message.

- Using a REST client or browser, access the '/api/welcome' endpoint.

- Read and validate the response message.


**📤 Expected Output:**  
The endpoint should respond with the exact welcome message: 'Welcome to EduLift's Digital Learning Platform!'. The application should remain running and responsive.

---



### 📦 Building, Running, and Observing the Application


#### ✅ Build the Spring Boot Application with Maven

**🎯 Goal:**  
Practice building the Spring Boot application using Maven to produce an executable artifact.

**🛠 Instructions:**  

- In your terminal, navigate to the project's root directory.

- Run the Maven clean and package commands.

- Observe the output and verify there are no compilation errors.


**📤 Expected Output:**  
Maven completes successfully and produces a JAR file in the 'target' directory.

---

#### ✅ Run the Application via Terminal and Monitor Logs

**🎯 Goal:**  
Start the built application from the command line and observe runtime logs.

**🛠 Instructions:**  

- In the terminal, use the appropriate command to run the JAR file.

- Watch the application console output for startup logs and successful boot messages.

- Note any logging information related to the application startup and endpoint availability.


**📤 Expected Output:**  
The application starts as a standalone process and logs indicate that it is running and listening for requests.

---



### 📦 Fundamentals of API Testing with JUnit


#### ✅ Examine and Interpret a Basic JUnit API Test

**🎯 Goal:**  
Understand how a JUnit test is constructed to validate a Spring Boot REST endpoint.

**🛠 Instructions:**  

- Locate the test class for WelcomeController within the test source directory.

- Review the structure of a typical JUnit test method and the annotations used.

- Observe how the HTTP GET request and expected response assertion are implemented.


**📤 Expected Output:**  
You should be able to describe the purpose of the test annotations and how endpoint responses are validated in a Spring Boot test.

---

#### ✅ Run Unit Tests and Validate Results

**🎯 Goal:**  
Execute the provided unit test suite to ensure the welcome endpoint works as intended.

**🛠 Instructions:**  

- From your IDE or terminal, run the Maven test phase for the project.

- Observe the test output and ensure all tests pass without errors.

- Review the output to confirm the correct endpoint behavior is being asserted.


**📤 Expected Output:**  
All relevant unit tests should pass. The welcome endpoint’s behavior is confirmed as correct via automated testing.

---


