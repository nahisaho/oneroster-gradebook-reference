package org.imsglobal.oneroster.gradebook.repository;

import org.imsglobal.oneroster.gradebook.model.Result;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for Result entity
 */
@Repository
public interface ResultRepository extends JpaRepository<Result, Long> {

    /**
     * Find result by sourcedId
     */
    Optional<Result> findBySourcedId(String sourcedId);

    /**
     * Find all results with pagination
     */
    Page<Result> findAll(Pageable pageable);

    /**
     * Find results by line item sourcedId
     */
    @Query("SELECT r FROM Result r WHERE r.lineItem.sourcedId = :lineItemSourcedId")
    Page<Result> findByLineItemSourcedId(@Param("lineItemSourcedId") String lineItemSourcedId, Pageable pageable);

    /**
     * Find results by student ID
     */
    Page<Result> findByStudentId(String studentId, Pageable pageable);

    /**
     * Check if result exists by sourcedId
     */
    boolean existsBySourcedId(String sourcedId);
}
