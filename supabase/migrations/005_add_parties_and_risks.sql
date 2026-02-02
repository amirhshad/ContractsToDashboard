-- Migration: Add parties and risks columns to contracts table
-- Parties: Array of entities involved in the contract (names and roles)
-- Risks: Array of identified risks and concerns

-- Add parties column (JSONB array)
ALTER TABLE contracts
ADD COLUMN IF NOT EXISTS parties JSONB DEFAULT '[]'::jsonb;

-- Add risks column (JSONB array)
ALTER TABLE contracts
ADD COLUMN IF NOT EXISTS risks JSONB DEFAULT '[]'::jsonb;

-- Add comment for documentation
COMMENT ON COLUMN contracts.parties IS 'Array of {name, role} objects representing parties in the contract';
COMMENT ON COLUMN contracts.risks IS 'Array of {title, description, severity} objects representing identified risks';
