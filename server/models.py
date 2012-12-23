from google.appengine.ext import db


class Server(db.Model):
    server_name = db.StringProperty()
    ip_address = db.StringProperty()
    subnet_mask = db.StringProperty()
    gateway = db.StringProperty()
    dns1 = db.StringProperty()
    dns2 = db.StringProperty()
    user_limit = db.IntegerProperty(default=None)
    expire_date = db.DateTimeProperty()
