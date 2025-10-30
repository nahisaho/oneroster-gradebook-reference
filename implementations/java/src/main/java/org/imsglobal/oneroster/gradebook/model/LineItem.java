package org.imsglobal.oneroster.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMin;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * LineItem entity representing an assignment or assessment
 * 
 * Based on IMS Global OneRoster v1.2 Gradebook Service specification
 */
@Entity
@Table(name = "line_items")
@Getter
@Setter
public class LineItem extends BaseEntity {

    /**
     * Title of the line item
     */
    @Column(nullable = false, length = 255)
    private String title;

    /**
     * Description of the line item
     */
    @Column(columnDefinition = "TEXT")
    private String description;

    /**
     * Date the line item is assigned
     */
    @Column(name = "assign_date")
    private LocalDate assignDate;

    /**
     * Due date for the line item
     */
    @Column(name = "due_date")
    private LocalDate dueDate;

    /**
     * Maximum score possible for this line item
     */
    @DecimalMin(value = "0.0", message = "Score maximum must be at least 0.0")
    @Column(name = "score_maximum", precision = 10, scale = 2)
    private BigDecimal scoreMaximum;

    /**
     * Category this line item belongs to
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    /**
     * Results associated with this line item
     */
    @OneToMany(mappedBy = "lineItem", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Result> results = new ArrayList<>();

    /**
     * Helper method to add a result to this line item
     */
    public void addResult(Result result) {
        results.add(result);
        result.setLineItem(this);
    }

    /**
     * Helper method to remove a result from this line item
     */
    public void removeResult(Result result) {
        results.remove(result);
        result.setLineItem(null);
    }
}
