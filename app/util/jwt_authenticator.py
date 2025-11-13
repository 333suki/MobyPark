from datetime import datetime, timedelta, timezone

import jwt

SECRET = "verysecretkey"
ALGORITHM = "HS256"


class TokenError(Exception):
    pass

class TokenExpiredError(TokenError):
    pass

class TokenInvalidError(TokenError):
    pass

class TokenMissingError(TokenError):
    pass


class JWTAuthenticator:
    @staticmethod
    def generate_token(user_id: int, user_role: str):
        payload = {
            "sub": str(user_id),
            "role": user_role,
            "exp": datetime.now(timezone.utc) + timedelta(hours = 1)
        }
        return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    @staticmethod
    def validate_token(token: str | None) -> dict:
        """
        Validates a token

        Params:
        token: The JWT token to check

        Returns:
        A dictionary with the keys "sub", which is the users ID, and "role", which is the users role.

        Raises:
        A TokenError when something about the token is wrong, expired or invalid.
        """
        if not token:
            raise TokenMissingError("No token provided")
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        try:
            payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            sub: int = int(payload.get("sub"))
            role: str = payload.get("role")
            if not sub:
                raise TokenInvalidError("Missing field \"sub\" in token")
            if not role:
                raise TokenInvalidError("Missing field \"role\" in token")
            return { "sub": sub, "role": role }
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expired")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(str(e))
