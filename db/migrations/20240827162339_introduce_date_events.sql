-- migrate:up
CREATE TABLE IF NOT EXISTS public.dating_events (
    id BIGSERIAL PRIMARY KEY,
    start_dttm TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    users_limit INT2 NOT NULL DEFAULT 20
);

GRANT SELECT, INSERT, UPDATE ON public.dating_events TO service_datemaker;
GRANT ALL ON public.dating_events TO developer;
GRANT USAGE, UPDATE ON SEQUENCE dating_events_id_seq TO service_datemaker, developer;

CREATE TABLE IF NOT EXISTS public.dating_registrations (
    user_id INT8,
    event_id INT8,
    registered_on_dttm TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    confirmed_on_dttm TIMESTAMP WITHOUT TIME ZONE
);

GRANT SELECT, INSERT, UPDATE ON public.dating_registrations TO service_datemaker;
GRANT ALL ON public.dating_registrations TO developer;

-- migrate:down
DROP TABLE IF EXISTS public.dating_events;
DROP TABLE IF EXISTS public.dating_registrations;
