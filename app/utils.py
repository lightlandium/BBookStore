import random

def generate_confirmation_code():
    return str(random.randint(100000, 999999))