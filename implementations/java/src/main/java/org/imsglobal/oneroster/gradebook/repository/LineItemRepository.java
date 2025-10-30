package org.imsglobal.oneroster.gradebook.repository;

import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for LineItem entity
 */
@Repository
public interface LineItemRepository extends JpaRepository<LineItem, Long> {

    /**
     * Find line item by sourcedId
     */
    Optional<LineItem> findBySourcedId(String sourcedId);

    /**
     * Find all line items with pagination
     */
    Page<LineItem> findAll(Pageable pageable);

    /**
     * Find line items by category sourcedId
     */
    @Query("SELECT li FROM LineItem li WHERE li.category.sourcedId = :categorySourcedId")
    Page<LineItem> findByCategorySourcedId(@Param("categorySourcedId") String categorySourcedId, Pageable pageable);

    /**
     * Check if line item exists by sourcedId
     */
    boolean existsBySourcedId(String sourcedId);
}
