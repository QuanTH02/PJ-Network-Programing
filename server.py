import os
import socket
import threading
import sqlite3
import re
import random
import string
import shutil
import sys

from const import IP, SIZE, FORMAT, SERVER_DATA_PATH

DB_CONNECTIONS = {}
DB_CONNECTIONS_LOCK = threading.Lock()
ACTIVE_SESSIONS = {}
ACTIVE_SESSIONS_LOCK = threading.Lock()


def write_log(addr, request, response, cursor, dbconn):
    cursor.execute(
        "Insert into log(time, client_address,request,response) values(datetime('now'),?,?,?)",
        (addr, request, response),
    )
    dbconn.commit()


def random_team_code(cursor):
    characters = string.ascii_letters + string.digits
    code = "".join(random.choice(characters) for _ in range(6))
    cursor.execute("Select team_code from team")
    result = cursor.fetchall()
    while code in result:
        characters = string.ascii_letters + string.digits
        code = "".join(random.choice(characters) for _ in range(6))
    return code


def get_database_connection():
    thread_id = threading.current_thread().ident
    with DB_CONNECTIONS_LOCK:
        if thread_id not in DB_CONNECTIONS:
            DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        else:
            try:
                DB_CONNECTIONS[thread_id].execute("SELECT 1").fetchone()
            except sqlite3.ProgrammingError:
                DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        return DB_CONNECTIONS[thread_id]


def close_connection(dbconn):
    dbconn.close()


def delete_file(conn, data, cursor, dbconn):
    filename = data[1]
    path = f"{SERVER_DATA_PATH} / {filename}"
    os.remove(path)
    cursor.execute("Delete from upload_file where file_path = ?", (path,))
    dbconn.commit()

    send_data = "1210"
    conn.send(send_data.encode(FORMAT))


def rename_file(conn, data, cursor, dbconn):
    file_path = data[1]
    new_file_name = data[2]
    file_name = file_path.split("/")[-1]
    file_directory = "/".join(file_path.split("/")[:-1])

    if not new_file_name:
        send_data = "2202"
    elif "/" in new_file_name or "\\" in new_file_name:
        send_data = "2202"
    elif new_file_name.endswith("."):
        send_data = "2202"
    else:
        new_file_extension = new_file_name.split(".")[-1]
        old_file_extension = file_name.split(".")[-1]

        if new_file_extension.lower() != old_file_extension.lower():
            send_data = "2203"
        else:
            new_full_path = f"{file_directory}/{new_file_name}"

            try:
                os.rename(file_path, new_full_path)
                send_data = "1200"
                cursor.execute(
                    "Update Upload_file set file_path = ? where file_path = ?",
                    (file_path, new_full_path),
                )
                dbconn.commit()
            except FileNotFoundError:
                send_data = "2201"
            except FileExistsError:
                send_data = "2201"

    conn.send(send_data.encode(FORMAT))


def copy_file(conn, data, cursor, dbconn):
    source_path = data[1]
    destination_directory = data[2]
    account = data[3]
    source_file_name = source_path.split("/")[-1]
    destination_path = f"{destination_directory}/{source_file_name}"
    if os.path.exists(destination_path):
        send_data = "2181"
    else:
        try:
            shutil.copy2(source_path, destination_path)
            send_data = "1220"
            cursor.execute(
                "INSERT INTO upload_file (file_path, upload_user, time_upload) VALUES (?, ?, datetime('now'))",
                (destination_path, account),
            )
            dbconn.commit()
        except Exception as e:
            print(e)
            send_data = "2221"

    conn.send(send_data.encode(FORMAT))


def move_file(conn, data, cursor, dbconn):
    source_path = data[1]
    destination_directory = data[2]
    source_file_name = source_path.split("/")[-1]
    destination_path = f"{destination_directory}/{source_file_name}"

    if os.path.exists(destination_path):
        send_data = "2181"
    else:
        try:
            shutil.move(source_path, destination_path)
            cursor.execute(
                "UPDATE upload_file SET file_path = ?, time_upload = datetime('now') WHERE file_path = ?",
                (destination_path, source_path),
            )
            dbconn.commit()
            send_data = "1230"
        except Exception as e:
            print(e)
            send_data = "2207"

    conn.send(send_data.encode(FORMAT))


