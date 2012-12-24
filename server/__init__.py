from forms import ServerForm, LoginInfoForm
from server.models import Server, LoginInfo
from account.models import Account
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api.app_identity import get_application_id
from flask import request, redirect, url_for, \
    render_template, Blueprint, abort, flash, make_response, current_app as app
from helpers import get_server
from decorator import check_login
import datetime


server_blueprint = Blueprint('server', __name__, template_folder='templates')

@server_blueprint.route('/server/add', methods=['GET', 'POST'])
@check_login
def add(account):
    if request.method == 'POST':
        form = ServerForm(request.form)
        if form.validate():
            server = Server()
            form.populate_obj(server)
            server.put()
            flash(u'Server added!')
            return redirect(url_for('server.show', server_key=server.key()))
    else:
        form = ServerForm()

    return render_template('server/form.html', form=form, account=account)


@server_blueprint.route('/server/<server_key>')
@check_login
def show(account, server_key):
    server = get_server(server_key)
    if server is None:
        return abort(404)

    return render_template('server/show.html', account=account, server=server)


@server_blueprint.route('/server/<server_key>/delete')
@check_login
def delete(account, server_key):
    server = get_server(server_key)
    if server is not None:
        server.delete()
        flash(u'Server deleted!')

    return redirect(url_for('index'))


@server_blueprint.route('/server/<server_key>/edit/', methods=['GET','POST'])
@check_login
def edit(account, server_key):
    server = get_server(server_key)
    if server is None:
        return abort(404)

    if request.method == 'POST':
        form = ServerForm(request.form)
        if form.validate():
            form.populate_obj(server)
            server.put()
            return redirect(url_for('server.show', server_key=server.key()))
    else:
        form = ServerForm(**db.to_dict(server))
       
    return render_template('/server/form.html', form=form,
                server=server.key(), account=account)


@server_blueprint.route('/tasks/expiry')
def expiry():
    ub_now = datetime.datetime.now() + datetime.timedelta(hours=app.config['TIMEZONE'])
    ub_today = ub_now.date()
    last_min = datetime.time(23, 59)
    sender = 'no-reply@' + get_application_id() + '.appspotmail.com'
    site_url = 'http://' + get_application_id() + '.appspot.com'
    tomorrow = datetime.datetime.combine(ub_today, last_min)
    servers = Server.all().filter("expire_date <=", tomorrow)
    accounts = Account.all()
    for server in servers:
        for account in accounts:
            message = mail.EmailMessage(sender=sender, to=account.email)
            message.subject = "Server expire notification: %s" % server.server_name
            message.body = "Server will expire at %s\n" \
                            "%s%s" % (server.expire_date, site_url,
                                    url_for('server.show', server_key=server.key()))
            message.send()

    return make_response('hello')


@server_blueprint.route('/server/<server_key>/update_login', methods=['GET','POST'])
@check_login
def update(account, server_key):
    if request.method == 'POST':
        form = LoginInfoForm(request.form)
        if form.validate():
            server = get_server(server_key)
            login_info = LoginInfo()
            form.populate_obj(login_info)
            login_info.server = server
            login_info.put()
            flash(u'Login info updated!')
            return redirect(url_for('server.show', server_key=server.key()))
    else:
        form = LoginInfoForm()

    return render_template('server/form.html', form=form, account=account)
