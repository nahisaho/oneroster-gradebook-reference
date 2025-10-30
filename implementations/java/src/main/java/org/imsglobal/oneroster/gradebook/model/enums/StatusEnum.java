package org.imsglobal.oneroster.gradebook.model.enums;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Status enumeration for entities
 * 
 * Based on IMS Global OneRoster v1.2 specification
 */
public enum StatusEnum {
    /**
     * Entity is active
     */
    ACTIVE("active"),
    
    /**
     * Entity is marked for deletion
     */
    TOBEDELETED("tobedeleted");

    private final String value;

    StatusEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    public static StatusEnum fromValue(String value) {
        for (StatusEnum status : StatusEnum.values()) {
            if (status.value.equals(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Invalid Status value: " + value);
    }
}
