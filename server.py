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


def random_team_code(cursor):
    characters = string.ascii_letters + string.digits
    code = "".join(random.choice(characters) for _ in range(6))
    cursor.execute("Select team_code from team")
    result = cursor.fetchall()
    while code in result:
        characters = string.ascii_letters + string.digits
        code = "".join(random.choice(characters) for _ in range(6))
    return code


def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def get_account_id(username, cursor):
    cursor.execute("SELECT account_id FROM Account WHERE account=?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


def login(conn, data, cursor, addr):
    username, password = data[1], data[2]

    if username == "" or password == "":
        send_data = "2011"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute("SELECT password FROM Account WHERE account=?", (username,))
            result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode("utf-8"), result[0]):
            account_id = get_account_id(username, cursor)
            with ACTIVE_SESSIONS_LOCK:
                session_key = f"{addr[0]}:{addr[1]}:{account_id}"
                ACTIVE_SESSIONS[session_key] = {
                    "account_id": account_id,
                    "username": username,
                }
            send_data = "1030"
        else:
            send_data = "2032"

    conn.send(send_data.encode(FORMAT))
    if "account_id" in locals():
        return ACTIVE_SESSIONS.get(f"{addr[0]}:{addr[1]}:{account_id}")
    else:
        return None


def register(conn, data, cursor, dbconn):
    username, password, name = data[1], data[2], data[3]
    if username == "" or password == "" or name == "":
        send_data = "2011"
    elif is_valid_password(password) is False:
        send_data = "2012"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute("SELECT account FROM Account WHERE account = ?", (username,))
            result = cursor.fetchone()

        if result:
            send_data = "2013"
        else:
            send_data = "1010"
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO Account (account, password, name) VALUES (?, ?, ?)",
                (username, hashed_password, name),
            )
            dbconn.commit()

    conn.send(send_data.encode(FORMAT))


def dir_information(conn, data):
    dir = data[1]
    path = os.path.join(SERVER_DATA_PATH, dir)
    files = os.listdir(path)
    send_data = "1170"

    if len(files) == 0:
        send_data += "The server directory is empty"
    else:
        send_data += "\n".join(f for f in files)
    conn.send(send_data.encode(FORMAT))


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
        send_data = "2042"

    conn.send(send_data.encode(FORMAT))


def delete_file(conn, data):
    filename = data[1]
    path = f"{SERVER_DATA_PATH} / {filename}"
    os.remove(path)

    send_data = "1210"
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


def show_my_teams(conn, data, cursor):
    username = data[1]
    account_id = get_account_id(username, cursor)

    if account_id is not None:
        cursor.execute(
            "SELECT team_name FROM team WHERE leader_id = ? OR team_id IN (SELECT team_id FROM team_member WHERE member_id = ?)",
            (account_id, account_id),
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

        if cmd == "LOGIN":
            active_session = login(conn, data, cursor, addr)
        elif cmd == "LOGOUT":
            active_session = None
            break
        elif cmd == "SIGNUP":
            register(conn, data, cursor, dbconn)
        elif active_session is not None:
            account_id = active_session["account_id"]
            username = active_session["username"]
            if cmd == "LIST":
                dir_information(conn, data)
            elif cmd == "UPLOAD":
                upload_file(conn, data)
            elif cmd == "DELETE":
                delete_file(conn, data)
            elif cmd == "MKDIR":
                make_directory(conn, data)
            elif cmd == "CREATE_TEAM":
                create_team(conn, data, cursor, dbconn)
            elif cmd == "SHOW_MY_TEAMS":
                show_my_teams(conn, data, cursor)
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
