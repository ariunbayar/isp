from server.models import Server, LoginInfo
from account.models import Account
from google.appengine.ext.db import BadKeyError


def get_account(email):
    account = Account().all().filter("email =", email).get()
    return account
 
def get_server(encoded_key):
    try:
        server = Server.get(encoded_key)
        return server
    except BadKeyError:
        return None

def get_login_info(encoded_key):
    try:
        login_info = LoginInfo.get(encoded_key)
        return login_info
    except BadKeyError:
        return None
