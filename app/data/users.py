import uuid
import bcrypt
import string
import random


class User:

    def __init__(self, user_id: uuid.UUID, user_role: str, password: str, email: str, enabled: bool = True,
                 confirmed: bool = True, account_non_expired: bool = True, account_non_locked: bool = True,
                 credentials_non_expired: bool = True):
        self.id = user_id
        self.user_role = user_role
        self.password = password
        self.email = email
        self.enabled = enabled
        self.confirmed = confirmed
        self.account_non_expired = account_non_expired
        self.account_non_locked = account_non_locked
        self.credentials_non_expired = credentials_non_expired

    def __str__(self):
        def _trunc(val: str, length: int):
            return val[0: length] + "..."
        return f"id: {_trunc(str(self.id), 12)}, role: {self.user_role}, password: {_trunc(self.password, 16)}, " \
               f"email: {self.email}, enabled: {self.enabled}, confirmed: {self.confirmed}, " \
               f"acct_expired: {self.account_non_expired}, acct_locked: {self.account_non_locked}, " \
               f"cred_expired: {self.credentials_non_expired}"

    class Role:
        ADMIN = 'ROLE_ADMIN'
        DRIVER = 'ROLE_DRIVER'
        EMPLOYEE = 'ROLE_EMPLOYEE'
        CUSTOMER = 'ROLE_CUSTOMER'


class UserGenerator:
    @classmethod
    def generate_password(cls, password_len: int) -> str:
        """
        Generate a random password.
        :param password_len: the length of the password
        :return: the generated password
        """
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        numbers = string.digits
        symbols = string.punctuation
        all_chars = lower + upper + numbers + symbols
        password = "".join(random.sample(all_chars, password_len))

        def _salt_and_hash(_password: str):
            return bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt(rounds=10, prefix=b"2a"))

        return _salt_and_hash(password).decode('utf-8')

    @classmethod
    def generate_email(cls, min_len=4, max_len=20) -> str:
        """
        Generate a random email.
        :param min_len: the minimum length of the email
        :param max_len: the maximum length of the email
        :return: the generated email
        """
        extensions = ['com', 'net', 'org', 'gov']
        domains = ['gmail', 'yahoo', 'comcast', 'verizon', 'smoothstack', 'hotmail']
        win_ext = extensions[random.randint(0, len(extensions) - 1)]
        win_dom = domains[random.randint(0, len(domains) - 1)]
        acc_len = random.randint(min_len, max_len)
        win_acc = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(acc_len))
        finale = win_acc + "@" + win_dom + "." + win_ext
        return finale

    @classmethod
    def generate_user(cls, role) -> User:
        """
        Generate a random User.
        :param role: the role of the user
        :return: the generated User
        """
        password = cls.generate_password(password_len=12)
        email = cls.generate_email(min_len=4, max_len=12)
        user_id = uuid.uuid4()
        user = User(user_id=user_id, user_role=role, password=password, email=email)
        return user
