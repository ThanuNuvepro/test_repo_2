package com.controllers;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;

@RestController
@RequestMapping("/api/welcome")
@Tag(name = "Welcome", description = "Welcome Endpoint APIs")
public class WelcomeController {
    @GetMapping
    @Operation(
        summary = "Get Welcome Message",
        description = "Returns a welcome message specific to EduLift's Digital Learning Platform.",
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Successful operation",
                content = @Content(mediaType = "text/plain", schema = @Schema(type = "string"))
            )
        }
    )
    public String welcome() {
        return "Welcome to EduLift's Digital Learning Platform!";
    }
}
