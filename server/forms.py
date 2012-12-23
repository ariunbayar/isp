from wtforms import Form, TextField, validators, DateTimeField, IntegerField


class ServerForm(Form):
    server_name = TextField(u'Server name', validators=[validators.required()])
    ip_address = TextField(u'IP address', validators=[validators.required(), validators.IPAddress()])
    subnet_mask = TextField(u'Subnet mask', validators=[validators.required(), validators.IPAddress(message='Invalid Subnet mask')])
    gateway = TextField(u'Gateway', validators=[validators.required(), validators.IPAddress(message='Invalid Gateway')])
    dns1 = TextField(u'DNS1', validators=[validators.optional(), validators.IPAddress(message='Invalid DNS1')])
    dns2 = TextField(u'DNS2', validators=[validators.optional(), validators.IPAddress(message='Invalid DNS1')])
    expire_date = DateTimeField(u'Expire date', format='%Y-%m-%d %H:%M')
    user_limit = IntegerField(u'User limit', validators=[validators.optional()])
