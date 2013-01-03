from forms import ServerForm, LoginInfoForm
from server.models import Server, LoginInfo
from account.models import Account
from google.appengine.ext import ndb, db
from google.appengine.api import mail
from google.appengine.api.app_identity import get_application_id
from flask import request, redirect, url_for, \
    render_template, Blueprint, abort, flash, make_response, current_app as app
from helpers import get_server, get_login_info
from decorator import check_login
import datetime

from old_models import Server as OldServer, Account as OldAccount

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
            return redirect(url_for('server.show',
                                     server_key=server.key.urlsafe()))
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
    if server_key is not None:
        ndb.Key(urlsafe=server_key).delete()
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
            return redirect(url_for('server.show',
                server_key=server.key.urlsafe()))
    else:
        form = ServerForm(**server._to_dict())
       
    return render_template('/server/form.html', form=form,
                server_key=server.key.urlsafe(), account=account)


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
def update_login_info(account, server_key):
    if request.method == 'POST':
        form = LoginInfoForm(request.form)
        if form.validate():
            if not server_key:
                return abort(404)

            login_info = LoginInfo()
            form.populate_obj(login_info)
            login_info.server = ndb.Key(urlsafe=server_key)
            login_info.put()
            flash(u'Login info updated!')
            return redirect(url_for('server.show', server_key=server_key))
    else:
        form = LoginInfoForm()

    ctx = dict(form=form, account=account, server_key=server_key)

    return render_template('server/login_info_form.html', **ctx)


@server_blueprint.route('/login_info/<login_info_key>/delete')
@check_login
def delete_login_info(account, login_info_key):
    login_info = get_login_info(login_info_key)
    import logging
    logging.error(login_info)
    server_key = login_info.server.urlsafe()
    if login_info is not None:
        ndb.Key(urlsafe=login_info_key).delete()
        flash(u'Login info deleted!')

    return redirect(url_for('server.show', server_key=server_key))


@server_blueprint.route('/tasks/migrate')
def migrate():
    old_servers = OldServer().all()
    old_accounts = OldAccount().all()

    for old_server in old_servers:
        server = Server(**db.to_dict(old_server))
        server.put()

    for old_account in old_accounts:
        account = Account(**db.to_dict(old_account))
        account.put()

    return redirect(url_for('index'))
