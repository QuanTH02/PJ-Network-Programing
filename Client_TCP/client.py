import socket
import os
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)



IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

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
    choice = input("Choose an option (1-10): ")
    return choice

def responseFromServer(client):
    requests = client.recv(SIZE).decode(FORMAT)
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
        if response.startswith("1180"):
            print("Upload file successfully")



        print(response)


def show_my_teams(client, username):
    client.send(f"SHOW_MY_TEAMS\n{username}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)
    responseFromServer(client)

def upload_file(client, path, des_path):
    filename = os.path.basename(path)
    client.send(f"UPLOAD\n{filename}\n{des_path}\r\n".encode(FORMAT))

    with open(path, "rb") as f:
        # text = f.read()
        while True:
            chunk = f.read(SIZE)
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
    
def login(client):
    username = input("Enter username: ")
    password = input("Enter password: ")
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

####################################################################
####################################################################
####################################################################
    
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/home/account=<account>')
def home_page(account):
    return render_template('home.html', account=account)

@app.route('/team/<team_name>/<account_name>')
def team_page(account, team_name):
    return render_template('team.html', team_name=team_name, account=account)

@app.route('/check-login', methods=['POST'])
def checkLogin():
    data = request.json
    account = data.get('account')
    password = data.get('password')

    if account == "nam123" and password == "Test1234":
        return jsonify({"message": "1030"})
    else:
        return jsonify({"message": "Invalid credentials"})
        
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    
    print(f"{data}")

    active_session = None
    while True:
        if active_session is None:
            choice = display_login_menu()

            if choice == "1":
                active_session = login(client)
                
            elif choice == "2":
                signup(client)
            elif choice == "3":
                client.send("LOGOUT".encode(FORMAT))
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
                break
            else:
                print("Invalid choice. Please try again.")

            # client.settimeout(2.0)

            responseFromServer(client)

            

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    app.run(debug=True)
    main()
