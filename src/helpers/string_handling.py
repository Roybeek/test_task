import random
import string

__all__ = (
    'create_random_string',
)


def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))
