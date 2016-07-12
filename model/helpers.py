from werkzeug.security import generate_password_hash, check_password_hash

def get_hashed_password(plain_text_password):
    return generate_password_hash(plain_text_password)

def check_password(plain_text_password, hashed_password):
    return check_password_hash(hashed_password, plain_text_password)

def valid_email(email):
    approved_addresses = ["brianyu28@gmail.com"]
    approved_extensions = ["@pleasantonusd.net"]
    if email in approved_addresses:
        return True
    else:
        for extension in approved_extensions:
            if extension in email:
                return True
    return False