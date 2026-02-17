CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- SERIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.series (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.series IS 'Sonny Angel series (e.g., Animal Series, Fruit Series)';

-- =====================================================
-- ANGELS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.angels (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    card_number VARCHAR(50),
    series_id BIGINT REFERENCES public.series(id) ON DELETE CASCADE,
    image VARCHAR(500),
    image_bw VARCHAR(500),
    image_opacity VARCHAR(500),
    image_profile_pic VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_angels_series ON public.angels(series_id);

COMMENT ON TABLE public.angels IS 'Individual Sonny Angels with image variants';
COMMENT ON COLUMN public.angels.image IS 'Original color image path';
COMMENT ON COLUMN public.angels.image_bw IS 'Black and white variant path';
COMMENT ON COLUMN public.angels.image_opacity IS 'Reduced opacity variant path';
COMMENT ON COLUMN public.angels.image_profile_pic IS 'Circular cropped profile picture path';

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    profile_pic VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_users_email ON public.users(email);

COMMENT ON TABLE public.users IS 'App-specific user profiles (extends Supabase auth.users)';

-- =====================================================
-- USER COLLECTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_collections (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    angel_id BIGINT REFERENCES public.angels(id) ON DELETE CASCADE,
    count INT DEFAULT 0,
    is_favorite BOOLEAN DEFAULT FALSE,
    in_search_of BOOLEAN DEFAULT FALSE,
    willing_to_trade BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, angel_id)
);

CREATE INDEX idx_user_collections_user ON public.user_collections(user_id);
CREATE INDEX idx_user_collections_angel ON public.user_collections(angel_id);

COMMENT ON TABLE public.user_collections IS 'User angel collections (owned, wishlist, trade list)';
COMMENT ON COLUMN public.user_collections.count IS 'How many of this angel the user owns';
COMMENT ON COLUMN public.user_collections.in_search_of IS 'User is looking for this angel';
COMMENT ON COLUMN public.user_collections.willing_to_trade IS 'User willing to trade this angel';

-- =====================================================
-- AUDIT LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'success'
);

CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON public.audit_logs(resource);
CREATE INDEX idx_audit_logs_timestamp ON public.audit_logs(timestamp DESC);

COMMENT ON TABLE public.audit_logs IS 'Audit trail for all sensitive operations';

-- =====================================================
-- JOB RUNS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.job_runs (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'success', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    images_found INTEGER DEFAULT 0,
    images_processed INTEGER DEFAULT 0,
    images_uploaded INTEGER DEFAULT 0,
    angels_created INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_job_runs_status ON public.job_runs(status);
CREATE INDEX idx_job_runs_started_at ON public.job_runs(started_at DESC);
CREATE INDEX idx_job_runs_job_name ON public.job_runs(job_name);

COMMENT ON TABLE public.job_runs IS 'Tracks automated job executions';

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================
ALTER TABLE public.series ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.angels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_collections ENABLE ROW LEVEL SECURITY;

-- Series and Angels: Public read access
CREATE POLICY "Series are viewable by everyone"
    ON public.series FOR SELECT
    USING (true);

CREATE POLICY "Angels are viewable by everyone"
    ON public.angels FOR SELECT
    USING (true);

-- Users: Users can manage their own profile
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can create own profile"
    ON public.users FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- User Collections: Users can manage their own collections
CREATE POLICY "Users can view own collections"
    ON public.user_collections FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own collections"
    ON public.user_collections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own collections"
    ON public.user_collections FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own collections"
    ON public.user_collections FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_collections_updated_at
    BEFORE UPDATE ON public.user_collections
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- PERMISSIONS
-- =====================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
