-- Migration: Add status and error tracking columns to analysis_results table
-- Date: 2024-11-08

-- Add status column
ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'completed';

-- Add error tracking columns
ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS error_message TEXT;

ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS error_details TEXT;

-- Add index for status
CREATE INDEX IF NOT EXISTS idx_analysis_results_status ON analysis_results(status);

-- Success message
SELECT 'Migration completed: Added status and error columns to analysis_results' as message;