def create_team(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]

    if not team_name:
        send_data = "2011"
    else:
        cursor.execute("SELECT team_name FROM team WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()
        if result is not None:
            send_data = "2041"
        else:
            send_data = "1040"
            team_path = os.path.join(SERVER_DATA_PATH, team_name)
            os.makedirs(team_path)
            team_code = random_team_code(cursor)
            cursor.execute(
                "INSERT INTO team (leader, team_name, team_code) VALUES (?, ?, ?)",
                (account, team_name, team_code),
            )
            dbconn.commit()

    conn.send(send_data.encode(FORMAT))


def join_team(conn, data, cursor, dbconn):
    code = data[1]
    account = data[2]
    if code == None or account == None:
        send_data = "2011"
    else:
        cursor.execute(
            "SELECT team_code, team_name FROM team WHERE team_code = ?", (code,)
        )
        result = cursor.fetchone()

        if result[0] is None:
            send_data = "2061"
        else:
            team_name = result[1]
            cursor.execute(
                "SELECT account from team_member where team_name = ?", (team_name,)
            )
            team_account = cursor.fetchall()
            if account in team_account:
                send_data = "2062"
            else:
                send_data = "1060"
                cursor.execute(
                    "Insert into join_request (sender, team_name) values (?,?)",
                    (account, team_name),
                )
                dbconn.commit()
    conn.send(send_data.encode(FORMAT))


def get_request(conn, data, cursor):
    team_name = data[1]
    cursor.execute("SELECT sender from join_request where team_name = ?", (team_name,))
    results = cursor.fetchall()
    send_data = "1070"
    for result in results:
        send_data = send_data + "\n" + result[0]
    conn.send(send_data.encode(FORMAT))


def accept_request(conn, data, cursor, dbconn):
    team_name = data[1]
    account = data[2]
    send_data = "1080"
    cursor.execute("Insert into team_member values (?,?)", (account, team_name))
    dbconn.commit()
    cursor.execute(
        "Delete from join_request where team_name = ? and sender = ?",
        (team_name, account),
    )
    dbconn.commit()
    conn.send(send_data.encode(FORMAT))


def decline_request(conn, data, cursor, dbconn):
    team_name = data[1]
    account = data[2]
    send_data = "1090"
    cursor.execute(
        "Delete from join_request where team_name = ? and sender = ?",
        (team_name, account),
    )
    dbconn.commit()
    conn.send(send_data.encode(FORMAT))


def receive_file(conn, des_path):
    with open(des_path, "wb") as f:
        while True:
            chunk = conn.recv(SIZE)

            if not chunk:
                break
            f.write(chunk)


def send_file(conn, des_path):
    with open(des_path, "rb") as f:
        while True:
            chunk = conn.send(SIZE)

            if not chunk:
                break
            f.write(chunk)


def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE)
        if len(data) == 0:
            break
        data.decode(FORMAT)
        data = data.split("\n")
        cmd = data[0]
        if cmd == "DELETE_FILE":
            delete_file(conn, data, cursor, dbconn)
        elif cmd == "CREATE_TEAM":
            create_team(conn, data, cursor, dbconn)
        elif cmd == "MOVE_FILE":
            move_file(conn, data, cursor, dbconn)
        elif cmd == "COPY_FILE":
            copy_file(conn, data, cursor, dbconn)
        elif cmd == "RENAME_FILE":
            rename_file(conn, data, cursor, dbconn)

        elif cmd == "JOIN_TEAM":
            join_team(conn, data, cursor, dbconn)

        elif cmd == "GET_REQUEST":
            get_request(conn, data, cursor)
        elif cmd == "ACCEPT_REQUEST":
            accept_request(conn, data, cursor, dbconn)
        elif cmd == "DECLINE_REQUEST":
            decline_request(conn, data, cursor, dbconn)

        else:
            conn.send("3000".encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()
    close_connection(dbconn)


def main():
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        return

    PORT = int(sys.argv[1])
    ADDR = (IP, PORT)
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
