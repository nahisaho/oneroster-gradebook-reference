package org.imsglobal.oneroster.gradebook.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.ResultDto;
import org.imsglobal.oneroster.gradebook.service.ResultService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for Result operations
 */
@RestController
@RequestMapping("/ims/oneroster/v1p2/results")
@RequiredArgsConstructor
public class ResultController {

    private final ResultService resultService;

    /**
     * Get all results
     * Requires: read scope
     */
    @GetMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<Page<ResultDto>> getAllResults(
            @RequestParam(defaultValue = "0") int offset,
            @RequestParam(defaultValue = "100") int limit) {
        
        Pageable pageable = PageRequest.of(offset / limit, limit);
        Page<ResultDto> results = resultService.getAllResults(pageable);
        return ResponseEntity.ok(results);
    }

    /**
     * Get result by sourcedId
     * Requires: read scope
     */
    @GetMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<ResultDto> getResultBySourcedId(@PathVariable String sourcedId) {
        ResultDto result = resultService.getResultBySourcedId(sourcedId);
        return ResponseEntity.ok(result);
    }

    /**
     * Create new result
     * Requires: gradebook write scope
     */
    @PostMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput')")
    public ResponseEntity<ResultDto> createResult(@Valid @RequestBody ResultDto resultDTO) {
        ResultDto createdResult = resultService.createResult(resultDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdResult);
    }

    /**
     * Update existing result
     * Requires: gradebook write scope
     */
    @PutMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput')")
    public ResponseEntity<ResultDto> updateResult(
            @PathVariable String sourcedId,
            @Valid @RequestBody ResultDto resultDTO) {
        
        ResultDto updatedResult = resultService.updateResult(sourcedId, resultDTO);
        return ResponseEntity.ok(updatedResult);
    }

    /**
     * Delete result (soft delete)
     * Requires: gradebook write scope
     */
    @DeleteMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput')")
    public ResponseEntity<Void> deleteResult(@PathVariable String sourcedId) {
        resultService.deleteResult(sourcedId);
        return ResponseEntity.noContent().build();
    }
}
