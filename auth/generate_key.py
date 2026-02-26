import secrets

def generate_secret_key():
    """Generate a secure random key (useful for future JWT integration)."""
    key = secrets.token_hex(32)
    print(f"Generated key: {key}")
    return key

if __name__ == "__main__":
    generate_secret_key()
