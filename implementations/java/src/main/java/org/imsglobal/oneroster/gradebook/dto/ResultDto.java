package org.imsglobal.oneroster.gradebook.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.imsglobal.oneroster.gradebook.model.enums.ScoreStatusEnum;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO for Result entity
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ResultDto {

    @JsonProperty("sourcedId")
    private String sourcedId;

    @NotBlank(message = "Student ID is required")
    @JsonProperty("studentId")
    private String studentId;

    @DecimalMin(value = "0.0", message = "Score must be at least 0.0")
    @JsonProperty("score")
    private BigDecimal score;

    @DecimalMin(value = "0.0", message = "Score percent must be at least 0.0")
    @DecimalMax(value = "1.0", message = "Score percent must be at most 1.0")
    @JsonProperty("scorePercent")
    private BigDecimal scorePercent;

    @JsonProperty("scoreStatus")
    private ScoreStatusEnum scoreStatus;

    @JsonProperty("comment")
    private String comment;

    @NotBlank(message = "Line item sourced ID is required")
    @JsonProperty("lineItemSourcedId")
    private String lineItemSourcedId;

    @JsonProperty("status")
    private StatusEnum status;

    @JsonProperty("dateLastModified")
    private LocalDateTime dateLastModified;

    @JsonProperty("metadata")
    private String metadata;
}
