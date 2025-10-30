package org.imsglobal.oneroster.gradebook.service;

import org.imsglobal.oneroster.gradebook.dto.ResultDto;
import org.imsglobal.oneroster.gradebook.mapper.ResultMapper;
import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.imsglobal.oneroster.gradebook.model.Result;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.repository.LineItemRepository;
import org.imsglobal.oneroster.gradebook.repository.ResultRepository;
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
class ResultServiceTest {

    @Mock
    private ResultRepository resultRepository;

    @Mock
    private LineItemRepository lineItemRepository;

    @Mock
    private ResultMapper resultMapper;

    @InjectMocks
    private ResultService resultService;

    private Result result;
    private ResultDto resultDto;
    private LineItem lineItem;

    @BeforeEach
    void setUp() {
        lineItem = new LineItem();
        lineItem.setSourcedId("test-lineitem-1");
        lineItem.setTitle("Quiz 1");

        result = new Result();
        result.setSourcedId("test-result-1");
        result.setStudentId("student-1");
        result.setStatus(StatusEnum.ACTIVE);
        result.setLineItem(lineItem);

        resultDto = new ResultDto();
        resultDto.setSourcedId("test-result-1");
        resultDto.setStudentId("student-1");
        resultDto.setStatus(StatusEnum.ACTIVE);
        resultDto.setLineItemSourcedId("test-lineitem-1");
    }

    @Test
    void testGetAllResults() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<Result> resultPage = new PageImpl<>(List.of(result));
        when(resultRepository.findAll(pageable)).thenReturn(resultPage);
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        Page<ResultDto> resultPage2 = resultService.getAllResults(pageable);

        // Then
        assertNotNull(resultPage2);
        assertEquals(1, resultPage2.getTotalElements());
        verify(resultRepository).findAll(pageable);
    }

    @Test
    void testGetResultBySourcedId() {
        // Given
        when(resultRepository.findBySourcedId("test-result-1")).thenReturn(Optional.of(result));
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        ResultDto foundResult = resultService.getResultBySourcedId("test-result-1");

        // Then
        assertNotNull(foundResult);
        assertEquals("test-result-1", foundResult.getSourcedId());
        verify(resultRepository).findBySourcedId("test-result-1");
    }

    @Test
    void testGetResultBySourcedId_NotFound() {
        // Given
        when(resultRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.getResultBySourcedId("non-existent")
        );
    }

    @Test
    void testGetResultsByLineItemSourcedId() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<Result> resultPage = new PageImpl<>(List.of(result));
        when(resultRepository.findByLineItemSourcedId("test-lineitem-1", pageable)).thenReturn(resultPage);
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        Page<ResultDto> results = resultService.getResultsByLineItemSourcedId("test-lineitem-1", pageable);

        // Then
        assertNotNull(results);
        assertEquals(1, results.getTotalElements());
        verify(resultRepository).findByLineItemSourcedId("test-lineitem-1", pageable);
    }

    @Test
    void testGetResultsByStudentId() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);
        Page<Result> resultPage = new PageImpl<>(List.of(result));
        when(resultRepository.findByStudentId("student-1", pageable)).thenReturn(resultPage);
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        Page<ResultDto> results = resultService.getResultsByStudentId("student-1", pageable);

        // Then
        assertNotNull(results);
        assertEquals(1, results.getTotalElements());
        verify(resultRepository).findByStudentId("student-1", pageable);
    }

    @Test
    void testCreateResult() {
        // Given
        when(resultRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(resultMapper.toEntity(resultDto)).thenReturn(result);
        when(resultRepository.save(any(Result.class))).thenReturn(result);
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        ResultDto createdResult = resultService.createResult(resultDto);

        // Then
        assertNotNull(createdResult);
        verify(lineItemRepository).findBySourcedId("test-lineitem-1");
        verify(resultRepository).save(any(Result.class));
    }

    @Test
    void testCreateResult_WithoutSourcedId() {
        // Given
        ResultDto dtoWithoutId = new ResultDto();
        dtoWithoutId.setStudentId("student-1");
        dtoWithoutId.setLineItemSourcedId("test-lineitem-1");
        when(resultRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(resultMapper.toEntity(any(ResultDto.class))).thenReturn(result);
        when(resultRepository.save(any(Result.class))).thenReturn(result);
        when(resultMapper.toDto(result)).thenReturn(resultDto);

        // When
        ResultDto createdResult = resultService.createResult(dtoWithoutId);

        // Then
        assertNotNull(createdResult);
        assertNotNull(dtoWithoutId.getSourcedId());
    }

    @Test
    void testCreateResult_DuplicateSourcedId() {
        // Given
        when(resultRepository.existsBySourcedId("test-result-1")).thenReturn(true);

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.createResult(resultDto)
        );
    }

    @Test
    void testUpdateResult() {
        // Given
        when(resultRepository.findBySourcedId("test-result-1")).thenReturn(Optional.of(result));
        when(lineItemRepository.findBySourcedId("test-lineitem-1")).thenReturn(Optional.of(lineItem));
        when(resultRepository.save(any(Result.class))).thenReturn(result);
        when(resultMapper.toDto(result)).thenReturn(resultDto);
        doNothing().when(resultMapper).updateEntityFromDto(any(), any());

        // When
        ResultDto updatedResult = resultService.updateResult("test-result-1", resultDto);

        // Then
        assertNotNull(updatedResult);
        verify(resultRepository).findBySourcedId("test-result-1");
        verify(resultRepository).save(result);
    }

    @Test
    void testUpdateResult_NotFound() {
        // Given
        when(resultRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.updateResult("non-existent", resultDto)
        );
    }

    @Test
    void testDeleteResult() {
        // Given
        when(resultRepository.findBySourcedId("test-result-1")).thenReturn(Optional.of(result));
        when(resultRepository.save(any(Result.class))).thenReturn(result);

        // When
        resultService.deleteResult("test-result-1");

        // Then
        assertEquals(StatusEnum.TOBEDELETED, result.getStatus());
        verify(resultRepository).save(result);
    }

    @Test
    void testDeleteResult_NotFound() {
        // Given
        when(resultRepository.findBySourcedId(anyString())).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.deleteResult("non-existent")
        );
    }

    @Test
    void testCreateResult_LineItemNotFound() {
        // Given
        ResultDto dtoWithInvalidLineItem = new ResultDto();
        dtoWithInvalidLineItem.setSourcedId("test-result-2");
        dtoWithInvalidLineItem.setStudentId("student-1");
        dtoWithInvalidLineItem.setLineItemSourcedId("invalid-lineitem");
        when(resultRepository.existsBySourcedId(anyString())).thenReturn(false);
        when(lineItemRepository.findBySourcedId("invalid-lineitem")).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.createResult(dtoWithInvalidLineItem)
        );
    }

    @Test
    void testUpdateResult_LineItemNotFound() {
        // Given
        ResultDto dtoWithInvalidLineItem = new ResultDto();
        dtoWithInvalidLineItem.setLineItemSourcedId("invalid-lineitem");
        when(resultRepository.findBySourcedId("test-result-1")).thenReturn(Optional.of(result));
        when(lineItemRepository.findBySourcedId("invalid-lineitem")).thenReturn(Optional.empty());

        // When/Then
        assertThrows(IllegalArgumentException.class, () -> 
            resultService.updateResult("test-result-1", dtoWithInvalidLineItem)
        );
    }
}
