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

GRANT SELECT, INSERT, UPDATE ON public.users TO chathub_service;
GRANT ALL ON public.users TO developer;

CREATE TABLE public.images
(
    id INT8 PRIMARY KEY,
    owner INT8 NOT NULL,
    s3_bucket varchar(64) NOT NULL,
    s3_path VARCHAR(1024) NOT NULL,
    url varchar(1024),
    upload_dttm TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

GRANT SELECT, INSERT, UPDATE ON public.images TO chathub_service;
GRANT ALL ON public.images TO developer;

-- migrate:down
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.images;
