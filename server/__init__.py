from forms import ServerForm
from server.models import Server
from google.appengine.ext import db
from flask import request, redirect, url_for, \
    render_template, Blueprint, abort, flash
from helpers import get_server
from decorator import check_login


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
        return

    return render_template('server/show.html', account=account,
            server=server)


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
