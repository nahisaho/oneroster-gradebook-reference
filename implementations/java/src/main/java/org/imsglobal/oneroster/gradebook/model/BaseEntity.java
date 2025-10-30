package org.imsglobal.oneroster.gradebook.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

/**
 * Base entity class for all OneRoster entities
 * 
 * Provides common fields like sourcedId, status, and audit timestamps
 */
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Unique identifier from the source system (OneRoster GUID)
     */
    @Column(nullable = false, unique = true, length = 255)
    private String sourcedId;

    /**
     * Status of the entity (active or tobedeleted)
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private StatusEnum status = StatusEnum.ACTIVE;

    /**
     * Timestamp of last modification (managed by JPA auditing)
     */
    @LastModifiedDate
    @Column(name = "date_last_modified")
    private LocalDateTime dateLastModified;

    /**
     * Metadata as JSON text
     */
    @Column(columnDefinition = "TEXT")
    private String metadata;
}
