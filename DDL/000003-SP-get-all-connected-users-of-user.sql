/**
retrieve all connected users of user.

:param: in_user_id: user, for whom all connected users are retrieved.
:return: to_user_id: list of connected users.
*/

CREATE OR REPLACE FUNCTION get_all_connected_users_of_user (
  in_user_id bigint
)
RETURNS TABLE (
  to_user_id bigint
) AS
$body$
BEGIN

  RETURN QUERY
    SELECT    to_user_id
    FROM      Connected_Users
    WHERE     user_id = in_user_id;
  
END;
$body$
LANGUAGE 'plpgsql'