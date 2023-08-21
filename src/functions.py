import base64
import secrets
import string
import logging

logging.basicConfig(
    level=logging.INFO
)

def generate_base64_random_hash(length=3):
    random_string = secrets.token_urlsafe(length)
    base64_hash = base64.urlsafe_b64encode(random_string.encode()).rstrip(b'=').decode()
    return base64_hash

    return base64_hash

def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:\t%(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
    return logger

if __name__ =="__main__":
    print(generate_base64_random_hash())