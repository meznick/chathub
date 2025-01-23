-- migrate:up
alter table dating_events
alter column start_dttm
set data type timestamp with time zone;

-- migrate:down
alter table dating_events
alter column start_dttm
set data type timestamp without time zone;
