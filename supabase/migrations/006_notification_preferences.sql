-- User notification preferences
CREATE TABLE user_notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    
    -- Email reminders
    email_reminders_enabled BOOLEAN DEFAULT true,
    reminder_days_before INTEGER[] DEFAULT ARRAY[7, 30, 60],
    
    -- Analysis notifications
    analysis_notifications BOOLEAN DEFAULT true,
    
    -- Weekly summary
    weekly_summary_enabled BOOLEAN DEFAULT false,
    weekly_summary_day TEXT DEFAULT 'monday',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_notification_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own preferences" ON user_notification_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_notification_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_notification_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- Trigger to create preferences on user signup
CREATE OR REPLACE FUNCTION create_user_notification_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_notification_preferences (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION create_user_notification_preferences();

-- Function to get contracts with upcoming renewals
CREATE OR REPLACE FUNCTION get_upcoming_renewals(p_user_id UUID, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    id UUID,
    provider_name TEXT,
    contract_type TEXT,
    end_date DATE,
    next_renewal_date DATE,
    monthly_cost DECIMAL(10,2),
    currency TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.provider_name,
        c.contract_type,
        c.end_date,
        c.next_renewal_date,
        c.monthly_cost,
        c.currency
    FROM contracts c
    WHERE c.user_id = p_user_id
      AND c.next_renewal_date IS NOT NULL
      AND c.next_renewal_date <= CURRENT_DATE + (p_days || ' days')::INTERVAL
      AND c.next_renewal_date >= CURRENT_DATE
    ORDER BY c.next_renewal_date ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
