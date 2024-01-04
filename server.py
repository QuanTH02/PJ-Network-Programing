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
    account, password = data[1], data[2]

    if account == "" or password == "":
        send_data = "2011"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute("SELECT password FROM Account WHERE account=?", (account,))
            result = cursor.fetchone()

        if result:
            if result[0] != password:
                send_data = "2032"
            else:
                with ACTIVE_SESSIONS_LOCK:
                    session_key = f"{addr[0]}:{addr[1]}:{account}"
                    ACTIVE_SESSIONS[session_key] = {
                        "account_id": account,
                        "username": account,
                    }
                send_data = "1030"
        else:
            send_data = "2031"

    conn.send(send_data.encode(FORMAT))
    if "username" in locals():
        return ACTIVE_SESSIONS.get(f"{addr[0]}:{addr[1]}:{account}")
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


def quit_team(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]
    
        # Check if the user is the leader of the team
    cursor.execute("SELECT leader FROM Team WHERE team_name = ?", (team_name,))
    leader_result = cursor.fetchone()

    if leader_result and leader_result[0] == account:
        send_data = "2111"  # Cannot quit as the team leader
    else:
        cursor.execute("DELETE FROM Team_member WHERE team_name=? AND account=?", (team_name, account),)
        send_data = "1110"  # Successfully quit the team
        dbconn.commit()       
    conn.send(send_data.encode(FORMAT))

def remove_member(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]
    # Remove the member from the team
    cursor.execute("DELETE FROM Team_member WHERE team_name = ? AND account = ?", (team_name, account))
    dbconn.commit()
    send_data = "1120"  # Successfully removed the member
    conn.send(send_data.encode(FORMAT))


def get_all_user(conn, cursor):
    cursor.execute("SELECT account FROM Account")
    result = cursor.fetchall()
    user = [row[0] for row in result]
    send_data = "1130\n" + "\n".join(user)
    conn.send(send_data.encode(FORMAT))


def invite_member(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]
    cursor.execute("SELECT name FROM Account WHERE account = ?", (account,))
    user_result = cursor.fetchone()
    if user_result is not None:
    # Check if the user is already a member of the team
        cursor.execute("SELECT * FROM Team_member WHERE team_name = ? AND account = ?", (team_name, account))
        user_existed = cursor.fetchone()

        if user_existed is not None:
            send_data = "2141"
        else:
            cursor.execute("INSERT INTO Invite_request (receiver, team_name) VALUES (?, ?)",
                                        (account, team_name))                
            dbconn.commit()
            send_data = "1140"  # Invite request sent successfully

    conn.send(send_data.encode(FORMAT))

def get_all_invitations(cursor, data, conn):
    account = data[1]
    cursor.execute("SELECT * FROM Invite_request WHERE receiver=?", (account,))
    result = cursor.fetchall()

    if result:
        send_data = "\n".join([f"You have received an invitation to join team '{row[2]}'" for row in result])
    else:
        send_data = "No pending invitations."

    conn.send(send_data.encode(FORMAT))



def accept_invitation(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]
    cursor.execute("INSERT INTO Team_member (account, team_name) VALUES (?, ?)",
                                        (account, team_name)) 
    dbconn.commit()

    cursor.execute("DELETE FROM Invite_request WHERE receiver=? AND team_name=?", (account, team_name),)
    dbconn.commit()

    send_data = "1160"
    conn.send(send_data.encode(FORMAT))


def decline_invitation(conn, data, cursor, dbconn):
    team_name, account = data[1], data[2]
    cursor.execute("DELETE FROM Invite_request WHERE receiver=? AND team_name=?", (account, team_name),)
    dbconn.commit()

    send_data = "1170"
    conn.send(send_data.encode(FORMAT))


def delete_file(conn, data):
    filename = data[1]
    path = f"{SERVER_DATA_PATH} / {filename}"
    os.remove(path)

    send_data = "1210"
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

            cursor.execute(
                "INSERT INTO team_member (account, team_name) VALUES (?, ?)",
                (account, team_name),
            )
            dbconn.commit()

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

def change_password(conn, data, cursor, dbconn):
    account, password, new_password, cf_password = data[1], data[2], data[3], data[4]
    if account is not None:
        cursor.execute(
            "SELECT password FROM Account WHERE account = ?",
            (account, ),
        )
        pw_result = cursor.fetchone()
        if pw_result and pw_result[0] == password:
            if pw_result[0] == new_password:
                send_data = "2021"
            elif new_password != cf_password:
                send_data = "2022"
            elif is_valid_password(new_password) is False:
                send_data = "2023"
            else:
                with DB_CONNECTIONS_LOCK:
                    cursor.execute(
                        "UPDATE Account SET password = ? WHERE account = ?",
                        (new_password, account),
                    )
                    dbconn.commit()
                send_data = "1020"
        else:
            send_data = "2024"
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
            elif cmd == "QUIT":
                quit_team(conn, data, cursor, dbconn)
            elif cmd == "GET_ALL_INVITATIONS":
                get_all_invitations(cursor, data, conn)
            elif cmd == "ACCEPT_INVITATION":
                accept_invitation(conn, data, cursor, dbconn)
            elif cmd == "DECLINE_INVITATION":
                decline_invitation(conn, data, cursor, dbconn)
            elif cmd == "REMOVE_MEMBER":
                remove_member(conn, data, cursor, dbconn)
            elif cmd == "CREATE_TEAM":
                create_team(conn, data, cursor, dbconn)
            elif cmd == "GET_ALL_USER":
                get_all_user(conn, cursor)
            elif cmd == "INVITE_MEMBER":
                invite_member(conn, data, cursor, dbconn)
            elif cmd == "SHOW_MY_TEAMS":
                show_my_teams(conn, data, cursor)
            elif cmd == "CHANGE_PASSWORD":
                change_password(conn, data, cursor, dbconn)
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
