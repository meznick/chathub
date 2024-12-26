-- migrate:up
ALTER TABLE dating_registrations
ADD COLUMN confirmation_event_sent BOOL DEFAULT FALSE;

-- migrate:down
ALTER TABLE dating_registrations
DROP COLUMN IF EXISTS confirmation_event_sent;
