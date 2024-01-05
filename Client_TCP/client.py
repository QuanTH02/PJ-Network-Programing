import random
import socket
import os
import string
import sys
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
FILE_BLOCK_SIZE = 131072
CLIENT_DATA_PATH = "client_data"

def display_login_menu():
    print("****************************************")
    print("1. Login")
    print("2. Signup")
    print("3. Exit")
    choice = input("Choose an option (1/2/3): ")
    print("****************************************")
    return choice

def display_main_menu():
    print("****************************************")
    print("1. Show My Teams")
    print("2. Upload File")
    print("3. Make Directory")
    print("4. Show Team Members")
    print("5. Create Directory")
    print("6. Rename Directory")
    print("7. Delete Directory")
    print("8. Copy Directory")
    print("9. Move Directory")
    print("10. Logout")
    print("11. Join Team")
    print("12. Create Team")
    print("13. Download File")
    choice = input("Choose an option (1-13): ")
    print("****************************************")
    return choice

def responseFromServer(client):
    print("Go to responseFromServer")
    requests = client.recv(SIZE).decode(FORMAT)

    # Sửa
    responses = [request for request in requests.split('\r\n') if request]

    for response in responses:
        # Đăng ký và quản lý tài khoản
        if response.startswith("1010"):
            print("Đăng ký thành công")
        if response.startswith("2011"):
            print("Chưa nhập đủ các trường thông tin")
        if response.startswith("2012"):
            print("Trường thông tin nhập chưa đúng định dạng")
        if response.startswith("2013"):
            print("Tài khoản đã tồn tại")
        if response.startswith("1020"):
            print("Đổi mật khẩu thành công")
        if response.startswith("2021"):
            print("2 mật khẩu trùng nhau")
        if response.startswith("2022"):
            print("Mật khẩu mới nhập lại không trùng khớp")
        if response.startswith("2023"):
            print("Mật khẩu mới không đúng định dạng")
        if response.startswith("2024"):
            print("Nhập mật khẩu cũ sai")

        
        # if response.startswith(""):
        #     print("")
        # if response.startswith(""):
        #     print("")
        # if response.startswith(""):
        #     print("")


        if response.startswith("1260"):
            print("Show my teams successfully")
        if response.startswith("1100"):
            print("Show team member successfully")
        if response.startswith("1190"):
            print("Upload file successfully")
        if response.startswith("2181"):
            print("File đã tồn tại ở thư mục đích")
        if response.startswith("1200"):
            print("Download file successfully")
        if response.startswith("1060"):
            print("Join team successfully")
        if response.startswith("2061"):
            print("Nhập sai Team code")
        if response.startswith("2062"):
            print("Đã tham gia nhóm rồi")
        if response.startswith("1040"):
            print("Create team successfully")
        if response.startswith("2041"):
            print("Tên nhóm đã tồn tại")

        print(response)
        return response


def show_my_teams(client, username):
    client.send(f"SHOW_MY_TEAMS\n{username}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # return response
    # responseFromServer(client)


def upload_file(client, path, des_path):
    filename = os.path.basename(path)
    file_size = os.path.getsize(path)
    client.send(f"UPLOAD\n{filename}\n{des_path}\n{file_size}\r\n".encode(FORMAT))
    print("To recv")
    response = client.recv(SIZE).decode(FORMAT)
    print("To respond")
    if response == "2181":
        return

    print("To open")
    with open(path, "rb") as f:
        print("Uploading file...")
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)
            if not chunk:
                break
            client.send(chunk)

    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def download_file(client, path):
    client.send(f"DOWNLOAD\n{path}\r\n".encode(FORMAT))
    file_path = os.path.join(CLIENT_DATA_PATH, os.path.basename(path))

    if os.path.exists(file_path):
        send_data = "2191"
        client.send(send_data.encode(FORMAT))
        return
    
    client.send("OK".encode(FORMAT))

    file_size = int(client.recv(SIZE).decode(FORMAT))
    with open(file_path, "wb") as f:
        while file_size > 0:
            chunk = client.recv(FILE_BLOCK_SIZE)
            f.write(chunk)
            file_size -= len(chunk)

