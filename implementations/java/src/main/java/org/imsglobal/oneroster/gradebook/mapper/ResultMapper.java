package org.imsglobal.oneroster.gradebook.mapper;

import org.imsglobal.oneroster.gradebook.dto.ResultDto;
import org.imsglobal.oneroster.gradebook.model.Result;
import org.mapstruct.*;

/**
 * MapStruct mapper for Result entity and DTO
 */
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ResultMapper {

    /**
     * Convert entity to DTO
     */
    @Mapping(source = "lineItem.sourcedId", target = "lineItemSourcedId")
    ResultDto toDto(Result result);

    /**
     * Convert DTO to entity (lineItem relationship handled separately)
     */
    @Mapping(target = "lineItem", ignore = true)
    Result toEntity(ResultDto resultDTO);

    /**
     * Update entity from DTO, ignoring null values
     */
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "lineItem", ignore = true)
    void updateEntityFromDto(ResultDto dto, @MappingTarget Result entity);
}
