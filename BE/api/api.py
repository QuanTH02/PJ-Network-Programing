import bcrypt
from flask import Blueprint, Flask, jsonify, request
from model import Account, db, Team, Team_member, Upload_file, Join_request, Session, Invite_request 
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_share.db'
CORS(app)

db.init_app(app)
user = Blueprint('user', __name__)

@user.route('/api/login', methods=['POST'])
def login():
    data = request.json
    account = data.get('account')
    password = data.get('password')

    user_data = Account.query.filter_by(account=account).first()
    if user_data:
        # Kiểm tra mật khẩu
        if password == user_data.password:
            # Mật khẩu chính xác
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid password'}), 401
    else:
        return jsonify({'error': 'No user found'}), 404
    

@user.route('/api/get_all_user', methods=['GET'])
def get_all_user():
    user_data = Account.query.all()
    user_list = []
    for user in user_data:
        user_info = {
            'account': user.account,
            'data': {
                'password': str(user.password) if isinstance(user.password, bytes) else user.password,
                'name': user.name
            }
        }
        user_list.append(user_info)
    if user_list:
        return jsonify(user_list)
    else:
        return jsonify({'error': 'No users found'}), 404

@user.route('/api/get_user/<account>', methods=['GET'])
def get_user(account):
    user_data = Account.query.filter_by(account=account).first()
    if user_data:
        user_info = {
            'account': user_data.account,
            'data': {
                'password': str(user_data.password) if isinstance(user_data.password, bytes) else user_data.password,
                'name': user_data.name
            }
        }
        return jsonify(user_info)
    else:
        return jsonify({'error': 'No user found'}), 404

@user.route('/api/get_list_team/<account>', methods=['GET'])
def get_list_team(account):
    team_data = Team.query.filter_by(leader=account).all()
    team_list = []
    for team in team_data:
        team_info = {
            'team_name': team.team_name,
            'data': {
                'leader': team.leader,
                'team_code': team.team_code
            }
        }
        team_list.append(team_info)
    if team_list:
        return jsonify(team_list)
    else:
        return jsonify({'error': 'No users found'}), 404




app.register_blueprint(user)

if __name__ == '__main__':       
    app.run(debug=True, port=5000)
