/**
All connected users.

user_id - user, who connected to_user_id,
to_user_id - user, who was connected by user_id,
received_date - date, when row was added.
*/

CREATE TABLE Connected_Users (
  user_id BIGINT NOT NULL,
  to_user_id BIGINT NOT NULL,
  received_date DATE DEFAULT now() NOT NULL,
  CONSTRAINT connected_users_pkey PRIMARY KEY(user_id, to_user_id)
) 
WITH (oids = false);