import os
import sys
sys.path.append('../')

from config import SIZE, FORMAT, FILE_BLOCK_SIZE

def show_my_teams(client):
    client.send(f"SHOW_MY_TEAMS\r\n".encode(FORMAT))

def upload_file(client, path, team_name, des_path):
    filename = os.path.basename(path)
    file_size = os.path.getsize(path)
    client.send(f"UPLOAD\n{filename}\n{team_name}\n{des_path}\n{file_size}\r\n".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    if response == "3001" or response == "2101" or response == "2042":
        return

    with open(path, "rb") as f:
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)
            if not chunk:
                break
            client.send(chunk)

def download_file(client, team_name, src_path, des_path):
    client.send(f"DOWNLOAD\n{team_name}\n{src_path}\r\n".encode(FORMAT))
    file_path = os.path.join(des_path, os.path.basename(src_path))

    response = client.recv(SIZE).decode(FORMAT)
    if response == '2042' or response == '2101' or response == '2201':
        return

    if os.path.exists(file_path):
        file_name = os.path.basename(src_path)
        new_file_name = file_name.split('.')[0] + '(1).' + file_name.split('.')[1]
        file_path = os.path.join(des_path, new_file_name)

    file_size = int(client.recv(SIZE).decode(FORMAT))
    with open(file_path, "wb") as f:
        while file_size > 0:
            chunk = client.recv(FILE_BLOCK_SIZE)
            f.write(chunk)
            file_size -= len(chunk)

def show_team_member(client, team_name):
    client.send(f"GET_MEMBER\n{team_name}\r\n".encode(FORMAT))


def create_directory(client, team_name, dir_path, dir_name):
    client.send(f"CREATE_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\r\n".encode(FORMAT))


def rename_directory(client, team_name, dir_path, dir_name, dir_new_name):
    client.send(f"RENAME_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\n{dir_new_name}\r\n".encode(FORMAT))


def delete_directory(client, team_name, dir_path, dir_name):
    client.send(f"DELETE_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\r\n".encode(FORMAT))


def copy_directory(client, team_name, src_path, dir_name, des_path):
    client.send(f"COPY_FOLDER\n{team_name}\n{src_path}\n{dir_name}\n{des_path}\r\n".encode(FORMAT))


def move_directory(client, team_name, src_path, dir_name, des_path):
    client.send(f"MOVE_FOLDER\n{team_name}\n{src_path}\n{dir_name}\n{des_path}\r\n".encode(FORMAT))