package org.imsglobal.oneroster.gradebook.service;

import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.ResultDto;
import org.imsglobal.oneroster.gradebook.mapper.ResultMapper;
import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.imsglobal.oneroster.gradebook.model.Result;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.LineItemRepository;
import org.imsglobal.oneroster.gradebook.repository.ResultRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service for Result operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class ResultService {

    private final ResultRepository resultRepository;
    private final LineItemRepository lineItemRepository;
    private final ResultMapper resultMapper;

    /**
     * Get all results with pagination
     */
    @Transactional(readOnly = true)
    public Page<ResultDto> getAllResults(Pageable pageable) {
        return resultRepository.findAll(pageable)
                .map(resultMapper::toDto);
    }

    /**
     * Get result by sourcedId
     */
    @Transactional(readOnly = true)
    public ResultDto getResultBySourcedId(String sourcedId) {
        Result result = resultRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Result not found: " + sourcedId));
        return resultMapper.toDto(result);
    }

    /**
     * Get results by line item sourcedId
     */
    @Transactional(readOnly = true)
    public Page<ResultDto> getResultsByLineItemSourcedId(String lineItemSourcedId, Pageable pageable) {
        return resultRepository.findByLineItemSourcedId(lineItemSourcedId, pageable)
                .map(resultMapper::toDto);
    }

    /**
     * Get results by student ID
     */
    @Transactional(readOnly = true)
    public Page<ResultDto> getResultsByStudentId(String studentId, Pageable pageable) {
        return resultRepository.findByStudentId(studentId, pageable)
                .map(resultMapper::toDto);
    }

    /**
     * Create new result
     */
    public ResultDto createResult(ResultDto resultDTO) {
        // Generate sourcedId if not provided
        if (resultDTO.getSourcedId() == null || resultDTO.getSourcedId().isEmpty()) {
            resultDTO.setSourcedId(UUID.randomUUID().toString());
        }

        // Check for duplicate sourcedId
        if (resultRepository.existsBySourcedId(resultDTO.getSourcedId())) {
            throw new IllegalArgumentException("Result with sourcedId already exists: " + resultDTO.getSourcedId());
        }

        Result result = resultMapper.toEntity(resultDTO);

        // Set line item (required)
        if (resultDTO.getLineItemSourcedId() == null || resultDTO.getLineItemSourcedId().isEmpty()) {
            throw new IllegalArgumentException("LineItem sourcedId is required");
        }

        LineItem lineItem = lineItemRepository.findBySourcedId(resultDTO.getLineItemSourcedId())
                .orElseThrow(() -> new IllegalArgumentException("LineItem not found: " + resultDTO.getLineItemSourcedId()));
        result.setLineItem(lineItem);

        if (result.getStatus() == null) {
            result.setStatus(StatusEnum.ACTIVE);
        }

        Result savedResult = resultRepository.save(result);
        return resultMapper.toDto(savedResult);
    }

    /**
     * Update existing result
     */
    public ResultDto updateResult(String sourcedId, ResultDto resultDTO) {
        Result result = resultRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Result not found: " + sourcedId));

        // Update line item if provided
        if (resultDTO.getLineItemSourcedId() != null && !resultDTO.getLineItemSourcedId().isEmpty()) {
            LineItem lineItem = lineItemRepository.findBySourcedId(resultDTO.getLineItemSourcedId())
                    .orElseThrow(() -> new IllegalArgumentException("LineItem not found: " + resultDTO.getLineItemSourcedId()));
            result.setLineItem(lineItem);
        }

        // Update only provided fields
        resultMapper.updateEntityFromDto(resultDTO, result);

        Result updatedResult = resultRepository.save(result);
        return resultMapper.toDto(updatedResult);
    }

    /**
     * Delete result (soft delete)
     */
    public void deleteResult(String sourcedId) {
        Result result = resultRepository.findBySourcedId(sourcedId)
                .orElseThrow(() -> new IllegalArgumentException("Result not found: " + sourcedId));

        result.setStatus(StatusEnum.TOBEDELETED);
        resultRepository.save(result);
    }
}
