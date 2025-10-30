package org.imsglobal.oneroster.gradebook.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * DTO for LineItem entity
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class LineItemDto {

    @JsonProperty("sourcedId")
    private String sourcedId;

    @NotBlank(message = "Title is required")
    @JsonProperty("title")
    private String title;

    @JsonProperty("description")
    private String description;

    @JsonProperty("assignDate")
    private LocalDate assignDate;

    @JsonProperty("dueDate")
    private LocalDate dueDate;

    @DecimalMin(value = "0.0", message = "Score maximum must be at least 0.0")
    @JsonProperty("scoreMaximum")
    private BigDecimal scoreMaximum;

    @JsonProperty("categorySourcedId")
    private String categorySourcedId;

    @JsonProperty("status")
    private StatusEnum status;

    @JsonProperty("dateLastModified")
    private LocalDateTime dateLastModified;

    @JsonProperty("metadata")
    private String metadata;
}
