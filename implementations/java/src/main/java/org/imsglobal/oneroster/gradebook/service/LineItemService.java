package org.imsglobal.oneroster.gradebook.service;

import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.LineItemDto;
import org.imsglobal.oneroster.gradebook.mapper.LineItemMapper;
import org.imsglobal.oneroster.gradebook.model.Category;
import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.CategoryRepository;
import org.imsglobal.oneroster.gradebook.repository.LineItemRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service for LineItem operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class LineItemService {

    private final LineItemRepository lineItemRepository;
    private final CategoryRepository categoryRepository;
    private final LineItemMapper lineItemMapper;

    /**
     * Get all line items with pagination
     */
    @Transactional(readOnly = true)
    public Page<LineItemDto> getAllLineItems(Pageable pageable) {
        return lineItemRepository.findAll(pageable)
                .map(lineItemMapper::toDto);
    }

    /**
     * Get line item by sourcedId
     */
    @Transactional(readOnly = true)
    public LineItemDto getLineItemBySourcedId(String sourcedId) {
        LineItem lineItem = lineItemRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("LineItem not found: " + sourcedId));
        return lineItemMapper.toDto(lineItem);
    }

    /**
     * Get line items by category sourcedId
     */
    @Transactional(readOnly = true)
    public Page<LineItemDto> getLineItemsByCategorySourcedId(String categorySourcedId, Pageable pageable) {
        return lineItemRepository.findByCategorySourcedId(categorySourcedId, pageable)
                .map(lineItemMapper::toDto);
    }

    /**
     * Create new line item
     */
    public LineItemDto createLineItem(LineItemDto lineItemDTO) {
        // Generate sourcedId if not provided
        if (lineItemDTO.getSourcedId() == null || lineItemDTO.getSourcedId().isEmpty()) {
            lineItemDTO.setSourcedId(UUID.randomUUID().toString());
        }

        // Check for duplicate sourcedId
        if (lineItemRepository.existsBySourcedId(lineItemDTO.getSourcedId())) {
            throw new IllegalArgumentException("LineItem with sourcedId already exists: " + lineItemDTO.getSourcedId());
        }

        LineItem lineItem = lineItemMapper.toEntity(lineItemDTO);

        // Set category if provided
        if (lineItemDTO.getCategorySourcedId() != null && !lineItemDTO.getCategorySourcedId().isEmpty()) {
            Category category = categoryRepository.findBySourcedId(lineItemDTO.getCategorySourcedId())
                    .orElseThrow(() -> new IllegalArgumentException("Category not found: " + lineItemDTO.getCategorySourcedId()));
            lineItem.setCategory(category);
        }

        if (lineItem.getStatus() == null) {
            lineItem.setStatus(StatusEnum.ACTIVE);
        }

        LineItem savedLineItem = lineItemRepository.save(lineItem);
        return lineItemMapper.toDto(savedLineItem);
    }

    /**
     * Update existing line item
     */
    public LineItemDto updateLineItem(String sourcedId, LineItemDto lineItemDTO) {
        LineItem lineItem = lineItemRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("LineItem not found: " + sourcedId));

        // Update category if provided
        if (lineItemDTO.getCategorySourcedId() != null && !lineItemDTO.getCategorySourcedId().isEmpty()) {
            Category category = categoryRepository.findBySourcedId(lineItemDTO.getCategorySourcedId())
                    .orElseThrow(() -> new IllegalArgumentException("Category not found: " + lineItemDTO.getCategorySourcedId()));
            lineItem.setCategory(category);
        }

        // Update only provided fields
        lineItemMapper.updateEntityFromDto(lineItemDTO, lineItem);

        LineItem updatedLineItem = lineItemRepository.save(lineItem);
        return lineItemMapper.toDto(updatedLineItem);
    }

    /**
     * Delete line item (soft delete)
     */
    public void deleteLineItem(String sourcedId) {
        LineItem lineItem = lineItemRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("LineItem not found: " + sourcedId));

        lineItem.setStatus(StatusEnum.TOBEDELETED);
        lineItemRepository.save(lineItem);
    }
}
