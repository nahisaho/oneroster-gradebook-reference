package org.imsglobal.oneroster.gradebook.model.enums;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Score status enumeration for Result entities
 * 
 * Based on IMS Global OneRoster v1.2 specification
 */
public enum ScoreStatusEnum {
    /**
     * Score has been earned in full
     */
    EARNED_FULL("earnedFull"),
    
    /**
     * Score has been partially earned
     */
    EARNED_PARTIAL("earnedPartial"),
    
    /**
     * Score was not earned (e.g., failed)
     */
    NOT_EARNED("notEarned"),
    
    /**
     * Assignment was not submitted
     */
    NOT_SUBMITTED("notSubmitted");

    private final String value;

    ScoreStatusEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    public static ScoreStatusEnum fromValue(String value) {
        for (ScoreStatusEnum status : ScoreStatusEnum.values()) {
            if (status.value.equals(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Invalid ScoreStatus value: " + value);
    }
}
