-- Create contracts table
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Basic info
    provider_name TEXT NOT NULL,
    contract_type TEXT CHECK (contract_type IN ('insurance', 'utility', 'subscription', 'rental', 'saas', 'service', 'other')),

    -- Financial
    monthly_cost DECIMAL(10,2),
    annual_cost DECIMAL(10,2),
    currency TEXT DEFAULT 'USD',
    payment_frequency TEXT CHECK (payment_frequency IN ('monthly', 'annual', 'quarterly', 'one-time', 'other')),

    -- Dates
    start_date DATE,
    end_date DATE,
    next_renewal_date DATE,
    cancellation_deadline DATE,

    -- Terms
    auto_renewal BOOLEAN DEFAULT true,
    cancellation_notice_days INTEGER,
    key_terms JSONB DEFAULT '[]'::jsonb,

    -- File reference
    file_path TEXT,
    file_name TEXT,

    -- Extraction metadata
    extracted_text TEXT,
    extraction_confidence DECIMAL(3,2) CHECK (extraction_confidence >= 0 AND extraction_confidence <= 1),
    user_verified BOOLEAN DEFAULT false,
    raw_extraction JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contracts_updated_at
    BEFORE UPDATE ON contracts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own contracts" ON contracts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own contracts" ON contracts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own contracts" ON contracts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own contracts" ON contracts
    FOR DELETE USING (auth.uid() = user_id);

-- Indexes for performance
CREATE INDEX idx_contracts_user_id ON contracts(user_id);
CREATE INDEX idx_contracts_end_date ON contracts(end_date);
CREATE INDEX idx_contracts_contract_type ON contracts(contract_type);
