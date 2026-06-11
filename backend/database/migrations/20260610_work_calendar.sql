-- Work calendar module
-- NOTE:
-- This codebase currently authenticates users through the backend `usuarios` table
-- and propagates the authenticated user to PostgreSQL through
-- `app.current_user_id`. Because of that, the RLS policies below follow the
-- runtime model that exists today instead of Supabase Auth `auth.uid()`.

BEGIN;

CREATE TABLE IF NOT EXISTS public.work_schedules (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    schedule_type VARCHAR NOT NULL,
    anchor_date DATE NOT NULL,
    state_code VARCHAR NULL,
    city_name VARCHAR NULL,
    working_weekdays_json TEXT NOT NULL DEFAULT '[]',
    custom_pattern_json TEXT NOT NULL DEFAULT '[]',
    note TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.vacation_periods (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL DEFAULT 'Ferias',
    vacation_type VARCHAR NOT NULL DEFAULT 'regular',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    requested_days INTEGER NULL,
    counted_days INTEGER NULL,
    note TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.work_calendar_overrides (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    override_date DATE NOT NULL,
    is_working_day BOOLEAN NOT NULL,
    title VARCHAR NOT NULL DEFAULT 'Excecao manual',
    note TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_work_schedules_user_id_is_active
    ON public.work_schedules (user_id, is_active);
CREATE INDEX IF NOT EXISTS ix_work_schedules_user_id_created_at
    ON public.work_schedules (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_vacation_periods_user_id_start_date
    ON public.vacation_periods (user_id, start_date);
CREATE INDEX IF NOT EXISTS ix_vacation_periods_user_id_end_date
    ON public.vacation_periods (user_id, end_date);
CREATE INDEX IF NOT EXISTS ix_work_calendar_overrides_user_id_override_date
    ON public.work_calendar_overrides (user_id, override_date);

ALTER TABLE public.work_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.work_schedules FORCE ROW LEVEL SECURITY;
ALTER TABLE public.vacation_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vacation_periods FORCE ROW LEVEL SECURITY;
ALTER TABLE public.work_calendar_overrides ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.work_calendar_overrides FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS work_schedules_backend_access ON public.work_schedules;
DROP POLICY IF EXISTS work_schedules_user_access ON public.work_schedules;
CREATE POLICY work_schedules_backend_access ON public.work_schedules
    FOR ALL TO PUBLIC
    USING (current_setting('app.backend_access', true) = 'on')
    WITH CHECK (current_setting('app.backend_access', true) = 'on');
CREATE POLICY work_schedules_user_access ON public.work_schedules
    FOR ALL TO PUBLIC
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER)
    WITH CHECK (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER);

DROP POLICY IF EXISTS vacation_periods_backend_access ON public.vacation_periods;
DROP POLICY IF EXISTS vacation_periods_user_access ON public.vacation_periods;
CREATE POLICY vacation_periods_backend_access ON public.vacation_periods
    FOR ALL TO PUBLIC
    USING (current_setting('app.backend_access', true) = 'on')
    WITH CHECK (current_setting('app.backend_access', true) = 'on');
CREATE POLICY vacation_periods_user_access ON public.vacation_periods
    FOR ALL TO PUBLIC
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER)
    WITH CHECK (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER);

DROP POLICY IF EXISTS work_calendar_overrides_backend_access ON public.work_calendar_overrides;
DROP POLICY IF EXISTS work_calendar_overrides_user_access ON public.work_calendar_overrides;
CREATE POLICY work_calendar_overrides_backend_access ON public.work_calendar_overrides
    FOR ALL TO PUBLIC
    USING (current_setting('app.backend_access', true) = 'on')
    WITH CHECK (current_setting('app.backend_access', true) = 'on');
CREATE POLICY work_calendar_overrides_user_access ON public.work_calendar_overrides
    FOR ALL TO PUBLIC
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER)
    WITH CHECK (user_id = NULLIF(current_setting('app.current_user_id', true), '')::INTEGER);

COMMIT;
