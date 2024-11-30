-- migrate:up
ALTER TABLE public.users
ADD COLUMN manual_score INT2 DEFAULT 2;

-- migrate:down
ALTER TABLE public.users
DROP COLUMN IF EXISTS manual_score;
