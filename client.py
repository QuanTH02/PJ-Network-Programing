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
    print("2. List Files")
    print("3. Quit Team")
    print("4. Remove Member")
    print("5. List Invitations")
    print("6. Create Team")
    print("7. Invite Member")
    print("8. Change password")
    print("9. Logout")
    choice = input("Choose an option (1-8): ")
    return choice


def login(client):
    account = input("Enter username: ")
    password = input("Enter password: ")
    client.send(f"LOGIN\n{account}\n{password}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")

    if response.startswith("1030"):
        print("Login successful!")
        return {"username": account}
    elif response.startswith("2011"):
        print("Missing information!")
        return None
    elif response.startswith("2032"):
        print("Incorrect password!")
        return None
    else:
        print("Account doesn't exist!")
        return None


def signup(client):
    username = input("Enter username: ")
    password = input("Enter password: ")
    name = input("Enter your name: ")
    client.send(f"SIGNUP\n{username}\n{password}\n{name}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")
    if response.startswith("1010"):
        print("Signup successful!")
    else:
        print("Signup failed. Please try again.")


def show_my_teams(client, username):
    client.send(f"SHOW_MY_TEAMS\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def list_files(client, path):
    client.send(f"LIST\n{path}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def upload_file(client, path):
    with open(path, "r") as f:
        text = f.read()

    filename = os.path.basename(path)
    client.send(f"UPLOAD\n{filename}\n{text}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def make_directory(client, dir_name):
    client.send(f"MKDIR\n{dir_name}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def delete_file(client, file_path):
    client.send(f"DELETE\n{file_path}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def create_team(client, team_name, username):
    client.send(f"CREATE_TEAM\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def quit_team(client, team_name, username):
    client.send(f"QUIT\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def remove_member(client, team_name, username):
    client.send(f"REMOVE_MEMBER\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def get_all_user(client):
    client.send("GET_ALL_USER".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def invite_member(client, team_name, username):
    client.send(f"INVITE_MEMBER\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def get_all_invitations(client, username):
    client.send(f"GET_ALL_INVITATIONS\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    return response

def accept_invitation(client, team_name, username):
    client.send(f"ACCEPT_INVITATION\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def decline_invitation(client, team_name, username):
    client.send(f"DECLINE_INVITATION\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)

def change_password(client, username, password, new_password, cf_password):
    client.send(f"CHANGE_PASSWORD\n{username}\n{password}\n{new_password}\n{cf_password}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)

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
                path = input("Enter directory path: ")
                list_files(client, path)
            elif choice == "3":
                team_name = input("Enter team name: ")
                quit_team(client, team_name, active_session["username"])
            elif choice == "4":
                team_name = input("Enter team name: ")
                member_name = input("Enter member name: ")
                remove_member(client, team_name, member_name)
            elif choice == "5":
                get_all_invitations(client, active_session["username"])
                response = get_all_invitations(client, active_session["username"])
                print(response)
                if "No pending invitations." not in response:
                    team_name = input("Enter team name: ")
                    selection = input("Accept or decline: ")
                    if selection == "accept":
                        accept_invitation(client, team_name, active_session["username"])
                    elif selection == "decline":
                        decline_invitation(client, team_name, active_session["username"])
            elif choice == "6":
                team_name = input("Enter team name: ")
                create_team(client, team_name, active_session["username"])
            elif choice == "7":
                get_all_user(client)
                team_name = input("Enter team name: ")
                username = input("Enter username: ")
                invite_member(client, team_name, username)
            elif choice == "8":
                password = input("Enter current password: ")
                new_password = input("Enter new password: ")
                cf_password = input("Confirm new password: ")
                change_password(client, active_session["username"], password, new_password, cf_password)
            elif choice == "9":
                client.send("LOGOUT".encode(FORMAT))
                break
            else:
                print("Invalid choice. Please try again.")

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
