-- Create recommendations table
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Recommendation details
    type TEXT NOT NULL CHECK (type IN ('cost_reduction', 'consolidation', 'risk_alert', 'renewal_reminder')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Impact
    estimated_savings DECIMAL(10,2),
    priority TEXT CHECK (priority IN ('high', 'medium', 'low')),

    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'accepted', 'dismissed')),

    -- AI metadata
    reasoning TEXT,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acted_on_at TIMESTAMPTZ
);

-- Enable Row Level Security
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own recommendations" ON recommendations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own recommendations" ON recommendations
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own recommendations" ON recommendations
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can insert recommendations (from backend)
CREATE POLICY "Service role can insert recommendations" ON recommendations
    FOR INSERT WITH CHECK (true);

-- Indexes
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_contract_id ON recommendations(contract_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
