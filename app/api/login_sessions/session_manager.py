class LoginSessionManager:
    """
    This class manages user login session based on session tokens and their matching user ID's
    """

    sessions: dict[str, int] = {}

    @staticmethod
    def add_session(token: str, user_id: int):
        """
        Adds a new login session with the token as key and the corresponding user ID as value.

        Params:
        token: the session token to save as the key
        user_id: the user ID to save as the value
        """
        LoginSessionManager.sessions[token] = user_id

    @staticmethod
    def remove_session(token: str) -> int | None:
        """
        Removes a login session based on the token.

        Params:
        token: the token to remove the session for.

        Returns:
        the corresponding user ID on success, or None on failure.
        """
        return LoginSessionManager.sessions.pop(token, None)

    @staticmethod
    def get_session(token: str) -> int | None:
        """
        Gets a user ID based on the session token.

        Params:
        token: the session token to get the corresponding user ID for

        Returns:
        the corresponding user ID on success, or None on failure
        """
        return LoginSessionManager.sessions.get(token, None)
