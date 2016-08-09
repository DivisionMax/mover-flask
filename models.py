class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(120), unique=True)
    # passwords must be hashed and salted
    def __init__(self, password, email):
        # hashed and salted passwords
        self.password_hash = hash_password(password)
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email