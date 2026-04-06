import bcrypt

password = b"password123"
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
print(hashed.decode())