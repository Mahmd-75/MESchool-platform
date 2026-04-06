from functools import wraps
from flask import session, abort, redirect, url_for
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                logger.warning(
                    f"Accès refusé — user_id={session.get('user_id')} "
                    f"role={session.get('role')} tentative sur route réservée à {roles}"
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator