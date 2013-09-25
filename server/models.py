from google.appengine.ext import ndb
from datetime import datetime, timedelta, time
from flask import current_app as app


class Server(ndb.Model):
    server_name = ndb.StringProperty()
    ip_address = ndb.StringProperty()
    subnet_mask = ndb.StringProperty()
    gateway = ndb.StringProperty()
    dns1 = ndb.StringProperty()
    dns2 = ndb.StringProperty()
    user_limit = ndb.IntegerProperty(default=None)
    expire_date = ndb.DateTimeProperty()
    cisco_ip_address = ndb.StringProperty()
    cisco_subnet_mask = ndb.StringProperty()
    cisco_gateway = ndb.StringProperty()
    cisco_ip_range = ndb.TextProperty()
    blocked = ndb.BooleanProperty()
    token = ndb.StringProperty()
    radius_response = ndb.PickleProperty()
    cisco_response = ndb.PickleProperty()

    def is_expired(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        return self.expire_date < ub_now

    def is_expires_today(self):
        ub_now = datetime.now() + timedelta(hours=app.config['TIMEZONE'])
        ub_today = ub_now.date()
        last_min = time(23, 59)
        return self.expire_date <= datetime.combine(ub_today, last_min)

    def login_infos(self):
        return LoginInfo.query().filter(LoginInfo.server==self.key)


class LoginInfo(ndb.Model):
    url = ndb.StringProperty()
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    server = ndb.KeyProperty(Server)
    title = ndb.StringProperty()

    SSH = 'ssh'
    HTTP = 'http'

    PROTOCOL_CHOICES = [
            SSH,
            HTTP]

    protocol = ndb.StringProperty(choices=PROTOCOL_CHOICES)
