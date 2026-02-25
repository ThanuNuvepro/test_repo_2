package com.controllers;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

@WebMvcTest(WelcomeController.class)
public class WelcomeControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void testWelcomeEndpointReturnsCorrectMessage() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/api/welcome"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.content().string("Welcome to EduLift's Digital Learning Platform!"));
    }
}
