import socket
import os

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
        print(response)


def show_my_teams(client, username):
    client.send(f"SHOW_MY_TEAMS\n{username}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def upload_file(client, path):
    with open(path, "r") as f:
        text = f.read()

    filename = os.path.basename(path)
    client.send(f"UPLOAD\n{filename}\n{text}".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

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
                upload_file(client, path)
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


            client.settimeout(2.0)
            try:
                responseFromServer(client)
            except socket.timeout:
                print("Timeout occurred! Continue without receiving data.")
            

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
