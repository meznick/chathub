-- migrate:up
CREATE TABLE dating_event_groups (
    event_id INT2,
    group_no INT2,
    pair_no INT2,
    turn_no INT2, -- dating turn no when pair active
    user_1_id BIGINT,
    user_2_id BIGINT
);
GRANT SELECT, DELETE ON dating_event_groups TO chathub_service, developer;

-- migrate:down
DROP TABLE dating_event_groups;
