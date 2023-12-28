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


def main():
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        return
    IP = socket.gethostbyname(socket.gethostname())
    PORT = sys.argv[1]
    ADDR = (IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print(f"{data}")

    while True:
        data = input("> ")
        if len(data) == 0:
            break
        data = data.split(",")
        cmd = data[0]

        if cmd == "CREATE_TEAM":
            create_team(client, data[1], data[2])
        elif cmd == "DELETE_FILE":
            delete_file(client, data[1])
        else:
            print("Unknown command.")

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
