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

    def is_expired(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        return self.expire_date < ub_now

    def is_expires_today(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        ub_today = ub_now.date()
        last_min = time(23, 59)
        return self.expire_date <= datetime.combine(ub_today, last_min)
