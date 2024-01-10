from datetime import datetime, timedelta
import socket
import threading
import sqlite3

from quan_server import (
    upload_file,
    download_file,
    create_directory,
    rename_directory,
    delete_directory,
    copy_directory,
    move_directory,
    show_my_teams,
    show_team_member,
)
from nam_server import (
    write_client_message_log,
    create_team,
    join_team,
    get_join_request,
    accept_join_request,
    decline_join_request,
    delete_file,
    rename_file,
    copy_file,
    move_file,
)
from nguyet_server import (
    register,
    change_password,
    quit_team,
    remove_member,
    get_all_user,
    invite_member,
    get_all_invitations,
    accept_invitation,
    decline_invitation,
    dir_information,
)

import sys

sys.path.append("../")

from config import (
    LIST_CMD,
    IP,
    SESSION_TIMEOUT_MINUTES,
    SIZE,
    FORMAT
)

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
    thread_id = threading.current_thread().ident
    with DB_CONNECTIONS_LOCK:
        if thread_id in DB_CONNECTIONS:
            del DB_CONNECTIONS[thread_id]
    dbconn.close()

# 
def login(conn, data, cursor, addr):
    username, password = data[1], data[2]

    if username == "" or password == "":
        send_data = "2011"
    else:
        cursor.execute("SELECT password FROM Account WHERE account=?", (username,))
        result = cursor.fetchone()

        if result:
            if result[0] != password:
                send_data = "2032"
            else:
                with ACTIVE_SESSIONS_LOCK:
                    ACTIVE_SESSIONS[addr] = {
                        "account": username,
                        "ip_address": addr,
                        "client_socket": conn,
                        "created_at": str(datetime.now()),
                        "expires_at": str(
                            datetime.now()
                            + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
                        ),
                    }
                send_data = "1030\n" + username
        else:
            send_data = "2031"

    # conn.send(f"{send_data}\r\n".encode(FORMAT))

    return send_data


def check_session_timeout(ip_address):
    with ACTIVE_SESSIONS_LOCK:
        if ip_address not in ACTIVE_SESSIONS:
            return False
        login_time = datetime.strptime(
            ACTIVE_SESSIONS[ip_address]["created_at"], "%Y-%m-%d %H:%M:%S.%f"
        )
        if datetime.now() - login_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            del ACTIVE_SESSIONS[ip_address]
            return False
        else:
            return True
# 


def handle_client(conn, addr):
    with get_database_connection() as dbconn:
        cursor = dbconn.cursor()

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    current_account = None
    quit_program = False

    while True:
        requests = conn.recv(SIZE).decode(FORMAT)
        unknown = None

        if "\r\n" not in requests:
            unknown = "3000\r\n"
            conn.send(unknown.encode(FORMAT))
            continue

        if len(requests) == 0:
            break

        if requests == "\r\n":
            continue

        if not requests.endswith("\r\n"):
            unknown = "3000\r\n"
            commands = [request for request in requests.split("\r\n")[:-1] if request]
        else:
            commands = [request for request in requests.split("\r\n") if request]
        print(commands)

        for command in commands:
            data = command.split("\n")
            cmd = data[0]

            if len(cmd) == 0 or cmd == "QUIT":
                quit_program = True
                break

            if cmd not in LIST_CMD:
                response = "3000"
            else:
                if current_account is None:
                    print("You are not logged in!")
                    if cmd == "LOGIN":
                        if len(data) != 3:
                            response = "3001"
                        else:
                            response = login(conn, data, cursor, addr)
                            if response.startswith("1030"):
                                current_account = response.split("\n")[1]
                    elif cmd == "SIGNUP":
                        if len(data) != 4:
                            response = "3001"
                        else:
                            response = register(data, cursor, dbconn)
                    else:
                        response = "2322"
                else:
                    print("You are logged in!")

                    if not check_session_timeout(addr):
                        response = "2311"
                    else:
                        if cmd == "UPLOAD":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = upload_file(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "DOWNLOAD":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = download_file(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "CHANGE_PASSWORD":
                            if len(data) != 4:
                                response = "3001"
                            else:
                                response = change_password(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "SHOW_MY_TEAMS":
                            if len(data) != 1:
                                response = "3001"
                            else:
                                response = show_my_teams(current_account, cursor)
                        elif cmd == "GET_MEMBER":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = show_team_member(
                                    data, current_account, cursor
                                )
                        elif cmd == "CREATE_FOLDER":
                            if len(data) != 4:
                                response = "3001"
                            else:
                                response = create_directory(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "RENAME_FOLDER":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = rename_directory(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "DELETE_FOLDER":
                            if len(data) != 4:
                                response = "3001"
                            else:
                                response = delete_directory(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "COPY_FOLDER":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = copy_directory(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "MOVE_FOLDER":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = move_directory(
                                    conn, data, current_account, cursor
                                )
                        elif cmd == "JOIN_TEAM":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = join_team(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "CREATE_TEAM":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = create_team(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "QUIT_TEAM":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = quit_team(
                                    conn, data, current_account, cursor, dbconn
                                )
                        elif cmd == "REMOVE_MEMBER":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = remove_member(
                                    conn, data, current_account, cursor, dbconn
                                )
                        elif cmd == "GET_ALL_USER":
                            if len(data) != 1:
                                response = "3001"
                            else:
                                response = get_all_user(current_account, cursor)
                        elif cmd == "INVITE_MEMBER":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = invite_member(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "GET_ALL_INVITATIONS":
                            if len(data) != 1:
                                response = "3001"
                            else:
                                response = get_all_invitations(current_account, cursor)
                        elif cmd == "ACCEPT_INVITATION":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = accept_invitation(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "DECLINE_INVITATION":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = decline_invitation(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "FOLDER_INFORMATION":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = dir_information(
                                    data, current_account, cursor
                                )
                        elif cmd == "LOGOUT":
                            if len(data) != 1:
                                response = "3001"
                            else:
                                response = "1320"
                                current_account = None
                                with ACTIVE_SESSIONS_LOCK:
                                    del ACTIVE_SESSIONS[addr]
                        elif cmd == "GET_JOIN_REQUEST":
                            if len(data) != 2:
                                response = "3001"
                            else:
                                response = get_join_request(
                                    data, current_account, cursor
                                )
                        elif cmd == "ACCEPT_JOIN_REQUEST":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = accept_join_request(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "DECLINE_JOIN_REQUEST":
                            if len(data) != 3:
                                response = "3001"
                            else:
                                response = decline_join_request(
                                    data, current_account, cursor, dbconn
                                )
                        elif cmd == "DELETE_FILE":
                            if len(data) != 4:
                                response = "3001"
                            else:
                                response = delete_file(data, current_account, cursor)
                        elif cmd == "RENAME_FILE":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = rename_file(data, current_account, cursor)
                        elif cmd == "COPY_FILE":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = copy_file(data, current_account, cursor)
                        elif cmd == "MOVE_FILE":
                            if len(data) != 5:
                                response = "3001"
                            else:
                                response = move_file(data, current_account, cursor)

                        else:
                            response = "2321"
            response += "\r\n"

            conn.send(response.encode(FORMAT))
            print("Response: ", response)

            write_client_message_log(addr, command, response, cursor, dbconn)

        if unknown:
            conn.send("3000\r\n".encode(FORMAT))
        if quit_program:
            print("Quiting program")
            with ACTIVE_SESSIONS_LOCK:
                if current_account is not None:
                    del ACTIVE_SESSIONS[addr]
                    current_account = None
            break

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