def make_directory(client, dir_name):
    client.send(f"MKDIR\n{dir_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def show_team_member(client, team_name):
    print("Show team member")
    client.send(f"GET_MEMBER\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def create_directory(client, dir_path, dir_name, username):
    client.send(f"CREATE_FOLDER\n{dir_path}\n{dir_name}\n{username}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def rename_directory(client, dir_path, dir_name):
    client.send(f"RENAME_FOLDER\n{dir_path}\n{dir_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def delete_directory(client, dir_path):
    client.send(f"DELETE_FOLDER\n{dir_path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def copy_directory(client, dir_path, des_path):
    client.send(f"COPY_FOLDER\n{dir_path}\n{des_path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def move_directory(client, dir_path, des_path):
    client.send(f"MOVE_FOLDER\n{dir_path}\n{des_path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)


####################################################################
####################################################################
####################################################################

def login(client, username, password):
    client.send(f"LOGIN\n{username}\n{password}\r\n".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")
    data = response.split("\n")
    return data[0]
    
def signup(client, username, password, name):
    client.send(f"SIGNUP\n{username}\n{password}\n{name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def create_team(client, team_name, username):
    print("Create team")
    client.send(f"CREATE_TEAM\n{team_name}\n{username}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def join_team(client, team_code, account):
    print("To join team")
    client.send(f"JOIN_TEAM\n{team_code}\n{account}\r\n".encode(FORMAT))
    print("Send successful")
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def logout(client):
    client.send("LOGOUT\r\n")
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")
####################################################################
####################################################################
####################################################################


@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home/account=<account>')
def home_page(account):
    # list_team = ['Toan', 'Ly', 'Hoa']
    # code_team = ['aaa', 'bbb', 'ccc']
    print("Xin chao")
    show_my_teams(client, account)
    response = responseFromServer(client)
    list_response = response.split('\n')
    trimmed_response = list_response[1:]

    mid = len(trimmed_response) // 2

    list_team = trimmed_response[:mid]
    print("List Team:")
    print(list_team)

    code_team = trimmed_response[mid:]
    print("Code Team:")
    print(code_team)

    return render_template('home.html', account=account, list_team=list_team, code_team=code_team)

@app.route('/team/<code_team>', methods=['GET'])
def team_page(code_team):
    print(code_team)
    account = request.args.get('account')
    if account:
        print(account)
    return render_template('team.html', code_team=code_team)
################################################################### 
# @Controller
@app.route('/check-login', methods=['POST'])
def checkLogin():
    data = request.json
    account = data.get('account')
    password = data.get('password')

    if login(client, account, password):
        return jsonify({"message": "1030"})
    # if account == "nam123" and password == "Test1234":
    #     return jsonify({"message": "1030"})
    else:
        return jsonify({"message": "Invalid credentials"})
    
@app.route('/check-join-team', methods=['POST'])
def checkJoinTeam():
    data = request.json
    account = data.get('account')
    code = data.get('code')
    join_team(client, code, account)

    response = responseFromServer(client)
    if response == "1060":
        return jsonify({"message": "1060"})
    elif response == "2011":
        return jsonify({"message": "2011"})
    elif response == "2061":
        return jsonify({"message": "2061"})
    elif response == "2062":
        return jsonify({"message": "2062"})
    else:
        return jsonify({"message": "Invalid credentials"})
    
@app.route('/check-create-team', methods=['POST'])
def checkCreateTeam():
    data = request.json
    account = data.get('account')
    team_name = data.get('team_name')
    create_team(client, team_name, account)
    response = responseFromServer(client)
    print("Response: ", response)

    if response.startswith("1040"):
        string_res = response.split('\n')
        print("String res: ", string_res)
        code = string_res[1]
        print("Code", code)
        return jsonify({"message": "1040", "code_team": code})
    elif response == "2011":
        return jsonify({"message": "2011"})
    elif response == "2041":
        return jsonify({"message": "2041"})
    else:
        return jsonify({"message": "Invalid credentials"})
####################################################################
####################################################################
####################################################################
    

def main():
    global client
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        return
    IP = socket.gethostbyname(socket.gethostname())
    PORT = int(sys.argv[1])
    ADDR = (IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print(f"{data}")
    session_key = None
    account = None

    # app.run(debug=True)

    while True:
        if session_key is None:
            print("You must login first if you have a account, or register if hadn't")
        data = input("> ")
        if len(data) == 0:
            break
        
        client.send(session_key.encode(FORMAT))
        response = client.recv(SIZE).decode(FORMAT)
        print(response)
        if response == "2311" and session_key:
            session_key = None
            account = None
            continue

        data = data.split(",")
        cmd = data[0]

        if cmd == "LOGIN":
            session_key = login(client, data[1], data[2])
            account = session_key.rsplit(":")[0]
        elif cmd == "SIGNUP":
            signup(client, data[1], data[2], data[3])
        elif cmd == "LOGOUT":
            session_key = None
            account = None
            logout(client)
        elif cmd == "SHOW_MY_TEAMS":
            show_my_teams(client, account)
        elif cmd == "UPLOAD":
            upload_file(client, data[1], data[2])
        elif cmd == "MKDIR":
            make_directory(client, data[1])
        elif cmd == "GET_MEMBER":
            show_team_member(client, data[1])
        elif cmd == "CREATE_FOLDER":
            create_directory(client, data[1], data[2], account)
        elif cmd == "RENAME_FOLDER":
            rename_directory(client, data[1], data[2], account)
        elif cmd == "DELETE_FOLDER":
            delete_directory(client, data[1], account)
        elif cmd == "COPY_FOLDER":
            copy_directory(client, data[1], data[2])
        elif cmd == "MOVE_FOLDER":
            move_directory(client, data[1], data[2])
        elif cmd == "DOWNLOAD":
            download_file(client, data[1])
        elif cmd == "JOIN_TEAM":
            join_team(client, data[1], account)
        elif cmd == "CREATE_TEAM":
            create_team(client, data[1], account)
        elif cmd == "DOWNLOAD":
            download_file(client, data[1])
        else:
            print("Unknown command.")

        responseFromServer(client)

            

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    # app.run(debug=True)
    main()

