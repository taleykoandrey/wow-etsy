/**
add new connected user.

:param: in_user_id: user for whom to_user_id would be connected,
:param: to_user_id: user who would be connected to user_id.
:return: void.
*/


CREATE OR REPLACE FUNCTION add_connected_user (
  in_user_id bigint,
  in_to_user_id bigint
)
RETURNS record AS
$body$
BEGIN

  INSERT INTO Connected_users(user_id, to_user_id)
  SELECT      in_user_id, 
              in_to_user_id;
END;
$body$
LANGUAGE 'plpgsql'