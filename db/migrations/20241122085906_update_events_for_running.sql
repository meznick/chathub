-- migrate:up
CREATE TABLE event_states (
    id INT2,
    state_name VARCHAR(32)
);
GRANT SELECT ON event_states TO service_datemaker, developer;

INSERT INTO event_states
VALUES
(0, 'NOT_STARTED'),
(1, 'REG_CONFIRM'),
(2, 'READY'),
(3, 'RUNNING'),
(4, 'FINISHED');

ALTER TABLE dating_events
ADD COLUMN state_id INT2 NOT NULL DEFAULT 0;

-- migrate:down
DROP TABLE event_states;

ALTER TABLE dating_events
DROP COLUMN state_id;
