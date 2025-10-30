package org.imsglobal.oneroster.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Category entity representing a grade category
 * 
 * Based on IMS Global OneRoster v1.2 Gradebook Service specification
 */
@Entity
@Table(name = "categories")
@Getter
@Setter
public class Category extends BaseEntity {

    /**
     * Title of the category
     */
    @Column(nullable = false, length = 255)
    private String title;

    /**
     * Weight of this category in overall grade calculation (0.0 to 1.0)
     */
    @DecimalMin(value = "0.0", message = "Weight must be at least 0.0")
    @DecimalMax(value = "1.0", message = "Weight must be at most 1.0")
    @Column(precision = 5, scale = 4)
    private BigDecimal weight;

    /**
     * Line items associated with this category
     */
    @OneToMany(mappedBy = "category", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<LineItem> lineItems = new ArrayList<>();

    /**
     * Helper method to add a line item to this category
     */
    public void addLineItem(LineItem lineItem) {
        lineItems.add(lineItem);
        lineItem.setCategory(this);
    }

    /**
     * Helper method to remove a line item from this category
     */
    public void removeLineItem(LineItem lineItem) {
        lineItems.remove(lineItem);
        lineItem.setCategory(null);
    }
}
