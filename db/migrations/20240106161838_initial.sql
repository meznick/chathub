-- migrate:up
create table public.users
(
    username varchar(16) primary key,
    password_hash varchar(128) not null,
    avatar_link varchar(256),
    bio varchar(512),
    sex varchar(1),
    name varchar(16),
    rating real default 0.0
);

grant select, insert, update on public.users to chathub_service;
grant all on public.users to developer;


-- migrate:down
drop table if exists public.users;
