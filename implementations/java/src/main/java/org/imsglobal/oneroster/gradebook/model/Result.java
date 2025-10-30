package org.imsglobal.oneroster.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import lombok.Getter;
import lombok.Setter;
import org.imsglobal.oneroster.gradebook.model.enums.ScoreStatusEnum;

import java.math.BigDecimal;

/**
 * Result entity representing a student's score on a line item
 * 
 * Based on IMS Global OneRoster v1.2 Gradebook Service specification
 */
@Entity
@Table(name = "results")
@Getter
@Setter
public class Result extends BaseEntity {

    /**
     * Student identifier (OneRoster User sourcedId)
     */
    @Column(name = "student_id", nullable = false, length = 255)
    private String studentId;

    /**
     * Earned score for this result
     */
    @DecimalMin(value = "0.0", message = "Score must be at least 0.0")
    @Column(precision = 10, scale = 2)
    private BigDecimal score;

    /**
     * Score as a percentage (0.0 to 1.0)
     */
    @DecimalMin(value = "0.0", message = "Score percent must be at least 0.0")
    @DecimalMax(value = "1.0", message = "Score percent must be at most 1.0")
    @Column(name = "score_percent", precision = 5, scale = 4)
    private BigDecimal scorePercent;

    /**
     * Status of the score (earnedFull, earnedPartial, notEarned, notSubmitted)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "score_status", length = 20)
    private ScoreStatusEnum scoreStatus;

    /**
     * Comment or feedback for this result
     */
    @Column(columnDefinition = "TEXT")
    private String comment;

    /**
     * Line item this result is associated with
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "line_item_id", nullable = false)
    private LineItem lineItem;
}
