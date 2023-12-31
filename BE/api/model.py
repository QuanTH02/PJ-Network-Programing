from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class Account(db.Model):
    __tablename__ = 'Account'

    account = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Account(account='{self.account}', name='{self.name}')"
    

class Team(db.Model):
    __tablename__ = 'Team'

    team_name = db.Column(db.String(100), primary_key=True) # Khóa chính
    leader = db.Column(db.String(50), db.ForeignKey('Account.account'), nullable=False) # Khóa ngoại
    team_code = db.Column(db.String(50), nullable=True)

    # Khởi tạo quan hệ
    account = db.relationship('Account', backref=db.backref('teams', lazy=True))

    def __repr__(self):
        return f"Team(team_name='{self.team_name}', leader='{self.leader}', team_code='{self.team_code}')"
    
class Team_member(db.Model):
    __tablename__ = 'Team_member'

    account = db.Column(db.String(50), db.ForeignKey('Account.account'), primary_key=True, nullable=False) # Khóa ngoại
    team_name = db.Column(db.String(100), db.ForeignKey('Team.team_name'), primary_key=True, nullable=False) # Khóa ngoại

    # Khởi tạo quan hệ
    member = db.relationship('Account', backref=db.backref('teams_membership', lazy=True))
    team = db.relationship('Team', backref=db.backref('members', lazy=True))

    def __repr__(self):
        return f"Team_member(account='{self.account}', team_name='{self.team_name}')"
    
class Upload_file(db.Model):
    __tablename__ = 'Upload_file'

    file_path = db.Column(db.String(255), primary_key=True, nullable=False) # Khóa chính
    upload_Account = db.Column(db.String(50), db.ForeignKey('Account.account'), nullable=False) # Khóa ngoại
    time_upload = db.Column(db.DateTime, nullable=False)

    # Khởi tạo quan hệ
    Account = db.relationship('Account', backref=db.backref('uploaded_files', lazy=True))

    def __repr__(self):
        return f"Upload_file(file_path='{self.file_path}', time_upload='{self.time_upload}')"
    
class Join_request(db.Model):
    __tablename__ = 'Join_request'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # Khóa chính
    sender = db.Column(db.String(50), db.ForeignKey('Account.account'), nullable=False) # Khóa ngoại
    team_name = db.Column(db.String(100), db.ForeignKey('Team.team_name'), nullable=False) # Khóa ngoại

    # Khởi tạo quan hệ
    Account = db.relationship('Account', backref=db.backref('sent_requests', lazy=True))
    team = db.relationship('Team', backref=db.backref('join_requests', lazy=True))

    def __repr__(self):
        return f"Join_request(request_id={self.request_id}, sender='{self.sender}', team_name='{self.team_name}')"
    
class Session(db.Model):
    __tablename__ = 'Session'

    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # Khóa chính
    account = db.Column(db.String(50), db.ForeignKey('Account.account'), nullable=False) # Khóa ngoại
    token = db.Column(db.String(255), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Khởi tạo quan hệ
    Account = db.relationship('Account', backref=db.backref('sessions', lazy=True))

    def __repr__(self):
        return f"Session(session_id={self.session_id}, account='{self.account}', token='{self.token}', create_at='{self.create_at}', expires_at='{self.expires_at}', ip_address='{self.ip_address}', is_active={self.is_active})"


class Invite_request(db.Model):
    __tablename__ = 'Invite_request'
  
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # Khóa chính
    receiver = db.Column(db.String(50), db.ForeignKey('Account.account'), nullable=False) # Khóa ngoại
    team_name = db.Column(db.String(100), db.ForeignKey('Team.team_name'), nullable=False) # Khóa ngoại

    # Khởi tạo quan hệ
    Account = db.relationship('Account', backref=db.backref('received_invites', lazy=True))
    team = db.relationship('Team', backref=db.backref('invites', lazy=True))

    def __repr__(self):
        return f"Invite_request(request_id={self.request_id}, receiver='{self.receiver}', team_name='{self.team_name}')"
