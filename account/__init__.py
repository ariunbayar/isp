from account.models import Account
from flask import Blueprint, render_template, request, flash
from decorator import admin_check


account_blueprint = Blueprint('account', __name__, template_folder='templates')

@account_blueprint.route('/account/add', methods=['GET', 'POST'])
@admin_check
def add(account):
    if request.method == 'POST':
        account = Account()
        account.email = request.form['email']
        account.role = request.form['role']
        account.put()
        flash(u'Account added!')
        return render_template('account/accounts.html', account=account, accounts=Account.all())
    else:
        return render_template('account/account_add.html', account=account)


@account_blueprint.route('/account/delete')
@admin_check
def delete(account):
    encoded_key = request.args['account']
    account = Account.get(encoded_key)
    account.delete()
    flash(u'Account deleted!')

    return render_template('account/accounts.html', account=account, accounts=Account.all())


@account_blueprint.route('/account/list')
@admin_check
def list(account):
    return render_template('account/accounts.html', account=account, accounts=Account.all())
