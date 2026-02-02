-- Migration: Create contract_files table for multi-document support
-- Each contract can have up to 5 documents (e.g., Framework Agreement + SOWs)

-- Create document type enum
DO $$ BEGIN
    CREATE TYPE document_type AS ENUM (
        'main_agreement',
        'sow',
        'terms_conditions',
        'amendment',
        'addendum',
        'exhibit',
        'schedule',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create contract_files table
CREATE TABLE IF NOT EXISTS contract_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE NOT NULL,

    -- File info
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT DEFAULT 'application/pdf',

    -- Document metadata
    document_type document_type DEFAULT 'other',
    label TEXT,
    display_order INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups by contract
CREATE INDEX IF NOT EXISTS idx_contract_files_contract_id ON contract_files(contract_id);

-- Enable RLS
ALTER TABLE contract_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies (files inherit contract ownership)
CREATE POLICY "Users can view files of own contracts" ON contract_files
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM contracts
            WHERE contracts.id = contract_files.contract_id
            AND contracts.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert files for own contracts" ON contract_files
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM contracts
            WHERE contracts.id = contract_files.contract_id
            AND contracts.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete files of own contracts" ON contract_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM contracts
            WHERE contracts.id = contract_files.contract_id
            AND contracts.user_id = auth.uid()
        )
    );

-- Service role can manage files (for backend operations)
CREATE POLICY "Service role can manage contract files" ON contract_files
    FOR ALL USING (auth.role() = 'service_role');

-- Migrate existing single-file contracts to contract_files table
INSERT INTO contract_files (contract_id, file_path, file_name, document_type, label, display_order)
SELECT
    id,
    file_path,
    file_name,
    'main_agreement'::document_type,
    'Main Agreement',
    0
FROM contracts
WHERE file_path IS NOT NULL
AND file_name IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM contract_files cf WHERE cf.contract_id = contracts.id
);
