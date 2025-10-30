package org.imsglobal.oneroster.gradebook.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.imsglobal.oneroster.gradebook.dto.ResultDto;
import org.imsglobal.oneroster.gradebook.model.enums.ScoreStatusEnum;
import org.imsglobal.oneroster.gradebook.model.enums.StatusEnum;
import org.imsglobal.oneroster.gradebook.service.ResultService;
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
public class ResultControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ResultService resultService;

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getAllResults_shouldReturnResults() throws Exception {
        ResultDto result = new ResultDto();
        result.setSourcedId("res-1");
        result.setStudentId("student-1");
        result.setLineItemSourcedId("li-1");
        result.setScore(new BigDecimal("85.50"));
        result.setScorePercent(new BigDecimal("0.8550"));
        result.setScoreStatus(ScoreStatusEnum.EARNED_FULL);
        result.setComment("Good work");
        result.setStatus(StatusEnum.ACTIVE);

        when(resultService.getAllResults(any()))
                .thenReturn(new PageImpl<>(List.of(result), PageRequest.of(0, 100), 1));

        mockMvc.perform(get("/ims/oneroster/v1p2/results"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].sourcedId").value("res-1"))
                .andExpect(jsonPath("$.content[0].studentId").value("student-1"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly")
    void getResultBySourcedId_shouldReturnResult() throws Exception {
        ResultDto result = new ResultDto();
        result.setSourcedId("res-1");
        result.setStudentId("student-1");
        result.setScore(new BigDecimal("85.50"));

        when(resultService.getResultBySourcedId("res-1")).thenReturn(result);

        mockMvc.perform(get("/ims/oneroster/v1p2/results/res-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sourcedId").value("res-1"))
                .andExpect(jsonPath("$.studentId").value("student-1"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput")
    void createResult_shouldCreateResult() throws Exception {
        ResultDto inputDto = new ResultDto();
        inputDto.setStudentId("student-1");
        inputDto.setLineItemSourcedId("li-1");
        inputDto.setScore(new BigDecimal("85.50"));
        inputDto.setScorePercent(new BigDecimal("0.8550"));
        inputDto.setScoreStatus(ScoreStatusEnum.EARNED_FULL);
        inputDto.setComment("Good work");

        ResultDto outputDto = new ResultDto();
        outputDto.setSourcedId("res-1");
        outputDto.setStudentId("student-1");
        outputDto.setLineItemSourcedId("li-1");
        outputDto.setScore(new BigDecimal("85.50"));
        outputDto.setScorePercent(new BigDecimal("0.8550"));
        outputDto.setScoreStatus(ScoreStatusEnum.EARNED_FULL);
        outputDto.setComment("Good work");
        outputDto.setStatus(StatusEnum.ACTIVE);

        when(resultService.createResult(any(ResultDto.class))).thenReturn(outputDto);

        mockMvc.perform(post("/ims/oneroster/v1p2/results")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sourcedId").value("res-1"))
                .andExpect(jsonPath("$.studentId").value("student-1"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput")
    void updateResult_shouldUpdateResult() throws Exception {
        ResultDto inputDto = new ResultDto();
        inputDto.setStudentId("student-1");
        inputDto.setLineItemSourcedId("li-1");
        inputDto.setScore(new BigDecimal("90.00"));
        inputDto.setComment("Excellent improvement");

        ResultDto outputDto = new ResultDto();
        outputDto.setSourcedId("res-1");
        outputDto.setStudentId("student-1");
        outputDto.setLineItemSourcedId("li-1");
        outputDto.setScore(new BigDecimal("90.00"));
        outputDto.setComment("Excellent improvement");

        when(resultService.updateResult(eq("res-1"), any(ResultDto.class))).thenReturn(outputDto);

        mockMvc.perform(put("/ims/oneroster/v1p2/results/res-1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(inputDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.comment").value("Excellent improvement"));
    }

    @Test
    @WithMockUser(authorities = "SCOPE_https://purl.imsglobal.org/spec/or/v1p2/scope/gradebook.createput")
    void deleteResult_shouldDeleteResult() throws Exception {
        doNothing().when(resultService).deleteResult("res-1");

        mockMvc.perform(delete("/ims/oneroster/v1p2/results/res-1")
                        .with(csrf()))
                .andExpect(status().isNoContent());
    }

    @Test
    void getAllResults_withoutAuth_shouldReturnForbidden() throws Exception {
        // In test environment with permitAll(), access denied returns 403
        mockMvc.perform(get("/ims/oneroster/v1p2/results"))
                .andExpect(status().isForbidden());
    }
}
