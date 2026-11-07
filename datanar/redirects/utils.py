__all__ = ("generate_short_link",)

import secrets
import string

from redirects.models import Redirect

ALPHABET = string.ascii_letters + string.digits
MIN_LENGTH = 5
ATTEMPTS_PER_LENGTH = 20
MAX_GENERATION_ATTEMPTS = 200


def generate_short_link() -> str:
    for attempt in range(MAX_GENERATION_ATTEMPTS):
        length = MIN_LENGTH + attempt // ATTEMPTS_PER_LENGTH
        short_link = "".join(secrets.choice(ALPHABET) for _ in range(length))
        if not Redirect.objects.filter(short_link=short_link).exists():
            return short_link
    msg = "Error generating short link"
    raise RuntimeError(msg)
