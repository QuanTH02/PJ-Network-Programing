import bcrypt
from flask import Blueprint, Flask, jsonify, request
from model import Account, db, Team, Team_member, Upload_file, Join_request, Session, Invite_request 
from flask_cors import CORS
import datetime
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
import pytz


SECRET_KEY = "network"
local_tz = pytz.timezone('Asia/Ho_Chi_Minh')

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
        token_payload = {
            'account': user_data.account,
            'expires_at': str(datetime.datetime.now(local_tz) + datetime.timedelta(hours=1)),  # Token hết hạn sau 1 giờ
            'is_active': True
        }
        print("Payload: ", token_payload)
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        print("\n\nToken", token)

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
    # Lấy token từ header Authorization
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401

    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Kiểm tra trạng thái đăng nhập
        if not payload.get('is_active'):
            return jsonify({'error': 'User is not active'}), 401

        # Lấy danh sách người dùng
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

    except (InvalidTokenError, ExpiredSignatureError):
        return jsonify({'error': 'Invalid or expired token'}), 401

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
    # Lấy token từ header Authorization
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401

    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(payload)
        # Kiểm tra account từ token có khớp với account truyền vào không
        if payload['account'] == account:
            # Kiểm tra trạng thái đăng nhập
            if payload['is_active']:
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
                    return jsonify({'error': 'No teams found'}), 404
            else:
                return jsonify({'error': 'User is not active'}), 401
        else:
            return jsonify({'error': 'Token does not match the account'}), 401
    except InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401

# Chưa sửa
@user.route('/api/get_list_folder/<account>', methods=['GET'])
def get_list_folder():
    # Lấy token từ header Authorization
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401

    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Kiểm tra trạng thái đăng nhập
        if not payload.get('is_active'):
            return jsonify({'error': 'User is not active'}), 401

        # Lấy danh sách người dùng
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

    except (InvalidTokenError, ExpiredSignatureError):
        return jsonify({'error': 'Invalid or expired token'}), 401



app.register_blueprint(user)

if __name__ == '__main__':       
    app.run(debug=True, port=5000)
