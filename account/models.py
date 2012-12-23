from google.appengine.ext import db


class Account(db.Model):
    email = db.StringProperty()
    role = db.StringProperty()

    def is_admin(self):
        return self.role == 'admin'
