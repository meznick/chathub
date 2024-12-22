-- migrate:up
INSERT INTO event_states
VALUES
(5, 'SKIPPED');

-- migrate:down
DELETE FROM public.event_states
WHERE id = 5;
