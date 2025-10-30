package org.imsglobal.oneroster.gradebook.mapper;

import org.imsglobal.oneroster.gradebook.dto.LineItemDto;
import org.imsglobal.oneroster.gradebook.model.LineItem;
import org.mapstruct.*;

/**
 * MapStruct mapper for LineItem entity and DTO
 */
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface LineItemMapper {

    /**
     * Convert entity to DTO
     */
    @Mapping(source = "category.sourcedId", target = "categorySourcedId")
    LineItemDto toDto(LineItem lineItem);

    /**
     * Convert DTO to entity (category relationship handled separately)
     */
    @Mapping(target = "category", ignore = true)
    LineItem toEntity(LineItemDto lineItemDTO);

    /**
     * Update entity from DTO, ignoring null values
     */
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "category", ignore = true)
    void updateEntityFromDto(LineItemDto dto, @MappingTarget LineItem entity);
}
