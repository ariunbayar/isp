from google.appengine.api import users
from account.models import Account
from flask import abort
from functools import wraps


def check_login(fn):
    @wraps(fn)
    def check(*args, **kwargs):
        user = users.get_current_user()
        if user:
            email = user.email()
            account = Account.query().filter(Account.email==email.lower()).get()
            if isinstance(account, Account):
                kwargs.update({'account': account})
                return fn(*args, **kwargs)

        return abort(403)
    return check


def admin_check(fn):
    @check_login
    @wraps(fn)
    def check(*args, **kwargs):
        account = kwargs['account']
        if account.role == 'admin':
            return fn(*args, **kwargs)
        
        return abort(403)
    return check

