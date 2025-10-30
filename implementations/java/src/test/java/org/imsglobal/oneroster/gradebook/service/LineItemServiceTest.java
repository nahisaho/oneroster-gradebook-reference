package org.imsglobal.oneroster.gradebook.service;

import org.imsglobal.oneroster.gradebook.dto.LineItemDto;
import org.imsglobal.oneroster.gradebook.mapper.LineItemMapper;
import org.imsglobal.oneroster.gradebook.model.Category;
import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.CategoryRepository;
import org.imsglobal.oneroster.gradebook.repository.LineItemRepository;
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
class LineItemServiceTest {

    @Mock
    private LineItemRepository lineItemRepository;

    @Mock
    private CategoryRepository categoryRepository;

    @Mock
    private LineItemMapper lineItemMapper;

    @InjectMocks
    private LineItemService lineItemService;

    private LineItem lineItem;
    private LineItemDto lineItemDto;
    private Category category;

    @BeforeEach
    void setUp() {
        category = new Category();
        category.setSourcedId("test-category-1");
        category.setTitle("Homework");

        lineItem = new LineItem();
        lineItem.setSourcedId("test-lineitem-1");
        lineItem.setTitle("Quiz 1");
        lineItem.setStatus(StatusEnum.ACTIVE);
        lineItem.setCategory(category);

        lineItemDto = new LineItemDto();
        lineItemDto.setSourcedId("test-lineitem-1");
        lineItemDto.setTitle("Quiz 1");
        lineItemDto.setStatus(StatusEnum.ACTIVE);
        lineItemDto.setCategorySourcedId("test-category-1");
    }

    @Test
    void testGetAllLineItems() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<LineItem> lineItemPage = new PageImpl<>(List.of(lineItem));
        when(lineItemRepository.findAll(pageable)).thenReturn(lineItemPage);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        Page<LineItemDto> result = lineItemService.getAllLineItems(pageable);

        // Then
        assertNotNull(result);
        assertEquals(1, result.getTotalElements());
        verify(lineItemRepository).findAll(pageable);
    }

    @Test
    void testGetLineItemBySourcedId() {
        // Given
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        LineItemDto result = lineItemService.getLineItemBySourcedId("test-lineitem-1");

        // Then
        assertNotNull(result);
        assertEquals("test-lineitem-1", result.getSourcedId());
        verify(lineItemRepository).findBySourcedId("test-lineitem-1");
    }

    @Test
    void testGetLineItemBySourcedId_NotFound() {
        // Given
        when(lineItemRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.getLineItemBySourcedId("non-existent")
        );
    }

    @Test
    void testGetLineItemsByCategorySourcedId() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<LineItem> lineItemPage = new PageImpl<>(List.of(lineItem));
        when(lineItemRepository.findByCategorySourcedId("test-category-1", pageable)).thenReturn(lineItemPage);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        Page<LineItemDto> result = lineItemService.getLineItemsByCategorySourcedId("test-category-1", pageable);

        // Then
        assertNotNull(result);
        assertEquals(1, result.getTotalElements());
        verify(lineItemRepository).findByCategorySourcedId("test-category-1", pageable);
    }

    @Test
    void testCreateLineItem() {
        // Given
        when(lineItemRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(categoryRepository.findBySourcedId("test-category-1")).thenReturn(Optional.of(category));
        when(lineItemMapper.toEntity(lineItemDto)).thenReturn(lineItem);
        when(lineItemRepository.save(any(LineItem.class))).thenReturn(lineItem);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        LineItemDto result = lineItemService.createLineItem(lineItemDto);

        // Then
        assertNotNull(result);
        verify(categoryRepository).findBySourcedId("test-category-1");
        verify(lineItemRepository).save(any(LineItem.class));
    }

    @Test
    void testCreateLineItem_WithoutCategory() {
        // Given
        LineItemDto dtoWithoutCategory = new LineItemDto();
        dtoWithoutCategory.setSourcedId("test-lineitem-2");
        dtoWithoutCategory.setTitle("Test");
        when(lineItemRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(lineItemMapper.toEntity(any(LineItemDto.class))).thenReturn(lineItem);
        when(lineItemRepository.save(any(LineItem.class))).thenReturn(lineItem);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        LineItemDto result = lineItemService.createLineItem(dtoWithoutCategory);

        // Then
        assertNotNull(result);
        verify(categoryRepository, never()).findBySourcedId(anyString());
        verify(lineItemRepository).save(any(LineItem.class));
    }

    @Test
    void testCreateLineItem_WithoutSourcedId() {
        // Given
        LineItemDto dtoWithoutId = new LineItemDto();
        dtoWithoutId.setTitle("Test");
        when(lineItemRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(lineItemMapper.toEntity(any(LineItemDto.class))).thenReturn(lineItem);
        when(lineItemRepository.save(any(LineItem.class))).thenReturn(lineItem);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);

        // When
        LineItemDto result = lineItemService.createLineItem(dtoWithoutId);

        // Then
        assertNotNull(result);
        assertNotNull(dtoWithoutId.getSourcedId());
    }

    @Test
    void testCreateLineItem_DuplicateSourcedId() {
        // Given
        when(lineItemRepository.existsBySourcedId("test-lineitem-1")).thenReturn(true);

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.createLineItem(lineItemDto)
        );
    }

    @Test
    void testUpdateLineItem() {
        // Given
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(categoryRepository.findBySourcedId("test-category-1")).thenReturn(Optional.of(category));
        when(lineItemRepository.save(any(LineItem.class))).thenReturn(lineItem);
        when(lineItemMapper.toDto(lineItem)).thenReturn(lineItemDto);
        doNothing().when(lineItemMapper).updateEntityFromDto(any(), any());

        // When
        LineItemDto result = lineItemService.updateLineItem("test-lineitem-1", lineItemDto);

        // Then
        assertNotNull(result);
        verify(lineItemRepository).findBySourcedId("test-lineitem-1");
        verify(categoryRepository).findBySourcedId("test-category-1");
        verify(lineItemRepository).save(lineItem);
    }

    @Test
    void testUpdateLineItem_NotFound() {
        // Given
        when(lineItemRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.updateLineItem("non-existent", lineItemDto)
        );
    }

    @Test
    void testDeleteLineItem() {
        // Given
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(lineItemRepository.save(any(LineItem.class))).thenReturn(lineItem);

        // When
        lineItemService.deleteLineItem("test-lineitem-1");

        // Then
        assertEquals(StatusEnum.TOBEDELETED, lineItem.getStatus());
        verify(lineItemRepository).save(lineItem);
    }

    @Test
    void testDeleteLineItem_NotFound() {
        // Given
        when(lineItemRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.deleteLineItem("non-existent")
        );
    }

    @Test
    void testCreateLineItem_CategoryNotFound() {
        // Given
        LineItemDto dtoWithInvalidCategory = new LineItemDto();
        dtoWithInvalidCategory.setSourcedId("test-lineitem-3");
        dtoWithInvalidCategory.setTitle("Test");
        dtoWithInvalidCategory.setCategorySourcedId("invalid-category");
        when(lineItemRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(categoryRepository.findBySourcedId("invalid-category")).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.createLineItem(dtoWithInvalidCategory)
        );
    }

    @Test
    void testUpdateLineItem_CategoryNotFound() {
        // Given
        LineItemDto dtoWithInvalidCategory = new LineItemDto();
        dtoWithInvalidCategory.setCategorySourcedId("invalid-category");
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(categoryRepository.findBySourcedId("invalid-category")).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            lineItemService.updateLineItem("test-lineitem-1", dtoWithInvalidCategory)
        );
    }
}
