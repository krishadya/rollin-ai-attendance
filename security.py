import hashlib
import hmac
import secrets

# PBKDF2 settings
ITERATIONS = 100_000
SALT_SIZE = 16


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256.

    Returns:
        pbkdf2_sha256$iterations$salt$hash
    """
    salt = secrets.token_hex(SALT_SIZE)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    ).hex()

    return f"pbkdf2_sha256${ITERATIONS}${salt}${password_hash}"


def is_password_hash(value: str) -> bool:
    """Check whether a stored password is already hashed."""
    return value.startswith("pbkdf2_sha256$")


def verify_password(password: str, stored_password: str) -> bool:
    """
    Verify a password against a stored PBKDF2 hash.
    """
    try:
        algorithm, iterations, salt, stored_hash = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()

        return hmac.compare_digest(calculated_hash, stored_hash)

    except (AttributeError, TypeError, ValueError):
        return False
