-- migrate:up
CREATE TABLE public.likes
(
    source_user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL
);

GRANT INSERT, SELECT, DELETE ON public.likes TO developer, chathub_service;

CREATE VIEW public.matches AS
SELECT t1.source_user_id AS user_1_id, t2.source_user_id AS user_2_id, t1.event_id AS event_id
FROM public.likes AS t1
INNER JOIN public.likes AS t2
    ON t1.target_user_id = t2.source_user_id
    AND t1.source_user_id = t2.target_user_id
    AND t1.event_id = t2.event_id;

GRANT INSERT, SELECT, DELETE ON public.matches TO developer, chathub_service;

-- migrate:down
DROP VIEW public.matches;
DROP TABLE public.likes;
