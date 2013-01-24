import datetime
import time

from account.models import Account
from server import server_blueprint
from server.models import Server

from flask import make_response, current_app as app, url_for
from google.appengine.api import mail, urlfetch
from google.appengine.api.app_identity import get_application_id


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
