-- migrate:up
ALTER TABLE dating_registrations
ADD COLUMN is_ready BOOL default FALSE;

-- migrate:down
ALTER TABLE dating_registrations
DROP COLUMN is_ready;
