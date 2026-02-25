package com.api;

// Fixed: Added missing semicolons at end of import lines and ensured all required imports are present.
import com.models.Student;
import com.models.Assignment;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Collections;

public class StudentLogicTests {
    // Test calculation of average score with multiple assignments
    @Test
    public void testAverageScoreMultipleAssignments() {
        Student student = new Student(1L, "Emily Stone", "emily.stone@example.com");
        student.addAssignment(new Assignment("Math Test", 90));
        student.addAssignment(new Assignment("Science Quiz", 80));
        student.addAssignment(new Assignment("History Essay", 100));
        double sum = 0;
        int count = student.getAssignments().size();
        for (Assignment a : student.getAssignments()) {
            sum += a.getScore();
        }
        double average = count > 0 ? sum / count : 0.0;
        // Check that the average is computed correctly
        Assertions.assertEquals(90.0, average, 0.00001);
    }

    // Test average score calculation for a student with no assignments
    @Test
    public void testAverageScoreNoAssignments() {
        Student student = new Student(2L, "John Doe", "john.doe@example.com");
        double sum = 0;
        int count = student.getAssignments().size();
        for (Assignment a : student.getAssignments()) {
            sum += a.getScore();
        }
        double average = count > 0 ? sum / count : 0.0;
        // Should return 0.0 for no assignments
        Assertions.assertEquals(0.0, average, 0.00001);
    }

    // Test average score calculation when there is only one assignment
    @Test
    public void testAverageScoreOneAssignment() {
        Student student = new Student(3L, "Sara Lee", "sara.lee@example.com");
        student.addAssignment(new Assignment("Literature Project", 77.5));
        double sum = 0;
        int count = student.getAssignments().size();
        for (Assignment a : student.getAssignments()) {
            sum += a.getScore();
        }
        double average = count > 0 ? sum / count : 0.0;
        // The average should match the only assignment score
        Assertions.assertEquals(77.5, average, 0.00001);
    }
}
