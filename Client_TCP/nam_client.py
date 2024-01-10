import sys
sys.path.append('../')

from config import FORMAT

def create_team(client, team_name):
    client.send(f"CREATE_TEAM\n{team_name}\r\n".encode(FORMAT))

def join_team(client, team_code):
    client.send(f"JOIN_TEAM\n{team_code}\r\n".encode(FORMAT))
    
def get_join_request(client, team_name):
    client.send(f"GET_JOIN_REQUEST\n{team_name}\r\n".encode(FORMAT))

def accept_join_request(client, team_name, sender):
    client.send(f"ACCEPT_JOIN_REQUEST\n{team_name}\n{sender}\r\n".encode(FORMAT))

def decline_join_request(client, team_name, sender):
    client.send(f"DECLINE_JOIN_REQUEST\n{team_name}\n{sender}\r\n".encode(FORMAT))

def delete_file(client, team_name, dir_path, filename):
    client.send(f"DELETE_FILE\n{team_name}\n{dir_path}\n{filename}\r\n".encode(FORMAT))

def rename_file(client, team_name, dir_path, old_file_name, new_file_name):
    client.send(f"RENAME_FILE\n{team_name}\n{dir_path}\n{old_file_name}\n{new_file_name}\r\n".encode(FORMAT))

def copy_file(client, team_name, src_dir, filename, dest_dir):
    client.send(f"COPY_FILE\n{team_name}\n{src_dir}\n{filename}\n{dest_dir}\r\n".encode(FORMAT))
    
def move_file(client, team_name, src_dir, filename, dest_dir):
    client.send(f"MOVE_FILE\n{team_name}\n{src_dir}\n{filename}\n{dest_dir}\r\n".encode(FORMAT))