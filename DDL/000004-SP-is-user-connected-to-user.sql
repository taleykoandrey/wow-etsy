/**
check if to_user_id is connected to user_id.

:param: in_user_id: user for whom to_user_id would be connected,
:param: to_user_id: user who would be connected to user_id.
:return: true if to_user_id is connected to user_id, 
         false otherwise.
*/

CREATE OR REPLACE FUNCTION is_user_connected_to_user (
  in_user_id bigint,
  in_to_user_id bigint
)
RETURNS boolean AS
$body$
BEGIN
	IF EXISTS (SELECT    1
               FROM      Connected_Users
               WHERE     user_id = in_user_id
                 AND     to_user_id = in_to_user_id)
    THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
END;
$body$
LANGUAGE 'plpgsql'