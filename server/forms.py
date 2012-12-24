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
    cisco_ip_address = TextField(u'Cisco IP address', validators=[validators.required(), validators.IPAddress()])
    cisco_subnet_mask = TextField(u'Cisco Subnet mask', validators=[validators.required(), validators.IPAddress()])
    cisco_gateway = TextField(u'Cisco Gateway', validators=[validators.required(), validators.IPAddress()])
    cisco_ip_range = TextField(u'Cisco IP range', validators=[validators.required(), validators.IPAddress()])


class LoginInfoForm(Form):
    url = TextField(u'URL', validators=[validators.required()])
    username = TextField(u'User name', validators=[validators.required()])
    password = TextField(u'Password', validators=[validators.required()])
