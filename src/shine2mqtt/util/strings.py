import string
from random import choices


def generate_random_lowercase_string(length: int) -> str:
    return "".join(choices(string.ascii_lowercase, k=length))


def generate_random_uppercase_string(length: int) -> str:
    return "".join(choices(string.ascii_uppercase, k=length))
