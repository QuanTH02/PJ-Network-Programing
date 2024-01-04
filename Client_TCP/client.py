import random
import socket
import os
import string
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
FILE_BLOCK_SIZE = 131072

def display_login_menu():
    print("1. Login")
    print("2. Signup")
    print("3. Exit")
    choice = input("Choose an option (1/2/3): ")
    return choice

def display_main_menu():
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
    choice = input("Choose an option (1-12): ")
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
    if response == "2281":
        return

    print("To open")
    with open(path, "rb") as f:
        print("Uploading file...")
        # text = f.read()
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)
            if not chunk:
                break
            client.send(chunk)

    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def download_file(client, path):
    filename = os.path.basename(path)
    client.send(f"DOWNLOAD\n{filename}\r\n".encode(FORMAT))

    with open(filename.rsplit('/', 1)[0], "wb") as f:
        while True:
            chunk = client.recv(SIZE)
            if not chunk:
                break
            f.write(chunk)


def make_directory(client, dir_name):
    client.send(f"MKDIR\n{dir_name}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def show_team_member(client, team_name):
    print("Show team member")
    client.send(f"GET_MEMBER\n{team_name}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def create_directory(client, dir_path, dir_name, username):
    client.send(f"CREATE_FOLDER\n{dir_path}\n{dir_name}\n{username}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def rename_directory(client, dir_path, dir_name):
    client.send(f"RENAME_FOLDER\n{dir_path}\n{dir_name}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def delete_directory(client, dir_path):
    client.send(f"DELETE_FOLDER\n{dir_path}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def copy_directory(client, dir_path, des_path):
    client.send(f"COPY_FOLDER\n{dir_path}\n{des_path}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def move_directory(client, dir_path, des_path):
    client.send(f"MOVE_FOLDER\n{dir_path}\n{des_path}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)


####################################################################
####################################################################
####################################################################

def login(client, username, password):
# def login(client):
#     username = input("Enter username: ")
#     password = input("Enter password: ")
    client.send(f"LOGIN\n{username}\n{password}\r\n".encode(FORMAT))

    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

    requests = client.recv(SIZE).decode(FORMAT)
    responses = [request for request in requests.split('\r\n') if request]

    for response in responses:
        print(response)

        if response.startswith("1030"):
            print("Login successful!")
            return {"username": username}
        else:
            print("Login failed. Please try again.")
            return None
    
def signup(client):
    username = input("Enter username: ")
    password = input("Enter password: ")
    name = input("Enter your name: ")
    client.send(f"SIGNUP\n{username}\n{password}\n{name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")
    # if response.startswith("1010"):
    #     print("Signup successful!")
    # else:
    #     print("Signup failed. Please try again.")

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
###################################################################
def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print("Client: ", client)
    print(f"{data}")

    active_session = None 
    app.run(debug=True)
    while True:
        if active_session is None:
            choice = display_login_menu()
            if choice == "1":
                active_session = login(client)
            elif choice == "2":
                signup(client)
            elif choice == "3":
                # client.send("LOGOUT".encode(FORMAT))
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            choice = display_main_menu()

            if choice == "1":
                show_my_teams(client, active_session["username"])
            elif choice == "2":
                path = input("Enter file path: ")
                des_path = input("Enter file destination path: ")
                upload_file(client, path, des_path)
            elif choice == "3":
                dir_name = input("Enter directory name: ")
                make_directory(client, dir_name)
            elif choice == "4":
                team_name = input("Enter team name: ")
                show_team_member(client, team_name)
            elif choice == "5":
                path = input("Enter file path: ")
                dir_name = input("Enter directory name: ")
                create_directory(client, path, dir_name, active_session["username"])
            elif choice == "6":
                path = input("Enter file path: ")
                dir_name = input("Enter directory name: ")
                rename_directory(client, path, dir_name)
            elif choice == "7":
                path = input("Enter file path: ")
                delete_directory(client, path)
            elif choice == "8":
                path = input("Enter file path: ")
                des_path = input("Enter file destination path: ")
                copy_directory(client, path, des_path)
            elif choice == "9":
                path = input("Enter file path: ")
                des_path = input("Enter file destination path: ")
                move_directory(client, path, des_path)
            elif choice == "10":
                client.send("LOGOUT".encode(FORMAT))
                active_session = None
            elif choice == "11":
                team_code = input("Enter team code: ")
                join_team(client, team_code, active_session["username"])
            elif choice == "12":
                team_name = input("Enter team name: ")
                create_team(client, team_name, active_session["username"])
            else:
                print("Invalid choice. Please try again.")

            # client.settimeout(2.0)

            responseFromServer(client)

            

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    # app.run(debug=True)
    main()

