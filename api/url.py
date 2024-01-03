from flask import Blueprint
from .view import login, get_all_user, get_list_team, get_user

user = Blueprint('user', __name__)

@user.route('/api/login', methods=['POST'])
def route_login():
    return login()

@user.route('/api/get_all_user', methods=['GET'])
def route_get_all_user():
    return get_all_user()

@user.route('/api/get_user/<account>', methods=['GET'])
def route_get_user(account):
    return get_user(account)

@user.route('/api/get_list_team/<account>', methods=['GET'])
def rout_get_list_team(account):
    return get_list_team(account)