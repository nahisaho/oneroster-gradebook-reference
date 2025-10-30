package org.imsglobal.oneroster.gradebook.service;

import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.CategoryDto;
import org.imsglobal.oneroster.gradebook.mapper.CategoryMapper;
import org.imsglobal.oneroster.gradebook.model.Category;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.CategoryRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service for Category operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class CategoryService {

    private final CategoryRepository categoryRepository;
    private final CategoryMapper categoryMapper;

    /**
     * Get all categories with pagination
     */
    @Transactional(readOnly = true)
    public Page<CategoryDto> getAllCategories(Pageable pageable) {
        return categoryRepository.findAll(pageable)
                .map(categoryMapper::toDto);
    }

    /**
     * Get category by sourcedId
     */
    @Transactional(readOnly = true)
    public CategoryDto getCategoryBySourcedId(String sourcedId) {
        Category category = categoryRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Category not found: " + sourcedId));
        return categoryMapper.toDto(category);
    }

    /**
     * Create new category
     */
    public CategoryDto createCategory(CategoryDto categoryDTO) {
        // Generate sourcedId if not provided
        if (categoryDTO.getSourcedId() == null || categoryDTO.getSourcedId().isEmpty()) {
            categoryDTO.setSourcedId(UUID.randomUUID().toString());
        }

        // Check for duplicate sourcedId
        if (categoryRepository.existsBySourcedId(categoryDTO.getSourcedId())) {
            throw new IllegalArgumentException("Category with sourcedId already exists: " + categoryDTO.getSourcedId());
        }

        Category category = categoryMapper.toEntity(categoryDTO);
        if (category.getStatus() == null) {
            category.setStatus(StatusEnum.ACTIVE);
        }

        Category savedCategory = categoryRepository.save(category);
        return categoryMapper.toDto(savedCategory);
    }

    /**
     * Update existing category
     */
    public CategoryDto updateCategory(String sourcedId, CategoryDto categoryDTO) {
        Category category = categoryRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Category not found: " + sourcedId));

        // Update only provided fields
        categoryMapper.updateEntityFromDto(categoryDTO, category);

        Category updatedCategory = categoryRepository.save(category);
        return categoryMapper.toDto(updatedCategory);
    }

    /**
     * Delete category (soft delete)
     */
    public void deleteCategory(String sourcedId) {
        Category category = categoryRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Category not found: " + sourcedId));

        category.setStatus(StatusEnum.TOBEDELETED);
        categoryRepository.save(category);
    }
}
