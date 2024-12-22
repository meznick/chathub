-- migrate:up
ALTER TABLE public.likes
ADD COLUMN action_time TIMESTAMP DEFAULT NOW();

ALTER TABLE public.reports
ADD COLUMN action_time TIMESTAMP DEFAULT NOW();

ALTER TABLE public.dislikes
ADD COLUMN action_time TIMESTAMP DEFAULT NOW();


-- migrate:down
ALTER TABLE public.likes
DROP COLUMN action_time;

ALTER TABLE public.reports
DROP COLUMN action_time;

ALTER TABLE public.dislikes
DROP COLUMN action_time;
