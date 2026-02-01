-- Create storage bucket for contracts
INSERT INTO storage.buckets (id, name, public)
VALUES ('contracts', 'contracts', false)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for contracts bucket
CREATE POLICY "Users can upload own contract files"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'contracts'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can view own contract files"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'contracts'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete own contract files"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'contracts'
    AND auth.uid()::text = (storage.foldername(name))[1]
);
