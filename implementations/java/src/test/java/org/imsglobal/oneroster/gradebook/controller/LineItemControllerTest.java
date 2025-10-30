package org.imsglobal.oneroster.gradebook.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.imsglobal.oneroster.gradebook.dto.LineItemDto;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.service.LineItemService;
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
import java.time.LocalDate;
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
public class LineItemControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private LineItemService lineItemService;

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getAllLineItems_shouldReturnLineItems() throws Exception {
        LineItemDto lineItem = new LineItemDto();
        lineItem.setSourcedId("li-1");
        lineItem.setTitle("Midterm Exam");
        lineItem.setDescription("Chapter 1-5");
        lineItem.setAssignDate(LocalDate.of(2024, 1, 10));
        lineItem.setDueDate(LocalDate.of(2024, 1, 20));
        lineItem.setScoreMaximum(new BigDecimal("100.00"));
        lineItem.setStatus(StatusEnum.ACTIVE);

        when(lineItemService.getAllLineItems(any()))
                .thenReturn(new PageImpl<>(List.of(lineItem), PageRequest.of(0, 100), 1));

        mockMvc.perform(get("/ims/oneroster/v1p2/lineItems"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].sourcedId").value("li-1"))
                .andExpect(jsonPath("$.content[0].title").value("Midterm Exam"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getLineItemBySourcedId_shouldReturnLineItem() throws Exception {
        LineItemDto lineItem = new LineItemDto();
        lineItem.setSourcedId("li-1");
        lineItem.setTitle("Midterm Exam");
        lineItem.setScoreMaximum(new BigDecimal("100.00"));

        when(lineItemService.getLineItemBySourcedId("li-1")).thenReturn(lineItem);

        mockMvc.perform(get("/ims/oneroster/v1p2/lineItems/li-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sourcedId").value("li-1"))
                .andExpect(jsonPath("$.title").value("Midterm Exam"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void createLineItem_shouldCreateLineItem() throws Exception {
        LineItemDto inputDto = new LineItemDto();
        inputDto.setTitle("Midterm Exam");
        inputDto.setDescription("Chapter 1-5");
        inputDto.setAssignDate(LocalDate.of(2024, 1, 10));
        inputDto.setDueDate(LocalDate.of(2024, 1, 20));
        inputDto.setScoreMaximum(new BigDecimal("100.00"));
        inputDto.setCategorySourcedId("cat-1");

        LineItemDto outputDto = new LineItemDto();
        outputDto.setSourcedId("li-1");
        outputDto.setTitle("Midterm Exam");
        outputDto.setDescription("Chapter 1-5");
        outputDto.setAssignDate(LocalDate.of(2024, 1, 10));
        outputDto.setDueDate(LocalDate.of(2024, 1, 20));
        outputDto.setScoreMaximum(new BigDecimal("100.00"));
        outputDto.setStatus(StatusEnum.ACTIVE);

        when(lineItemService.createLineItem(any(LineItemDto.class))).thenReturn(outputDto);

        mockMvc.perform(post("/ims/oneroster/v1p2/lineItems")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sourcedId").value("li-1"))
                .andExpect(jsonPath("$.title").value("Midterm Exam"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void updateLineItem_shouldUpdateLineItem() throws Exception {
        LineItemDto inputDto = new LineItemDto();
        inputDto.setTitle("Updated Midterm Exam");
        inputDto.setScoreMaximum(new BigDecimal("120.00"));

        LineItemDto outputDto = new LineItemDto();
        outputDto.setSourcedId("li-1");
        outputDto.setTitle("Updated Midterm Exam");
        outputDto.setScoreMaximum(new BigDecimal("120.00"));

        when(lineItemService.updateLineItem(eq("li-1"), any(LineItemDto.class))).thenReturn(outputDto);

        mockMvc.perform(put("/ims/oneroster/v1p2/lineItems/li-1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Updated Midterm Exam"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.createput")
    void deleteLineItem_shouldDeleteLineItem() throws Exception {
        doNothing().when(lineItemService).deleteLineItem("li-1");

        mockMvc.perform(delete("/ims/oneroster/v1p2/lineItems/li-1")
                        .with(csrf()))
                .andExpect(status().isNoContent());
    }

    @Test
    void getAllLineItems_withoutAuth_shouldReturnForbidden() throws Exception {
        // In test environment with permitAll(), access denied returns 403
        mockMvc.perform(get("/ims/oneroster/v1p2/lineItems"))
                .andExpect(status().isForbidden());
    }
}
