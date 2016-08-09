from werkzeug.security import generate_password_hash, check_password_hash

# get a password hash
def hash_password(password):
    return generate_password_hash(password)

# check password hashes
def check_password(password, password_hash ):
    return check_password_hash(password, password_hash)
