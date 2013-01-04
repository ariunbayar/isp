from forms import ServerForm, LoginInfoForm
from server.models import Server, LoginInfo
from account.models import Account
from google.appengine.ext import ndb
from google.appengine.api import mail, urlfetch
from google.appengine.api.app_identity import get_application_id
from flask import request, redirect, url_for, \
    render_template, Blueprint, abort, flash, make_response, current_app as app
from helpers import get_server, get_login_info
from decorator import check_login
import datetime
import time
import urllib


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


def fetch_server_url(url, retry_count):
    while retry_count:
        result = urlfetch.fetch(url=url, deadline=10)

        if result.status_code == 200:
            break
        else:
            time.sleep(5)
            retry_count -= 1

    return result


@server_blueprint.route('/tasks/check-expire-date')
def check_server_expire_date():
    ub_now = datetime.datetime.now() + datetime.timedelta(hours=app.config['TIMEZONE'])
    ub_today = ub_now.date()
    last_min = datetime.time(23, 59)
    sender = 'no-reply@' + get_application_id() + '.appspotmail.com'
    site_url = 'http://' + get_application_id() + '.appspot.com'
    tomorrow = datetime.datetime.combine(ub_today, last_min)
    servers = Server.query().filter(Server.expire_date<=tomorrow)
    accounts = Account.query()
    for server in servers:
        for account in accounts:
            message = mail.EmailMessage(sender=sender, to=account.email)
            message.subject = "Server expire notification: %s" % server.server_name
            show_url = url_for('server.show', server_key=server.key.urlsafe())
            message_body = "Server %s is expired at %s\n %s%s" \
                           % (server.server_name, server.expire_date,
                              site_url, show_url)

            if server.blocked:
                url = 'http://%s/manager/expired/%s'\
                % (server.ip_address, server.token)
                result = fetch_server_url(url=url, retry_count=3)
                if result.status_code == 200:
                    if result.content == 'TRUE':
                        message_body += '\n Server %s is blocked upon expiry, %s'\
                                        % (server.server_name, server.expire_date)
                    else:
                        message_body += '\n %s' % result.content
                else:
                    message_body += '\n Unable to reach %s to block upon expiry, %s'\
                                    % (server.server_name, server.expire_date)

            message.body = message_body
            message.send()

    return make_response('')


@server_blueprint.route('/tasks/check-user-limit')
def check_server_user_limit():
    sender = 'no-reply@' + get_application_id() + '.appspotmail.com'
    site_url = 'http://' + get_application_id() + '.appspot.com'
    servers = Server.query()
    accounts = Account.query()
    for server in servers:
        if server.user_limit:
            for account in accounts:
                message = mail.EmailMessage(sender=sender, to=account.email)
                message_body = ''
                show_url = url_for('server.show', server_key=server.key.urlsafe())
                url = 'http://%s/manager/user_count/%s'\
                      % (server.ip_address, server.token)
                result = fetch_server_url(url=url, retry_count=3)
                if result.status_code == 200:
                    user_count = result.content

                    if user_count > server.user_limit:
                        message.subject = "Server expire notification: %s" % server.server_name
                        message_body += "User limit reached on %s." \
                                        "User limit: %s, Current users: %s\n %s%s" \
                                        % (server.server_name, server.user_limit,
                                           user_count, site_url, show_url)

                        if server.blocked:
                            url = 'http://%s/manager/add_user_blocked/%s'\
                                  % (server.ip_address, server.token)
                            result = fetch_server_url(url=url, retry_count=3)

                            user_blocked = result.content
                            if user_blocked == 'TRUE':
                                message_body += "Server %s add user is restricted to %s" \
                                                % (server.server_name, server.user_limit)
                            else:
                                message_body += '\n %s' % user_blocked
                else:
                    message_body += 'Unable to reach %s to retrieve user count \
                                    upon user limit check' % server.server_name

                message.body = message_body
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
