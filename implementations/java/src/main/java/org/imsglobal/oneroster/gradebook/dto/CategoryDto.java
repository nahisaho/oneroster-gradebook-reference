package org.imsglobal.oneroster.gradebook.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO for Category entity
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CategoryDto {

    @JsonProperty("sourcedId")
    private String sourcedId;

    @NotBlank(message = "Title is required")
    @JsonProperty("title")
    private String title;

    @DecimalMin(value = "0.0", message = "Weight must be at least 0.0")
    @DecimalMax(value = "1.0", message = "Weight must be at most 1.0")
    @JsonProperty("weight")
    private BigDecimal weight;

    @JsonProperty("status")
    private StatusEnum status;

    @JsonProperty("dateLastModified")
    private LocalDateTime dateLastModified;

    @JsonProperty("metadata")
    private String metadata;
}
