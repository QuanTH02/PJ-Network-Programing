import os
import random
import socket
import string
import threading
import sqlite3

from tqdm import tqdm

IP = "0.0.0.0"
PORT = 5000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
FILE_BLOCK_SIZE = 131072

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
    filename, des_path, file_size = data[1], data[2], int(data[3])
    des_path += "/" + filename
    filepath = os.path.join(SERVER_DATA_PATH, des_path)

    print("To exists")
    if os.path.exists(filepath):
        send_data = "2281"
        conn.send(send_data.encode(FORMAT))
        return send_data
    
    conn.send("OK".encode(FORMAT))

    print("To bar")
    bar = tqdm(
        range(file_size),
        f"Receiving {filepath}",
        unit="B",
        unit_scale=True,
        unit_divisor=SIZE,
    )

    print("To open")
    with open(filepath, "wb") as f:
        while file_size > 0:
            chunk = conn.recv(FILE_BLOCK_SIZE)
            f.write(chunk)
            bar.update(len(chunk))
            file_size -= len(chunk)

    send_data = "1190"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def download_file(conn, data):
    path = data[1]
    with open(path, "rb") as f:
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)     
            if not chunk:
                break
            conn.send(chunk)

    send_data = "1200\n"
    return send_data

def make_directory(conn, data):
    dir_path = data[1]
    full_path = os.path.join(SERVER_DATA_PATH, dir_path)

    try:
        os.makedirs(full_path)
        send_data = "1240"
    except FileExistsError:
        send_data = "2242"

    # conn.send(send_data.encode(FORMAT))
    return send_data


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

    # conn.send(send_data.encode(FORMAT))
    return send_data

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

    # conn.send(send_data.encode(FORMAT))
    return send_data

def delete_directory(conn, data):
    dir_path = data[1]

    full_path = os.path.join(SERVER_DATA_PATH, dir_path)
    os.rmdir(full_path)
    send_data = "1260"

    # conn.send(send_data.encode(FORMAT))
    return send_data

def copy_directory(conn, data):
    dir_path = data[1]
    des_path = data[2]
    dir_name = dir_path.rsplit('/', 1)[-1]

    full_des_path = os.path.join(SERVER_DATA_PATH, des_path)
    full_des_path = os.path.join(full_des_path, dir_name)

    try:
        os.makedirs(full_des_path)
        send_data = "1270"
    except FileExistsError:
        send_data = "2271"

    # conn.send(send_data.encode(FORMAT))
    return send_data

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

    # conn.send(send_data.encode(FORMAT))
    return send_data


def show_my_teams(conn, data, cursor):
    print("Show my teams: ~~~~~~~~~~~~~")
    username = data[1]

    if username is not None:
        cursor.execute(
            "SELECT team_code, team_name FROM team WHERE team_name IN (SELECT team_name FROM team_member WHERE account = ?)",
            (username, ),
        )
        # cursor.execute(
        #     "SELECT team_name FROM team_member WHERE account = ?",
        #     (username, ),
        # )
        result = cursor.fetchall()

        if not result:
            send_data = "1261\nYou are not a member of any team."
        else:
            result_team = []
            result_code = []

            for row in result:
                code = row[0]
                team = row[1]
                
                result_code.append(code)
                result_team.append(team)
                
            send_data = "1260\n" + "\n".join(result_team).rstrip("\n")
            send_data += "\n" + "\n".join(result_code)
        
    else:
        send_data = "2011"

    # conn.send(send_data.encode(FORMAT))
    return send_data

def show_team_member(conn, data, cursor):
    team_name = data[1]
    send_data = "1100"

    cursor.execute(
        "SELECT account FROM team_member WHERE team_name = ?",
        (team_name, )
    )

    result = cursor.fetchall()

    for account in result:
        send_data += "\n" + account[0]

    # conn.send(send_data.encode(FORMAT))
    return send_data


#################################################################### 
####################################################################
####################################################################

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
                    "account_id": username,
                    "username": username,
                }
            send_data = "1030"
        else:
            send_data = "2032"

    conn.send(f"{send_data}\r\n".encode(FORMAT))
    if "username" in locals():
        return ACTIVE_SESSIONS.get(f"{addr[0]}:{addr[1]}:{username}")
    else:
        return None
    
    # return send_data


