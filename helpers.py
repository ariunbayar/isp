import datetime

from account.models import Account

from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from flask import current_app as app


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


def current_datetime():
    """ Current time with timezone applied """
    timeoffset = datetime.timedelta(hours=app.config['TIMEZONE'])
    return datetime.datetime.now() + timeoffset


def run_task_at(url, run_at, **params):
    timeoffset = datetime.timedelta(hours=app.config['TIMEZONE'])
    taskqueue.add(eta= run_at - timeoffset, url=url, params=params)
