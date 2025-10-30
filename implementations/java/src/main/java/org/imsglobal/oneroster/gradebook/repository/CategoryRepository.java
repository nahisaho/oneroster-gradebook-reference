package org.imsglobal.oneroster.gradebook.repository;

import org.imsglobal.oneroster.gradebook.model.Category;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for Category entity
 */
@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {

    /**
     * Find category by sourcedId
     */
    Optional<Category> findBySourcedId(String sourcedId);

    /**
     * Find all categories with pagination
     */
    Page<Category> findAll(Pageable pageable);

    /**
     * Check if category exists by sourcedId
     */
    boolean existsBySourcedId(String sourcedId);
}