def register(conn, data, cursor, dbconn):
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

    conn.send("{send_data}\r\n".encode(FORMAT))
    # return send_data

def random_team_code(cursor):
    characters = string.ascii_letters + string.digits
    code = "".join(random.choice(characters) for _ in range(6))
    cursor.execute("Select team_code from team")
    result = cursor.fetchall()
    while code in result:
        characters = string.ascii_letters + string.digits
        code = "".join(random.choice(characters) for _ in range(6))
    return code

def create_team(conn, data, cursor, dbconn):
    print("To create team")
    team_name, account = data[1], data[2]

    if not team_name:
        send_data = "2011"
    else:
        print("To select team")
        cursor.execute("SELECT team_name FROM team WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()
        if result is not None:
            send_data = "2041"
        else:
            team_path = os.path.join(SERVER_DATA_PATH, team_name)
            os.makedirs(team_path)
            team_code = random_team_code(cursor)
            send_data = "1040\n" + team_code
            cursor.execute(
                "INSERT INTO team (leader, team_name, team_code) VALUES (?, ?, ?)",
                (account, team_name, team_code),
            )
            dbconn.commit()

    # conn.send(send_data.encode(FORMAT))
    print("To return")
    return send_data

def join_team(conn, data, cursor, dbconn):
    code = data[1]
    account = data[2]
    print("To join team")
    if code == None or account == None:
        send_data = "2011"
    else:
        cursor.execute(
            "SELECT team_code, team_name FROM team WHERE team_code = ?", (code,)
        )
        result = cursor.fetchone()

        print("To result")
        if result is None or result[0] is None:
            send_data = "2061"
        else:
            team_name = result[1]
            cursor.execute(
                "SELECT account from team_member where team_name = ?", (team_name,)
            )
            team_account = cursor.fetchall()
            print(team_account)
            print("Account: ", account)
            if any(account in record for record in team_account):
                send_data = "2062"
            else:
                send_data = "1060"
                cursor.execute(
                    "Insert into join_request (sender, team_name) values (?,?)",
                    (account, team_name),
                )
                dbconn.commit()
    # conn.send(send_data.encode(FORMAT))
    print("To return")
    return send_data

####################################################################
####################################################################
####################################################################

def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    active_session = None

    while True:
        requests = conn.recv(SIZE).decode(FORMAT)

        if len(requests) == 0:
            return

        if requests == "\r\n":
            break     

        unknown = None
        if not requests.endswith("\r\n"):
            unknown = "3000\r\n"
            # Sửa
            commands = [request for request in requests.split('\r\n')[:-1] if request] 
        else:
            commands = [request for request in requests.split('\r\n') if request]

        print(commands)

        for command in commands:
            data = command.split("\n")
            cmd = data[0]

            if cmd == "LOGIN":
                active_session = login(conn, data, cursor, addr)
            elif cmd == "LOGOUT":
                active_session = None
                conn.send("1300\r\n".encode(FORMAT))
            elif cmd == "SIGNUP":
                register(conn, data, cursor, dbconn)
            elif active_session is not None:
                print("Go to active session")
                account_id = active_session["account_id"]
                username = active_session["username"]
                if cmd == "UPLOAD":
                    response = upload_file(conn, data)
                elif cmd == "MKDIR":
                    response = make_directory(conn, data)
                elif cmd == "SHOW_MY_TEAMS":
                    response = show_my_teams(conn, data, cursor)
                elif cmd == "GET_MEMBER":
                    response = show_team_member(conn, data, cursor)
                elif cmd == "CREATE_FOLDER":
                    response = create_directory(conn, data)
                elif cmd == "RENAME_FOLDER":
                    response = rename_directory(conn, data)
                elif cmd == "DELETE_FOLDER":
                    response = delete_directory(conn, data)
                elif cmd == "COPY_FOLDER":
                    response = copy_directory(conn, data)
                elif cmd == "MOVE_FOLDER":
                    response = move_directory(conn, data)
                elif cmd == "JOIN_TEAM":
                    response = join_team(conn, data, cursor, dbconn)
                elif cmd == "CREATE_TEAM":
                    print("CREATE_TEAM")
                    response = create_team(conn, data, cursor, dbconn)
                else:
                    response = "4040"

                response += "\r\n"

                if unknown:
                    response += unknown

                conn.send(response.encode(FORMAT))
                print("Response: ", response)

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
