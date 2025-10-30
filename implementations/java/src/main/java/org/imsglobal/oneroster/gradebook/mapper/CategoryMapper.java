package org.imsglobal.oneroster.gradebook.mapper;

import org.imsglobal.oneroster.gradebook.dto.CategoryDto;
import org.imsglobal.oneroster.gradebook.model.Category;
import org.mapstruct.*;

/**
 * MapStruct mapper for Category entity and DTO
 */
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface CategoryMapper {

    /**
     * Convert entity to DTO
     */
    CategoryDto toDto(Category category);

    /**
     * Convert DTO to entity
     */
    Category toEntity(CategoryDto categoryDTO);

    /**
     * Update entity from DTO, ignoring null values
     */
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    void updateEntityFromDto(CategoryDto dto, @MappingTarget Category entity);
}
