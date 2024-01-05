import hashlib
import os
import socket
import threading
import sqlite3
import random
import string
import shutil
from tqdm import tqdm
import sys
from datetime import datetime, timedelta

from const import (
    IP,
    SIZE,
    FORMAT,
    SERVER_DATA_PATH,
    FILE_BLOCK_SIZE,
    SESSION_TIMEOUT_MINUTES,
)

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
    rand_char = random.choice(string.ascii_letters)
    rand_code = "".join(random.choice(characters) for _ in range(5))
    code = rand_char + rand_code
    cursor.execute("Select team_code from team")
    result = cursor.fetchall()
    while code in result:
        code = random_team_code(cursor)
    return code


def create_session_id():
    hash_object = hashlib.sha256(os.urandom(64))
    session_id = hash_object.hexdigest()
    while session_id in ACTIVE_SESSIONS:
        session_id = create_session_id()
    return session_id


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


def receive_file(conn, data):
    file_path = data[1]
    file_size = data[2]
    bar = tqdm(
        range(file_size),
        f"Receiving {file_path}",
        unit="B",
        unit_scale=True,
        unit_divisor=SIZE,
    )
    with open(file_path, "wb") as f:
        while True:
            chunk = conn.recv(FILE_BLOCK_SIZE)

            if not chunk:
                break
            chunk = chunk
            f.write(chunk)
            bar.update(len(chunk))


def send_file(conn, src_path):
    with open(src_path, "rb") as f:
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)

            if not chunk:
                break
            conn.send(SIZE)


################################## LOGIN + REGISTER #################################
def login(conn, data, cursor, addr):
    username, password = data[1], data[2]

    if username == "" or password == "":
        send_data = "2011"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute("SELECT password FROM Account WHERE account=?", (username,))
            result = cursor.fetchone()

        if result:
            with ACTIVE_SESSIONS_LOCK:
                session_key = f"{addr[0]}:{addr[1]}:{username}"
                ACTIVE_SESSIONS[session_key] = {
                    "account": username,
                    "ip_address": addr[0],
                    "client_socket": conn,
                    "created_at": str(datetime.now()),
                    "expires_at": str(
                        datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
                    ),
                }
            send_data = session_key + "\n1030"
        else:
            send_data = "2032"

    conn.send(f"{send_data}\r\n".encode(FORMAT))

    # return send_data


def signup(conn, data, cursor, dbconn):
    username, password, name = data[1], data[2], data[3]
    if username == "" or password == "" or name == "":
        send_data = "2011"
    # elif is_valid_password(password) is False:
    #     send_data = "2012"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute("SELECT account FROM Account WHERE account = ?", (username,))
            result = cursor.fetchone()

        if result:
            send_data = "2013"
        else:
            send_data = "1010"
            # hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO Account (account, password, name) VALUES (?, ?, ?)",
                (username, password, name),
            )
            dbconn.commit()

    conn.send(f"{send_data}\r\n".encode(FORMAT))
    # return send_data

def check_session_timeout(session_key):
    with ACTIVE_SESSIONS_LOCK:
        if session_key not in ACTIVE_SESSIONS:
            return False
        login_time = datetime.strptime(ACTIVE_SESSIONS[session_key]['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() - login_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            del ACTIVE_SESSIONS[session_key]
            return False
        else:
            return True
            
def logout(conn, session_key):
    with ACTIVE_SESSIONS_LOCK:
        if session_key in ACTIVE_SESSIONS:
            conn.send("1320").encode(FORMAT)
            del ACTIVE_SESSIONS[session_key]
        else:
            conn.send("2321").encode(FORMAT)
        

def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    while True:
        sesison_key = conn.recv(SIZE).decode(FORMAT)
        is_active = check_session_timeout(sesison_key)
        if is_active == False:
            conn.send("2311").encode(FORMAT)
        else:
            conn.send("1310").encode(FORMAT)
            
        data = conn.recv(SIZE).decode(FORMAT)
        if len(data) == 0:
            break
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
            
        elif cmd == "LOGIN":
            login(conn, data, cursor)
        elif cmd == "SIGNUP":
            signup(conn, data, cursor, dbconn)
        elif cmd == "LOGOUT":
            logout(conn, sesison_key)
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
