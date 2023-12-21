import os
import socket
import threading
import sqlite3
import re
import random
import string
import bcrypt

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

DB_CONNECTIONS = {}
DB_CONNECTIONS_LOCK = threading.Lock()
ACTIVE_SESSIONS = {}
ACTIVE_SESSIONS_LOCK = threading.Lock()


def get_database_connection():
    thread_id = threading.current_thread().ident
    with DB_CONNECTIONS_LOCK:
        if thread_id not in DB_CONNECTIONS:
            DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        else:
            try:
                # Try a simple query to check if the connection is still alive
                DB_CONNECTIONS[thread_id].execute("SELECT 1").fetchone()
            except sqlite3.ProgrammingError:
                # Reconnect if the connection is closed
                DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        return DB_CONNECTIONS[thread_id]


def close_connection(dbconn):
    dbconn.close()


def upload_file(conn, data):
    name, text = data[1], data[2]
    filepath = os.path.join(SERVER_DATA_PATH, name)
    with open(filepath, "w") as f:
        f.write(text)

    send_data = "1180"
    conn.send(send_data.encode(FORMAT))


def make_directory(conn, data):
    dir_path = data[1]
    full_path = os.path.join(SERVER_DATA_PATH, dir_path)

    try:
        os.makedirs(full_path)
        send_data = "1240"
    except FileExistsError:
        send_data = "2242"

    conn.send(send_data.encode(FORMAT))


def create_directory(conn, data):
    dir_path = data[1]
    dir_name = data[2]
    full_path = os.path.join(SERVER_DATA_PATH, dir_path)
    full_path = os.path.join(full_path, dir_name)

    try:
        os.makedirs(full_path)
        send_data = "1240"
    except FileExistsError:
        send_data = "2242"

    conn.send(send_data.encode(FORMAT))

def rename_directory(conn, data):
    dir_path = data[1]
    dir_name = data[2]
    full_path_old = os.path.join(SERVER_DATA_PATH, dir_path)
    full_path_new = os.path.join(SERVER_DATA_PATH, dir_path.rsplit('/', 1)[0], dir_name)

    try:
        os.rename(full_path_old, full_path_new)
        send_data = "1250"
    except FileExistsError:
        send_data = "2241"

    conn.send(send_data.encode(FORMAT))

def delete_directory(conn, data):
    dir_path = data[1]

    full_path = os.path.join(SERVER_DATA_PATH, dir_path)
    os.rmdir(full_path)
    send_data = "1260"

    conn.send(send_data.encode(FORMAT))

def copy_directory(conn, data):
    dir_path = data[1]
    des_path = data[2]
    dir_name = dir_path.rsplit('/', 1)[-1]

    full_dir_path = os.path.join(SERVER_DATA_PATH, dir_path)

    full_des_path = os.path.join(SERVER_DATA_PATH, des_path)
    full_des_path = os.path.join(full_des_path, dir_name)

    try:
        os.makedirs(full_des_path)
        send_data = "1270"
    except FileExistsError:
        send_data = "2271"

    conn.send(send_data.encode(FORMAT))

def move_directory(conn, data):
    dir_path = data[1]
    des_path = data[2]
    dir_name = dir_path.rsplit('/', 1)[-1]

    full_dir_path = os.path.join(SERVER_DATA_PATH, dir_path)

    full_des_path = os.path.join(SERVER_DATA_PATH, des_path)
    full_des_path = os.path.join(full_des_path, dir_name)

    try:
        os.makedirs(full_des_path)
        os.rmdir(full_dir_path)
        send_data = "1280"
    except FileExistsError:
        send_data = "2271"

    conn.send(send_data.encode(FORMAT))


def show_my_teams(conn, data, cursor):
    username = data[1]

    if username is not None:
        cursor.execute(
            "SELECT team_name FROM team_member WHERE account = ?",
            (username, ),
        )
        result = cursor.fetchall()
        if result:
            teams = [row[0] for row in result]
            send_data = "1260\n" + "\n".join(teams)
        else:
            send_data = "1261\nYou are not a member of any team."
    else:
        send_data = "2011"

    conn.send(send_data.encode(FORMAT))

def show_team_member(conn, data, cursor):
    team_name = data[1]
    send_data = "1100\n"

    cursor.execute(
        "SELECT account FROM team_member WHERE team_name = ?",
        (team_name, ),
    )

    result = cursor.fetchall()

    for account in result:
        send_data += "\n".join(account)

    conn.send(send_data.encode(FORMAT))


def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    active_session = None

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("\n")
        cmd = data[0]

        if active_session is not None:
            account_id = active_session["account_id"]
            username = active_session["username"]
            if cmd == "UPLOAD":
                upload_file(conn, data)
            elif cmd == "MKDIR":
                make_directory(conn, data)
            elif cmd == "SHOW_MY_TEAMS":
                show_my_teams(conn, data, cursor)
            elif cmd == "GET_MEMBER":
                show_team_member(conn, data, cursor)
            elif cmd == "CREATE_FOLDER":
                create_directory(conn, data)
            elif cmd == "RENAME_FOLDER":
                rename_directory(conn, data)
            elif cmd == "DELETE_FOLDER":
                delete_directory(conn, data)
            elif cmd == "COPY_FOLDER":
                copy_directory(conn, data)
            elif cmd == "MOVE_FOLDER":
                move_directory(conn, data)
            else:
                conn.send("4040".encode(FORMAT))

        elif len(cmd) == 0:
            break

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()
    close_connection(dbconn)


def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    main()
