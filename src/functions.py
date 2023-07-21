import base64
import secrets

def generate_base64_random_hash(length=3):
    random_string = secrets.token_urlsafe(length)
    base64_hash = base64.urlsafe_b64encode(random_string.encode()).rstrip(b'=').decode()
    return base64_hash

if __name__ =="__main__":
    print(generate_base64_random_hash())