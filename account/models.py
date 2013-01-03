from google.appengine.ext import ndb


class Account(ndb.Model):
    email = ndb.StringProperty()
    role = ndb.StringProperty()

    def is_admin(self):
        return self.role == 'admin'
