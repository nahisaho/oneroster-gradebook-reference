package org.imsglobal.oneroster.gradebook;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

/**
 * OneRoster Gradebook Service - Spring Boot Application
 * 
 * Reference implementation of IMS Global OneRoster v1.2 Gradebook Service
 * 
 * Provides REST API endpoints for:
 * - Categories (gradebook categories)
 * - Line Items (assignments/assessments)
 * - Results (student scores)
 * 
 * Features:
 * - OAuth 2.0 JWT authentication
 * - Scope-based authorization
 * - Pagination and filtering
 * - PostgreSQL database
 */
@SpringBootApplication
@EnableJpaAuditing
public class OneRosterGradebookApplication {

    public static void main(String[] args) {
        SpringApplication.run(OneRosterGradebookApplication.class, args);
    }
}
