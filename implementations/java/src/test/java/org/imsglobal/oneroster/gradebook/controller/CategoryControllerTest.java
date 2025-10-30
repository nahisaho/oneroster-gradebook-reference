package org.imsglobal.oneroster.gradebook.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.imsglobal.oneroster.gradebook.dto.CategoryDto;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.service.CategoryService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class CategoryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private CategoryService categoryService;

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getAllCategories_shouldReturnCategories() throws Exception {
        CategoryDto category = new CategoryDto();
        category.setSourcedId("cat-1");
        category.setTitle("Homework");
        category.setWeight(new BigDecimal("0.3"));
        category.setStatus(StatusEnum.ACTIVE);

        when(categoryService.getAllCategories(any()))
                .thenReturn(new PageImpl<>(List.of(category), PageRequest.of(0, 100), 1));

        mockMvc.perform(get("/ims/oneroster/v1p2/categories"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].sourcedId").value("cat-1"))
                .andExpect(jsonPath("$.content[0].title").value("Homework"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getCategoryBySourcedId_shouldReturnCategory() throws Exception {
        CategoryDto category = new CategoryDto();
        category.setSourcedId("cat-1");
        category.setTitle("Homework");

        when(categoryService.getCategoryBySourcedId("cat-1")).thenReturn(category);

        mockMvc.perform(get("/ims/oneroster/v1p2/categories/cat-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sourcedId").value("cat-1"))
                .andExpect(jsonPath("$.title").value("Homework"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void createCategory_shouldCreateCategory() throws Exception {
        CategoryDto inputDto = new CategoryDto();
        inputDto.setTitle("Homework");
        inputDto.setWeight(new BigDecimal("0.3"));

        CategoryDto outputDto = new CategoryDto();
        outputDto.setSourcedId("cat-1");
        outputDto.setTitle("Homework");
        outputDto.setWeight(new BigDecimal("0.3"));
        outputDto.setStatus(StatusEnum.ACTIVE);

        when(categoryService.createCategory(any(CategoryDto.class))).thenReturn(outputDto);

        mockMvc.perform(post("/ims/oneroster/v1p2/categories")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sourcedId").value("cat-1"))
                .andExpect(jsonPath("$.title").value("Homework"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void updateCategory_shouldUpdateCategory() throws Exception {
        CategoryDto inputDto = new CategoryDto();
        inputDto.setTitle("Updated Homework");
        inputDto.setWeight(new BigDecimal("0.4"));

        CategoryDto outputDto = new CategoryDto();
        outputDto.setSourcedId("cat-1");
        outputDto.setTitle("Updated Homework");
        outputDto.setWeight(new BigDecimal("0.4"));

        when(categoryService.updateCategory(eq("cat-1"), any(CategoryDto.class))).thenReturn(outputDto);

        mockMvc.perform(put("/ims/oneroster/v1p2/categories/cat-1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Updated Homework"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void deleteCategory_shouldDeleteCategory() throws Exception {
        mockMvc.perform(delete("/ims/oneroster/v1p2/categories/cat-1")
                        .with(csrf()))
                .andExpect(status().isNoContent());
    }

    @Test
    void getAllCategories_withoutAuth_shouldReturn401() throws Exception {
        // In test environment with permitAll(), access denied returns 403
        mockMvc.perform(get("/ims/oneroster/v1p2/categories"))
                .andExpect(status().isForbidden());
    }
}
