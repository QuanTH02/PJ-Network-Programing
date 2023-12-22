import os
import socket
import threading
import sqlite3
import re
import random
import string
import bcrypt
import shutil

IP = "0.0.0.0"
PORT = 5000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

DB_CONNECTIONS = {}
DB_CONNECTIONS_LOCK = threading.Lock()
ACTIVE_SESSIONS = {}
ACTIVE_SESSIONS_LOCK = threading.Lock()


def random_team_code(cursor):
    characters = string.ascii_letters + string.digits
    code = "".join(random.choice(characters) for _ in range(6))
    cursor.execute("Select team_code from team")
    result = cursor.fetchall()
    while code in result:
        characters = string.ascii_letters + string.digits
        code = "".join(random.choice(characters) for _ in range(6))
    return code


def get_account_id(username, cursor):
    cursor.execute("SELECT account_id FROM Account WHERE account=?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


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
    full_new_path = f"{file_directory}/{new_file_name}"

    if not new_file_name:
        send_data = "2202"  # Invalid new file name
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
    account_id = get_account_id(account, cursor)

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
                "INSERT INTO team (leader_id, team_name, team_code) VALUES (?, ?, ?)",
                (account_id, team_name, team_code),
            )
            dbconn.commit()

    conn.send(send_data.encode(FORMAT))


def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        if len(data) == 0:
            break
        data = data.split("\n")
        cmd = data[0]
        if cmd == "DELETE":
            delete_file(conn, data, cursor, dbconn)
        elif cmd == "CREATE_TEAM":
            create_team(conn, data, cursor, dbconn)
        else:
            conn.send("3000".encode(FORMAT))

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
