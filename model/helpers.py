import bcrypt

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt(8))

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)

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