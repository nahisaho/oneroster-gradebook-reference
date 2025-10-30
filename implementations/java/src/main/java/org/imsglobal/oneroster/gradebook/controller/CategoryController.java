package org.imsglobal.oneroster.gradebook.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.CategoryDto;
import org.imsglobal.oneroster.gradebook.service.CategoryService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for Category operations
 */
@RestController
@RequestMapping("/ims/oneroster/v1p2/categories")
@RequiredArgsConstructor
public class CategoryController {

    private final CategoryService categoryService;

    /**
     * Get all categories
     * Requires: read scope
     */
    @GetMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<Page<CategoryDto>> getAllCategories(
            @RequestParam(defaultValue = "0") int offset,
            @RequestParam(defaultValue = "100") int limit) {
        
        Pageable pageable = PageRequest.of(offset / limit, limit);
        Page<CategoryDto> categories = categoryService.getAllCategories(pageable);
        return ResponseEntity.ok(categories);
    }

    /**
     * Get category by sourcedId
     * Requires: read scope
     */
    @GetMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<CategoryDto> getCategoryBySourcedId(@PathVariable String sourcedId) {
        CategoryDto category = categoryService.getCategoryBySourcedId(sourcedId);
        return ResponseEntity.ok(category);
    }

    /**
     * Create new category
     * Requires: core write scope
     */
    @PostMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<CategoryDto> createCategory(@Valid @RequestBody CategoryDto categoryDTO) {
        CategoryDto createdCategory = categoryService.createCategory(categoryDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdCategory);
    }

    /**
     * Update existing category
     * Requires: core write scope
     */
    @PutMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<CategoryDto> updateCategory(
            @PathVariable String sourcedId,
            @Valid @RequestBody CategoryDto categoryDTO) {
        
        CategoryDto updatedCategory = categoryService.updateCategory(sourcedId, categoryDTO);
        return ResponseEntity.ok(updatedCategory);
    }

    /**
     * Delete category (soft delete)
     * Requires: core write scope
     */
    @DeleteMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<Void> deleteCategory(@PathVariable String sourcedId) {
        categoryService.deleteCategory(sourcedId);
        return ResponseEntity.noContent().build();
    }
}
