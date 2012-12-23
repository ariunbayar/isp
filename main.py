from flask import Flask, render_template
from google.appengine.api import users
from server import server_blueprint
from account import account_blueprint
from server.models import Server
from decorator import check_login


app = Flask(__name__)
app.config.from_object('settings')
app.register_blueprint(server_blueprint)
app.register_blueprint(account_blueprint)

@app.route('/')
@check_login
def index(account):
    return render_template('index.html', account=account)


@app.errorhandler(403)
def forbidden(e):
    url = users.create_login_url('/')
    user = users.get_current_user()
    email = user.email() if user else ''
    return render_template('403.html', login_url=url, email=email)


@app.context_processor
def inject_servers():
    context = {}
    context['servers'] = Server.all()
    context['logout_url'] = users.create_logout_url("/")
    #template_values['is_admin'] = (account.role == "admin")
    return context
