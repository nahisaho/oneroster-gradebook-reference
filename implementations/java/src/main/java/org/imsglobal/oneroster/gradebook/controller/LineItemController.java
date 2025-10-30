package org.imsglobal.oneroster.gradebook.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.imsglobal.oneroster.gradebook.dto.LineItemDto;
import org.imsglobal.oneroster.gradebook.service.LineItemService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for LineItem operations
 */
@RestController
@RequestMapping("/ims/oneroster/v1p2/lineItems")
@RequiredArgsConstructor
public class LineItemController {

    private final LineItemService lineItemService;

    /**
     * Get all line items
     * Requires: read scope
     */
    @GetMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<Page<LineItemDto>> getAllLineItems(
            @RequestParam(defaultValue = "0") int offset,
            @RequestParam(defaultValue = "100") int limit) {
        
        Pageable pageable = PageRequest.of(offset / limit, limit);
        Page<LineItemDto> lineItems = lineItemService.getAllLineItems(pageable);
        return ResponseEntity.ok(lineItems);
    }

    /**
     * Get line item by sourcedId
     * Requires: read scope
     */
    @GetMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly')")
    public ResponseEntity<LineItemDto> getLineItemBySourcedId(@PathVariable String sourcedId) {
        LineItemDto lineItem = lineItemService.getLineItemBySourcedId(sourcedId);
        return ResponseEntity.ok(lineItem);
    }

    /**
     * Create new line item
     * Requires: core write scope
     */
    @PostMapping
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<LineItemDto> createLineItem(@Valid @RequestBody LineItemDto lineItemDTO) {
        LineItemDto createdLineItem = lineItemService.createLineItem(lineItemDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdLineItem);
    }

    /**
     * Update existing line item
     * Requires: core write scope
     */
    @PutMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<LineItemDto> updateLineItem(
            @PathVariable String sourcedId,
            @Valid @RequestBody LineItemDto lineItemDTO) {
        
        LineItemDto updatedLineItem = lineItemService.updateLineItem(sourcedId, lineItemDTO);
        return ResponseEntity.ok(updatedLineItem);
    }

    /**
     * Delete line item (soft delete)
     * Requires: core write scope
     */
    @DeleteMapping("/{sourcedId}")
    @PreAuthorize("hasAuthority('SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput')")
    public ResponseEntity<Void> deleteLineItem(@PathVariable String sourcedId) {
        lineItemService.deleteLineItem(sourcedId);
        return ResponseEntity.noContent().build();
    }
}
