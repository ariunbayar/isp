from account.models import Account
from google.appengine.ext import ndb


def get_account(email):
    account = Account.query().filter(Account.email==email).get()
    return account
 
def get_server(encoded_key):
    try:
        server = ndb.Key(urlsafe=encoded_key).get()
        return server
    except Exception:
        return None

def get_login_info(encoded_key):
    try:
        login_info = ndb.Key(urlsafe=encoded_key).get()
        return login_info
    except Exception:
        return None
