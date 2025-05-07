-- Script to create a new dating event starting in 10 minutes and register 40 random users for it

-- Insert a new dating event with start time 10 minutes from now and capture its ID
WITH new_event AS (
    INSERT INTO public.dating_events (start_dttm, users_limit, state_id)
    VALUES (NOW() + INTERVAL '10 minutes', 40, 0)
    RETURNING id
)
-- Register 40 random users for the event
INSERT INTO public.dating_registrations (user_id, event_id, registered_on_dttm, confirmed_on_dttm, is_ready, confirmation_event_sent)
SELECT u.id, e.id, NOW(), NOW(), TRUE, TRUE
FROM (
    SELECT id FROM public.users ORDER BY RANDOM() LIMIT 20
) u
CROSS JOIN new_event e;
