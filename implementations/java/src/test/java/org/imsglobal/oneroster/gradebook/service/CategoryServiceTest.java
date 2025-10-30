package org.imsglobal.oneroster.gradebook.service;

import org.imsglobal.oneroster.gradebook.dto.CategoryDto;
import org.imsglobal.oneroster.gradebook.mapper.CategoryMapper;
import org.imsglobal.oneroster.gradebook.model.Category;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.CategoryRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CategoryServiceTest {

    @Mock
    private CategoryRepository categoryRepository;

    @Mock
    private CategoryMapper categoryMapper;

    @InjectMocks
    private CategoryService categoryService;

    private Category category;
    private CategoryDto categoryDto;

    @BeforeEach
    void setUp() {
        category = new Category();
        category.setSourcedId("test-category-1");
        category.setTitle("Homework");
        category.setStatus(StatusEnum.ACTIVE);

        categoryDto = new CategoryDto();
        categoryDto.setSourcedId("test-category-1");
        categoryDto.setTitle("Homework");
        categoryDto.setStatus(StatusEnum.ACTIVE);
    }

    @Test
    void testGetAllCategories() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<Category> categoryPage = new PageImpl<>(List.of(category));
        when(categoryRepository.findAll(pageable)).thenReturn(categoryPage);
        when(categoryMapper.toDto(category)).thenReturn(categoryDto);

        // When
        Page<CategoryDto> result = categoryService.getAllCategories(pageable);

        // Then
        assertNotNull(result);
        assertEquals(1, result.getTotalElements());
        assertEquals("test-category-1", result.getContent().get(0).getSourcedId());
        verify(categoryRepository).findAll(pageable);
        verify(categoryMapper).toDto(category);
    }

    @Test
    void testGetCategoryBySourcedId() {
        // Given
        when(categoryRepository.findBySourcedId("test-category-1")).thenReturn(Optional.of(category));
        when(categoryMapper.toDto(category)).thenReturn(categoryDto);

        // When
        CategoryDto result = categoryService.getCategoryBySourcedId("test-category-1");

        // Then
        assertNotNull(result);
        assertEquals("test-category-1", result.getSourcedId());
        verify(categoryRepository).findBySourcedId("test-category-1");
        verify(categoryMapper).toDto(category);
    }

    @Test
    void testGetCategoryBySourcedId_NotFound() {
        // Given
        when(categoryRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            categoryService.getCategoryBySourcedId("non-existent")
        );
    }

    @Test
    void testCreateCategory() {
        // Given
        when(categoryRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(categoryMapper.toEntity(categoryDto)).thenReturn(category);
        when(categoryRepository.save(any(Category.class))).thenReturn(category);
        when(categoryMapper.toDto(category)).thenReturn(categoryDto);

        // When
        CategoryDto result = categoryService.createCategory(categoryDto);

        // Then
        assertNotNull(result);
        assertEquals("test-category-1", result.getSourcedId());
        verify(categoryRepository).existsBySourcedId("test-category-1");
        verify(categoryRepository).save(any(Category.class));
    }

    @Test
    void testCreateCategory_WithoutSourcedId() {
        // Given
        CategoryDto dtoWithoutId = new CategoryDto();
        dtoWithoutId.setTitle("Test");
        when(categoryRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(categoryMapper.toEntity(any(CategoryDto.class))).thenReturn(category);
        when(categoryRepository.save(any(Category.class))).thenReturn(category);
        when(categoryMapper.toDto(category)).thenReturn(categoryDto);

        // When
        CategoryDto result = categoryService.createCategory(dtoWithoutId);

        // Then
        assertNotNull(result);
        assertNotNull(dtoWithoutId.getSourcedId()); // UUID should be generated
        verify(categoryRepository).save(any(Category.class));
    }

    @Test
    void testCreateCategory_DuplicateSourcedId() {
        // Given
        when(categoryRepository.existsBySourcedId("test-category-1")).thenReturn(true);

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            categoryService.createCategory(categoryDto)
        );
    }

    @Test
    void testUpdateCategory() {
        // Given
        when(categoryRepository.findBySourcedId("test-category-1")).thenReturn(Optional.of(category));
        when(categoryRepository.save(any(Category.class))).thenReturn(category);
        when(categoryMapper.toDto(category)).thenReturn(categoryDto);
        doNothing().when(categoryMapper).updateEntityFromDto(any(), any());

        // When
        CategoryDto result = categoryService.updateCategory("test-category-1", categoryDto);

        // Then
        assertNotNull(result);
        verify(categoryRepository).findBySourcedId("test-category-1");
        verify(categoryMapper).updateEntityFromDto(categoryDto, category);
        verify(categoryRepository).save(category);
    }

    @Test
    void testUpdateCategory_NotFound() {
        // Given
        when(categoryRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            categoryService.updateCategory("non-existent", categoryDto)
        );
    }

    @Test
    void testDeleteCategory() {
        // Given
        when(categoryRepository.findBySourcedId("test-category-1")).thenReturn(Optional.of(category));
        when(categoryRepository.save(any(Category.class))).thenReturn(category);

        // When
        categoryService.deleteCategory("test-category-1");

        // Then
        assertEquals(StatusEnum.TOBEDELETED, category.getStatus());
        verify(categoryRepository).findBySourcedId("test-category-1");
        verify(categoryRepository).save(category);
    }

    @Test
    void testDeleteCategory_NotFound() {
        // Given
        when(categoryRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            categoryService.deleteCategory("non-existent")
        );
    }
}
