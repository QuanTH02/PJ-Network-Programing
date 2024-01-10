import sys
sys.path.append('../')

from config import FORMAT

def login(client, username, password):
    client.send(f"LOGIN\n{username}\n{password}\r\n".encode(FORMAT))
    
def signup(client, username, password, name):
    client.send(f"SIGNUP\n{username}\n{password}\n{name}\r\n".encode(FORMAT))

def change_password(client, password, new_password, cf_password):
    client.send(f"CHANGE_PASSWORD\n{password}\n{new_password}\n{cf_password}\r\n".encode(FORMAT))

def logout(client):
    client.send(f"LOGOUT\r\n".encode(FORMAT))

def quit_team(client, team_name):
    client.send(f"QUIT_TEAM\n{team_name}\r\n".encode(FORMAT))

def remove_member(client, team_name, member_name):
    client.send(f"REMOVE_MEMBER\n{team_name}\n{member_name}\r\n".encode(FORMAT))

def get_all_user(client):
    client.send(f"GET_ALL_USER\r\n".encode(FORMAT))

def invite_member(client, team_name, member_name):
    client.send(f"INVITE_MEMBER\n{team_name}\n{member_name}\r\n".encode(FORMAT))

def get_all_invitations(client):
    client.send(f"GET_ALL_INVITATIONS\r\n".encode(FORMAT))

def accept_invitation(client, team_name):
    client.send(f"ACCEPT_INVITATION\n{team_name}\r\n".encode(FORMAT))

def decline_invitation(client, team_name):
    client.send(f"DECLINE_INVITATION\n{team_name}\r\n".encode(FORMAT))

def dir_information(client, team_name, path):
    client.send(f"FOLDER_INFORMATION\n{team_name}\n{path}\r\n".encode(FORMAT))