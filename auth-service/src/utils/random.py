import string
from secrets import choice as secrets_choice


def generate_random_string(len: int):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets_choice(alphabet) for _ in range(len))
