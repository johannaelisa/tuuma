from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 16:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 8:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
