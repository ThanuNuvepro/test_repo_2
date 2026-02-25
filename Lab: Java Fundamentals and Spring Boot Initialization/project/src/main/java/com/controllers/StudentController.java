package com.controllers;

import com.models.Student;
import com.models.Assignment;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.GetMapping;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.List;

@RestController
@RequestMapping("/students")
@Tag(name = "Students", description = "Endpoints for managing students and their assignments.")
public class StudentController {
    private static final AtomicLong studentIdGenerator = new AtomicLong(1);
    private static final Map<Long, Student> studentInMemoryStore = new ConcurrentHashMap<>();

    public static class CreateStudentRequest {
        @Schema(description = "Full name of the student.", example = "Alice Johnson")
        private String name;
        @Schema(description = "Email address of the student.", example = "alice.johnson@example.com")
        private String email;
        @Schema(description = "Name of the first assignment.", example = "Math Homework 1")
        private String assignmentName;
        @Schema(description = "Score for the first assignment.", example = "98.5")
        private double assignmentScore;
        public CreateStudentRequest() {}
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getAssignmentName() { return assignmentName; }
        public void setAssignmentName(String assignmentName) { this.assignmentName = assignmentName; }
        public double getAssignmentScore() { return assignmentScore; }
        public void setAssignmentScore(double assignmentScore) { this.assignmentScore = assignmentScore; }
    }

    public static class AssignmentRequest {
        @Schema(description = "Name of the assignment.", example = "History Essay 2")
        private String name;
        @Schema(description = "Score achieved for the assignment.", example = "89.0")
        private double score;
        public AssignmentRequest() {}
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getScore() { return score; }
        public void setScore(double score) { this.score = score; }
    }

    @PostMapping
    @Operation(
        summary = "Create a new student with their first assignment",
        description = "Adds a new student and their first assignment to the in-memory store.",
        requestBody = @io.swagger.v3.oas.annotations.parameters.RequestBody(
            required = true,
            description = "Student and first assignment creation request body.",
            content = @Content(
                schema = @Schema(implementation = CreateStudentRequest.class)
            )
        ),
        responses = {
            @ApiResponse(
                responseCode = "201",
                description = "Student created successfully",
                content = @Content(schema = @Schema(implementation = Student.class))
            ),
            @ApiResponse(
                responseCode = "400",
                description = "Invalid input data provided",
                content = @Content
            )
        }
    )
    public ResponseEntity<Student> createStudent(
        @RequestBody CreateStudentRequest request
    ) {
        if (request.getName() == null || request.getName().trim().isEmpty() ||
            request.getEmail() == null || request.getEmail().trim().isEmpty() ||
            request.getAssignmentName() == null || request.getAssignmentName().trim().isEmpty()) {
            return new ResponseEntity<>(null, HttpStatus.BAD_REQUEST);
        }
        Long assignedId = studentIdGenerator.getAndIncrement();
        Student student = new Student(assignedId, request.getName(), request.getEmail());
        Assignment assignment = new Assignment(request.getAssignmentName(), request.getAssignmentScore());
        student.addAssignment(assignment);
        studentInMemoryStore.put(assignedId, student);
        return new ResponseEntity<>(student, HttpStatus.CREATED);
    }

    @PutMapping("/{id}/assignments")
    @Operation(
        summary = "Add or update an assignment for a student",
        description = "Adds a new assignment or updates an existing assignment (by name) for the student with the given id in the in-memory store.",
        parameters = {
            @Parameter(
                name = "id",
                description = "Unique identifier of the student.",
                required = true,
                example = "1"
            )
        },
        requestBody = @io.swagger.v3.oas.annotations.parameters.RequestBody(
            required = true,
            description = "Assignment details to add or update for the student.",
            content = @Content(
                schema = @Schema(implementation = AssignmentRequest.class)
            )
        ),
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Assignment added or updated successfully.",
                content = @Content(schema = @Schema(implementation = Student.class))
            ),
            @ApiResponse(
                responseCode = "404",
                description = "Student not found.",
                content = @Content
            ),
            @ApiResponse(
                responseCode = "400",
                description = "Invalid input data.",
                content = @Content
            )
        }
    )
    public ResponseEntity<Student> addOrUpdateAssignment(
        @PathVariable("id") Long id,
        @RequestBody AssignmentRequest assignmentRequest
    ) {
        if (assignmentRequest.getName() == null || assignmentRequest.getName().trim().isEmpty()) {
            return new ResponseEntity<>(null, HttpStatus.BAD_REQUEST);
        }
        Student student = studentInMemoryStore.get(id);
        if (student == null) {
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);
        }
        List<Assignment> assignments = student.getAssignments();
        boolean updated = false;
        for (Assignment assignment : assignments) {
            if (assignment.getName().equalsIgnoreCase(assignmentRequest.getName())) {
                assignment.setScore(assignmentRequest.getScore());
                updated = true;
                break;
            }
        }
        if (!updated) {
            Assignment newAssignment = new Assignment(assignmentRequest.getName(), assignmentRequest.getScore());
            assignments.add(newAssignment);
        }
        student.setAssignments(assignments);
        return new ResponseEntity<>(student, HttpStatus.OK);
    }

    public static class StudentSummary {
        @Schema(description = "Name of the student.", example = "Alice Johnson")
        private String name;
        @Schema(description = "Number of assignments completed by the student.", example = "2")
        private int assignmentCount;
        @Schema(description = "Average score across all assignments.", example = "91.5")
        private double averageScore;
        public StudentSummary() {}
        public StudentSummary(String name, int assignmentCount, double averageScore) {
            this.name = name;
            this.assignmentCount = assignmentCount;
            this.averageScore = averageScore;
        }
        public String getName() {
            return name;
        }
        public void setName(String name) {
            this.name = name;
        }
        public int getAssignmentCount() {
            return assignmentCount;
        }
        public void setAssignmentCount(int assignmentCount) {
            this.assignmentCount = assignmentCount;
        }
        public double getAverageScore() {
            return averageScore;
        }
        public void setAverageScore(double averageScore) {
            this.averageScore = averageScore;
        }
    }

    @GetMapping("/{id}/summary")
    @Operation(
        summary = "Retrieve a student's performance summary",
        description = "Fetch the student's name, total assignments count, and average score.",
        parameters = {
            @Parameter(
                name = "id",
                description = "Unique identifier of the student.",
                required = true,
                example = "1"
            )
        },
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Student summary found and returned.",
                content = @Content(schema = @Schema(implementation = StudentSummary.class))
            ),
            @ApiResponse(
                responseCode = "404",
                description = "Student not found.",
                content = @Content
            )
        }
    )
    public ResponseEntity<StudentSummary> getStudentSummary(
            @PathVariable("id") Long id
    ) {
        Student student = studentInMemoryStore.get(id);
        if (student == null) {
            return new ResponseEntity<>(null, HttpStatus.NOT_FOUND);
        }
        int count = 0;
        double sum = 0;
        List<Assignment> assignments = student.getAssignments();
        if (assignments != null && !assignments.isEmpty()) {
            count = assignments.size();
            for (Assignment a : assignments) {
                sum += a.getScore();
            }
        }
        double average = count > 0 ? sum / count : 0.0;
        StudentSummary summary = new StudentSummary(student.getName(), count, average);
        return new ResponseEntity<>(summary, HttpStatus.OK);
    }
}
