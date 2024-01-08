import socket
import os
import sys

from const import FORMAT, SIZE


def delete_file(client, file_path):
    client.send(f"DELETE\n{file_path}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def create_team(client, team_name, username):
    client.send(f"CREATE_TEAM\n{team_name}\n{username}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def move_file(client, src_path, dst_path):
    client.send(f"MOVE_FILE\n{src_path}\n{dst_path}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def copy_file(client, src_path, dst_path, account):
    client.send(f"COPY_FILE\n{src_path}\n{dst_path}\n{account}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def rename_file(client, file_path, new_name):
    client.send(f"RENAME\n{file_path}\n{new_name}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def join_team(client, team_code, account):
    client.send(f"JOIN_TEAM\n{team_code}\n{account}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def get_request(client, team_name):
    client.send(f"GET_REQUEST\n{team_name}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def accept_request(client, team_name, account):
    client.send(f"ACCEPT_REQUEST\n{team_name}\n{account}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def decline_request(client, team_name, account):
    client.send(f"DECLINE_REQUEST\n{team_name}\n{account}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


def login(client, username, password):
    client.send(f"LOGIN\n{username}\n{password}\r\n".encode(FORMAT))

    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")
    data = response.split("\n")
    return data[0]


def signup(client, username, password, name):
    client.send(f"SIGNUP\n{username}\n{password}\n{name}\r\n".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")


def logout(client):
    client.send("LOGOUT\r\n")
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")


def main():
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

        if cmd == "CREATE_TEAM":
            create_team(client, data[1], account)
        elif cmd == "DELETE_FILE":
            delete_file(client, data[1])
        elif cmd == "MOVE_FILE":
            move_file(client, data[1], data[2])
        elif cmd == "COPY_FILE":
            copy_file(client, data[1], data[2], account)
        elif cmd == "RENAME_FILE":
            rename_file(client, data[1], data[2])

        elif cmd == "JOIN_TEAM":
            join_team(client, data[1], account)

        elif cmd == "GET_REQUEST":
            get_request(client, data[1])
        elif cmd == "ACCEPT_REQUEST":
            accept_request(client, data[1], account)
        elif cmd == "DECLINE_REQUEST":
            decline_request(client, data[1], account)

        elif cmd == "LOGIN":
            session_key = login(client, data[1], data[2])
            account = session_key.rsplit(":")[0]
        elif cmd == "SIGNUP":
            signup(client, data[1], data[2], data[3])
        elif cmd == "LOGOUT":
            session_key = None
            account = None
            logout(client)
        else:
            print("Unknown command.")

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
