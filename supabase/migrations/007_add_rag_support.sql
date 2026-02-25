-- Add full_text column to store extracted PDF text for RAG
ALTER TABLE contracts
ADD COLUMN IF NOT EXISTS full_text TEXT;

-- Create table for text chunks with embeddings
-- Using simple JSONB for chunks since pgvector might not be enabled
CREATE TABLE IF NOT EXISTS contract_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE contract_chunks ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own chunks" ON contract_chunks
    FOR SELECT USING (
        contract_id IN (SELECT id FROM contracts WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own chunks" ON contract_chunks
    FOR INSERT WITH CHECK (
        contract_id IN (SELECT id FROM contracts WHERE user_id = auth.uid())
    );

-- Index for text search
CREATE INDEX IF NOT EXISTS idx_contract_chunks_contract_id ON contract_chunks(contract_id);

-- Full-text search index (optional, for better search)
CREATE INDEX IF NOT EXISTS idx_contract_chunks_text ON contract_chunks USING gin(to_tsvector('english', chunk_text));
