-- migrate:up
CREATE TABLE public.users
(
    id INT8 PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    password_hash VARCHAR(128),
    bio VARCHAR(512),
    birthday DATE,
    sex VARCHAR(1),
    name VARCHAR(16),
    city VARCHAR(32),
    rating REAL DEFAULT 0.0
);

GRANT SELECT, INSERT, UPDATE ON public.users TO service_bot;
GRANT SELECT ON public.users TO service_datemaker;
GRANT ALL ON public.users TO developer;

CREATE TABLE public.images
(
    id BIGSERIAL PRIMARY KEY,
    owner INT8 NOT NULL,
    s3_bucket varchar(64) NOT NULL,
    s3_path VARCHAR(1024) NOT NULL,
    url varchar(1024),
    upload_dttm TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

GRANT SELECT, INSERT, UPDATE ON public.images TO service_bot;
GRANT SELECT ON public.images TO service_datemaker;
GRANT ALL ON public.images TO developer;
GRANT USAGE, UPDATE ON SEQUENCE images_id_seq TO service_bot, developer;

-- migrate:down
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.images CASCADE;
