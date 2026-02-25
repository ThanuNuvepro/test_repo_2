package com.api;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.http.MediaType;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@SpringBootTest
@AutoConfigureMockMvc
public class StudentApiIntegrationTests {
    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testCreateStudentEndpointReturnsCreatedStudent() throws Exception {
        String requestBody = "{" +
            ""name": "Jane Doe"," +
            ""email": "jane.doe@example.com"," +
            ""assignmentName": "Math Test"," +
            ""assignmentScore": 91.0" +
        "}";
        mockMvc.perform(post("/students")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Jane Doe"))
                .andExpect(jsonPath("$.email").value("jane.doe@example.com"))
                .andExpect(jsonPath("$.assignments[0].name").value("Math Test"))
                .andExpect(jsonPath("$.assignments[0].score").value(91.0));
    }

    @Test
    public void testGetStudentSummaryEndpoint() throws Exception {
        String requestBody = "{" +
            ""name": "Adam Smith"," +
            ""email": "adam.smith@example.com"," +
            ""assignmentName": "Science Project"," +
            ""assignmentScore": 88.5" +
        "}";
        MvcResult result = mockMvc.perform(post("/students")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isCreated())
                .andReturn();
        String content = result.getResponse().getContentAsString();
        String idValue = content.replaceAll(".*\"id\":(\d+).*", "$1");
        mockMvc.perform(get("/students/" + idValue + "/summary").contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Adam Smith"))
                .andExpect(jsonPath("$.assignmentCount").value(1))
                .andExpect(jsonPath("$.averageScore").value(88.5));
    }
}
