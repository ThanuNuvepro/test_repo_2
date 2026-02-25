package com.models;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(name = "Assignment", description = "Represents an assignment completed by a student.")
public class Assignment {
    @Schema(description = "The name of the assignment.", example = "Math Homework 1")
    private String name;

    @Schema(description = "The score achieved on the assignment.", example = "95.0")
    private double score;

    public Assignment() {
    }

    public Assignment(String name, double score) {
        this.name = name;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }
}
