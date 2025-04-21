-- migrate:up
CREATE TABLE public.dislikes
(
    source_user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL
);

GRANT INSERT, SELECT, DELETE ON public.dislikes TO developer, service_datemaker;

CREATE VIEW public.mismatches AS
SELECT t1.source_user_id AS user_1_id, t2.source_user_id AS user_2_id, t1.event_id AS event_id
FROM public.dislikes AS t1
INNER JOIN public.dislikes AS t2
    ON t1.target_user_id = t2.source_user_id
    AND t1.source_user_id = t2.target_user_id
    AND t1.event_id = t2.event_id;

GRANT INSERT, SELECT, DELETE ON public.mismatches TO developer, service_datemaker;

-- migrate:down
DROP VIEW public.mismatches;
DROP TABLE public.dislikes;
