-- migrate:up
CREATE TABLE public.reports
(
    source_user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL
);

GRANT INSERT, SELECT, DELETE ON public.reports TO developer, service_datemaker;

-- migrate:down
DROP TABLE public.reports;
