import bcrypt
import re

class AuthUtils:
    '''
        Authentication related utility functions (email, password, etc.)
    '''

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format using regex
        """
        
        email.strip().lower()
        if len(email) > 254:
            return False
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
