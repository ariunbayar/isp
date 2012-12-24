from google.appengine.ext import db
from datetime import datetime, timedelta, time
from flask import current_app as app


class Server(db.Model):
    server_name = db.StringProperty()
    ip_address = db.StringProperty()
    subnet_mask = db.StringProperty()
    gateway = db.StringProperty()
    dns1 = db.StringProperty()
    dns2 = db.StringProperty()
    user_limit = db.IntegerProperty(default=None)
    expire_date = db.DateTimeProperty()
    cisco_ip_address = db.StringProperty()
    cisco_subnet_mask = db.StringProperty()
    cisco_gateway = db.StringProperty()
    cisco_ip_range = db.TextProperty()

    def is_expired(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        return self.expire_date < ub_now

    def is_expires_today(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        ub_today = ub_now.date()
        last_min = time(23, 59)
        return self.expire_date <= datetime.combine(ub_today, last_min)


class LoginInfo(db.Model):
    url = db.StringProperty()
    username = db.StringProperty()
    password = db.StringProperty()
    server = db.ReferenceProperty(Server, collection_name='login_infos')
