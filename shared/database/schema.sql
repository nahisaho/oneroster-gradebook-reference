-- ================================================================
-- OneRoster Gradebook Service - Database Schema
-- Version: 1.0.0
-- Database: PostgreSQL 12+
-- Description: OneRoster 1.2 Gradebook Service data model
-- ================================================================

-- ================================================================
-- Extensions
-- ================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- Enums
-- ================================================================
CREATE TYPE status_enum AS ENUM ('active', 'tobedeleted');

CREATE TYPE score_status_enum AS ENUM (
    'earnedPartial',
    'earnedFull',
    'notEarned',
    'notSubmitted',
    'submitted',
    'late',
    'incomplete',
    'missing',
    'inProgress',
    'withdrawn'
);

-- ================================================================
-- Functions
-- ================================================================
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- Table: categories
-- ================================================================
CREATE TABLE categories (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status status_enum NOT NULL DEFAULT 'active',
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    weight DECIMAL(5, 4) CHECK (weight >= 0.0 AND weight <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT chk_title_length CHECK (char_length(title) >= 1)
);

-- Indexes for categories
CREATE INDEX idx_categories_status ON categories(status);
CREATE INDEX idx_categories_modified ON categories(date_last_modified);

-- Trigger for categories
CREATE TRIGGER update_categories_modtime
    BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Comments for categories
COMMENT ON TABLE categories IS 'OneRoster Gradebook Categories - used to group and weight LineItems';
COMMENT ON COLUMN categories.sourced_id IS 'Unique identifier for the category';
COMMENT ON COLUMN categories.status IS 'Status: active or tobedeleted';
COMMENT ON COLUMN categories.date_last_modified IS 'Timestamp of last modification';
COMMENT ON COLUMN categories.title IS 'Human-readable name of the category (e.g., Homework, Exams)';
COMMENT ON COLUMN categories.weight IS 'Weighting factor (0.0-1.0) for grade calculation';

-- ================================================================
-- Table: line_items
-- ================================================================
CREATE TABLE line_items (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status status_enum NOT NULL DEFAULT 'active',
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Core fields
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assign_date DATE,
    due_date DATE,
    
    -- References to Rostering Service
    class_sourced_id VARCHAR(255) NOT NULL,
    grading_period_sourced_id VARCHAR(255),
    academic_session_sourced_id VARCHAR(255),
    school_sourced_id VARCHAR(255),
    
    -- Reference to local Category
    category_sourced_id VARCHAR(255),
    
    -- Score configuration
    score_scale_sourced_id VARCHAR(255),
    result_value_min DECIMAL(10, 2),
    result_value_max DECIMAL(10, 2),
    
    -- Learning objectives (CASE framework)
    learning_objective_set JSONB,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_lineitem_category
        FOREIGN KEY (category_sourced_id)
        REFERENCES categories(sourced_id)
        ON DELETE SET NULL,
    
    CONSTRAINT chk_title_length CHECK (char_length(title) >= 1),
    CONSTRAINT chk_result_values CHECK (
        (result_value_min IS NULL AND result_value_max IS NULL) OR
        (result_value_min IS NOT NULL AND result_value_max IS NOT NULL AND result_value_min < result_value_max)
    ),
    CONSTRAINT chk_dates CHECK (
        (assign_date IS NULL OR due_date IS NULL) OR
        (assign_date <= due_date)
    )
);

-- Indexes for line_items
CREATE INDEX idx_line_items_status ON line_items(status);
CREATE INDEX idx_line_items_class ON line_items(class_sourced_id);
CREATE INDEX idx_line_items_category ON line_items(category_sourced_id);
CREATE INDEX idx_line_items_grading_period ON line_items(grading_period_sourced_id);
CREATE INDEX idx_line_items_academic_session ON line_items(academic_session_sourced_id);
CREATE INDEX idx_line_items_school ON line_items(school_sourced_id);
CREATE INDEX idx_line_items_modified ON line_items(date_last_modified);
CREATE INDEX idx_line_items_due_date ON line_items(due_date);

-- Trigger for line_items
CREATE TRIGGER update_line_items_modtime
    BEFORE UPDATE ON line_items
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Comments for line_items
COMMENT ON TABLE line_items IS 'OneRoster Gradebook LineItems - represents gradable assignments/assessments';
COMMENT ON COLUMN line_items.sourced_id IS 'Unique identifier for the line item';
COMMENT ON COLUMN line_items.title IS 'Name of the assignment/assessment';
COMMENT ON COLUMN line_items.class_sourced_id IS 'Reference to Class in Rostering Service';
COMMENT ON COLUMN line_items.category_sourced_id IS 'Foreign key to categories table';
COMMENT ON COLUMN line_items.result_value_min IS 'Minimum possible score';
COMMENT ON COLUMN line_items.result_value_max IS 'Maximum possible score';

-- ================================================================
-- Table: results
-- ================================================================
CREATE TABLE results (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status status_enum NOT NULL DEFAULT 'active',
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- References
    line_item_sourced_id VARCHAR(255) NOT NULL,
    student_sourced_id VARCHAR(255) NOT NULL,
    class_sourced_id VARCHAR(255),
    
    -- Score information
    score_status score_status_enum,
    score DECIMAL(10, 2),
    text_score VARCHAR(255),
    score_date DATE,
    comment TEXT,
    score_scale_sourced_id VARCHAR(255),
    
    -- Learning objectives
    learning_objective_set JSONB,
    
    -- Flags
    in_progress BOOLEAN DEFAULT FALSE,
    incomplete BOOLEAN DEFAULT FALSE,
    late BOOLEAN DEFAULT FALSE,
    missing BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_result_lineitem
        FOREIGN KEY (line_item_sourced_id)
        REFERENCES line_items(sourced_id)
        ON DELETE CASCADE,
    
    CONSTRAINT chk_score_types CHECK (
        (score IS NULL OR text_score IS NULL) OR
        (score IS NOT NULL OR text_score IS NOT NULL)
    ),
    
    -- Unique constraint: one result per student per line item
    CONSTRAINT uk_result_student_lineitem
        UNIQUE (line_item_sourced_id, student_sourced_id)
);

-- Indexes for results
CREATE INDEX idx_results_status ON results(status);
CREATE INDEX idx_results_lineitem ON results(line_item_sourced_id);
CREATE INDEX idx_results_student ON results(student_sourced_id);
CREATE INDEX idx_results_class ON results(class_sourced_id);
CREATE INDEX idx_results_modified ON results(date_last_modified);
CREATE INDEX idx_results_score_date ON results(score_date);
CREATE INDEX idx_results_score_status ON results(score_status);

-- Trigger for results
CREATE TRIGGER update_results_modtime
    BEFORE UPDATE ON results
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Comments for results
COMMENT ON TABLE results IS 'OneRoster Gradebook Results - individual student scores for line items';
COMMENT ON COLUMN results.sourced_id IS 'Unique identifier for the result';
COMMENT ON COLUMN results.line_item_sourced_id IS 'Foreign key to line_items table';
COMMENT ON COLUMN results.student_sourced_id IS 'Reference to User (student) in Rostering Service';
COMMENT ON COLUMN results.score IS 'Numeric score value';
COMMENT ON COLUMN results.text_score IS 'Text-based score (e.g., letter grade, rubric level)';
COMMENT ON COLUMN results.score_status IS 'Status of the submission/grading';

-- ================================================================
-- Table: score_scales (optional, for v1.2 ScoreScale support)
-- ================================================================
CREATE TABLE score_scales (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status status_enum NOT NULL DEFAULT 'active',
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Core fields
    title VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    
    -- Scope
    course_sourced_id VARCHAR(255),
    class_sourced_id VARCHAR(255),
    
    -- Scale definition (JSON array of scale values)
    score_scale_value JSONB NOT NULL,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_title_length CHECK (char_length(title) >= 1)
);

-- Indexes for score_scales
CREATE INDEX idx_score_scales_status ON score_scales(status);
CREATE INDEX idx_score_scales_class ON score_scales(class_sourced_id);
CREATE INDEX idx_score_scales_course ON score_scales(course_sourced_id);
CREATE INDEX idx_score_scales_modified ON score_scales(date_last_modified);

-- Trigger for score_scales
CREATE TRIGGER update_score_scales_modtime
    BEFORE UPDATE ON score_scales
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Comments for score_scales
COMMENT ON TABLE score_scales IS 'OneRoster Gradebook ScoreScales - defines grading scales (letter grades, rubrics, etc.)';
COMMENT ON COLUMN score_scales.sourced_id IS 'Unique identifier for the score scale';
COMMENT ON COLUMN score_scales.title IS 'Name of the score scale (e.g., "Letter Grades A-F")';
COMMENT ON COLUMN score_scales.score_scale_value IS 'JSON array defining scale values and thresholds';

-- ================================================================
-- Sample Data (for development/testing)
-- ================================================================

-- Sample Categories
INSERT INTO categories (sourced_id, status, title, weight) VALUES
('cat-homework', 'active', 'Homework', 0.30),
('cat-quizzes', 'active', 'Quizzes', 0.20),
('cat-exams', 'active', 'Exams', 0.50);

-- Sample LineItems
INSERT INTO line_items (
    sourced_id, status, title, description, 
    assign_date, due_date, class_sourced_id, 
    category_sourced_id, result_value_min, result_value_max
) VALUES
('li-chapter1-quiz', 'active', 'Chapter 1 Quiz', 'Quiz covering chapter 1 material',
 '2024-10-01', '2024-10-07', 'class-math-101', 'cat-quizzes', 0, 100),
 
('li-homework1', 'active', 'Homework Assignment 1', 'Practice problems from chapter 1',
 '2024-10-01', '2024-10-05', 'class-math-101', 'cat-homework', 0, 50),
 
('li-midterm', 'active', 'Midterm Exam', 'Comprehensive midterm examination',
 '2024-11-01', '2024-11-15', 'class-math-101', 'cat-exams', 0, 200);

-- Sample Results
INSERT INTO results (
    sourced_id, status, line_item_sourced_id, student_sourced_id,
    score_status, score, score_date, late, missing
) VALUES
('result-student1-chapter1quiz', 'active', 'li-chapter1-quiz', 'user-student-1',
 'submitted', 85, '2024-10-07', false, false),
 
('result-student2-chapter1quiz', 'active', 'li-chapter1-quiz', 'user-student-2',
 'submitted', 92, '2024-10-06', false, false),
 
('result-student1-homework1', 'active', 'li-homework1', 'user-student-1',
 'submitted', 45, '2024-10-08', true, false);

-- Sample ScoreScale
INSERT INTO score_scales (sourced_id, status, title, type, class_sourced_id, score_scale_value) VALUES
('scale-letter-grades', 'active', 'Letter Grades A-F', 'letter',
 'class-math-101',
 '[
    {"label": "A", "min": 90, "max": 100},
    {"label": "B", "min": 80, "max": 89},
    {"label": "C", "min": 70, "max": 79},
    {"label": "D", "min": 60, "max": 69},
    {"label": "F", "min": 0, "max": 59}
 ]'::jsonb);

-- ================================================================
-- Utility Views (optional)
-- ================================================================

-- View: Active Categories
CREATE VIEW v_active_categories AS
SELECT * FROM categories
WHERE status = 'active';

-- View: Active LineItems with Category Info
CREATE VIEW v_active_lineitems AS
SELECT 
    li.*,
    c.title AS category_title,
    c.weight AS category_weight
FROM line_items li
LEFT JOIN categories c ON li.category_sourced_id = c.sourced_id
WHERE li.status = 'active';

-- View: Student Results Summary
CREATE VIEW v_student_results AS
SELECT 
    r.student_sourced_id,
    r.class_sourced_id,
    li.title AS lineitem_title,
    li.category_sourced_id,
    c.title AS category_title,
    r.score,
    r.text_score,
    r.score_status,
    r.score_date,
    r.late,
    r.missing
FROM results r
INNER JOIN line_items li ON r.line_item_sourced_id = li.sourced_id
LEFT JOIN categories c ON li.category_sourced_id = c.sourced_id
WHERE r.status = 'active' AND li.status = 'active';

-- ================================================================
-- Permissions (example for application user)
-- ================================================================

-- Create application user (uncomment and modify as needed)
-- CREATE USER gradebook_app WITH PASSWORD 'your_secure_password';

-- Grant permissions
-- GRANT CONNECT ON DATABASE gradebook TO gradebook_app;
-- GRANT USAGE ON SCHEMA public TO gradebook_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gradebook_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gradebook_app;

-- ================================================================
-- Maintenance Functions
-- ================================================================

-- Function to purge tobedeleted records older than 90 days
CREATE OR REPLACE FUNCTION purge_deleted_records()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    row_count_temp INTEGER;
BEGIN
    -- Delete results
    DELETE FROM results
    WHERE status = 'tobedeleted'
    AND date_last_modified < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS row_count_temp = ROW_COUNT;
    deleted_count := deleted_count + row_count_temp;
    
    -- Delete line_items
    DELETE FROM line_items
    WHERE status = 'tobedeleted'
    AND date_last_modified < NOW() - INTERVAL '90 days'
    AND sourced_id NOT IN (SELECT DISTINCT line_item_sourced_id FROM results);
    
    GET DIAGNOSTICS row_count_temp = ROW_COUNT;
    deleted_count := deleted_count + row_count_temp;
    
    -- Delete categories
    DELETE FROM categories
    WHERE status = 'tobedeleted'
    AND date_last_modified < NOW() - INTERVAL '90 days'
    AND sourced_id NOT IN (SELECT DISTINCT category_sourced_id FROM line_items WHERE category_sourced_id IS NOT NULL);
    
    GET DIAGNOSTICS row_count_temp = ROW_COUNT;
    deleted_count := deleted_count + row_count_temp;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- Database Information
-- ================================================================

-- Query to check table sizes
CREATE VIEW v_table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ================================================================
-- End of Schema
-- ================================================================
