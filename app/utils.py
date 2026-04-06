import re

def sanitize_string(value, max_length=100):
    if not value:
        return ""
    value = value.strip()
    return value[:max_length]

def validate_username(username):
    if not username or len(username) < 3:
        return False, "Nom d'utilisateur trop court (min 3 caractères)."
    if len(username) > 50:
        return False, "Nom d'utilisateur trop long (max 50 caractères)."
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Caractères invalides. Utilisez lettres, chiffres, _, . ou -"
    return True, ""

def validate_password(password):
    if not password or len(password) < 8:
        return False, "Mot de passe trop court (min 8 caractères)."
    if len(password) > 128:
        return False, "Mot de passe trop long."
    return True, ""

def validate_grade(grade):
    try:
        g = float(grade)
        if g < 0 or g > 20:
            return False, "La note doit être entre 0 et 20."
        return True, ""
    except (ValueError, TypeError):
        return False, "Note invalide."