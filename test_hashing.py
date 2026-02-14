from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    hash = pwd_context.hash("testpassword")
    print(f"Hash successful: {hash}")
    assert pwd_context.verify("testpassword", hash)
    print("Verification successful")
except Exception as e:
    print(f"Error: {e}")
    exit(1)
