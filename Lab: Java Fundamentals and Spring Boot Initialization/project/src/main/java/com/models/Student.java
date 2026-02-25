package com.models;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.ArrayList;
import java.util.List;

@Schema(name = "Student", description = "Represents a student enrolled in the system.")
public class Student {
    @Schema(description = "Unique identifier for the student.", example = "1")
    private Long id;

    @Schema(description = "Full name of the student.", example = "Alice Johnson")
    private String name;

    @Schema(description = "Email address of the student.", example = "alice.johnson@example.com")
    private String email;

    @Schema(description = "List of assignments completed by the student.")
    private List<Assignment> assignments;

    public Student() {
        this.assignments = new ArrayList<>();
    }

    public Student(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.assignments = new ArrayList<>();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public List<Assignment> getAssignments() {
        return assignments;
    }

    public void setAssignments(List<Assignment> assignments) {
        this.assignments = assignments;
    }

    public void addAssignment(Assignment assignment) {
        this.assignments.add(assignment);
    }
}
