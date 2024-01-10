from datetime import datetime, timedelta
import os
import random
import re
import shutil
import socket
import string
import threading
import sqlite3
from tqdm import tqdm

import sys

sys.path.append("../")

from config import (
    LIST_CMD,
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


def check_role(account, team_name, cursor):
    with DB_CONNECTIONS_LOCK:
        cursor.execute(
            "SELECT leader FROM team WHERE team_name = ?",
            (team_name,),
        )
        result = cursor.fetchone()

    if result is None:
        return "Team not exist"

    if result[0] == account:
        return "Leader"
    else:
        with DB_CONNECTIONS_LOCK:
            cursor.execute(
                "SELECT account FROM team_member WHERE team_name = ? AND account = ?",
                (team_name, account),
            )
            result = cursor.fetchone()

        if result:
            return "Member"
        else:
            return None


def upload_file(conn, data, account, cursor):
    print("Uploading file")
    filename, team_name, des_path, file_size = data[1], data[2], data[3], int(data[4])

    role = check_role(account, team_name, cursor)

    if role == "Team not exist":
        send_data = "2042"
        conn.send(send_data.encode(FORMAT))
        return send_data
    elif role is None:
        send_data = "2101"
        conn.send(send_data.encode(FORMAT))
        return send_data

    des_path = SERVER_DATA_PATH + "/" + team_name + "/" + des_path

    print(des_path)
    if not os.path.isdir(des_path):
        send_data = "3001"
        conn.send(send_data.encode(FORMAT))
        return send_data

    filepath = des_path + "/" + filename

    if os.path.exists(filepath):
        new_file_name = filename.split(".")[0] + "(1)." + filename.split(".")[1]
        filepath = os.path.join(des_path, new_file_name)

    conn.send("OK".encode(FORMAT))

    print("To open")
    with open(filepath, "wb") as f:
        while file_size > 0:
            chunk = conn.recv(FILE_BLOCK_SIZE)
            f.write(chunk)
            file_size -= len(chunk)

    send_data = "1190"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def download_file(conn, data, account, cursor):
    team_name = data[1]
    path = SERVER_DATA_PATH + "/" + team_name + "/" + data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
        conn.send(send_data.encode(FORMAT))
        return send_data
    elif role is None:
        send_data = "2101"
        conn.send(send_data.encode(FORMAT))
        return send_data

    if not os.path.exists(path):
        send_data = "2201"
        conn.send(send_data.encode(FORMAT))
        return send_data

    conn.send("OK".encode(FORMAT))

    file_size = os.path.getsize(path)

    conn.send(str(file_size).encode(FORMAT))
    with open(path, "rb") as f:
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)
            if not chunk:
                break
            conn.send(chunk)

    send_data = "1200"
    return send_data


def create_directory(conn, data, account, cursor):
    team_name = data[1]
    dir_path = data[2]
    dir_name = data[3]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
        return send_data

    elif role is None:
        send_data = "2101"
        return send_data

    full_path = os.path.join(SERVER_DATA_PATH, team_name)
    full_path = os.path.join(full_path, dir_path)
    full_path = os.path.join(full_path, dir_name)
    print(full_path)

    if os.path.exists(full_path):
        send_data = "2251"
        conn.send(send_data.encode(FORMAT))
        return send_data

    try:
        os.makedirs(full_path)
        send_data = "1250"
    except FileExistsError:
        send_data = "2252"

    # conn.send(send_data.encode(FORMAT))
    return send_data


def rename_directory(conn, data, account, cursor):
    team_name = data[1]
    dir_path = data[2]
    dir_name = data[3]
    dir_new_name = data[4]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
        return send_data

    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        path_team_dir = SERVER_DATA_PATH + "/" + team_name + "/" + dir_path

        full_path_old = os.path.join(path_team_dir, dir_name)
        full_path_new = os.path.join(path_team_dir, dir_new_name)

        if not os.path.exists(full_path_old):
            send_data = "2261"
            conn.send(send_data.encode(FORMAT))
            return send_data

        try:
            os.rename(full_path_old, full_path_new)
            send_data = "1260"
        except FileExistsError:
            send_data = "2251"

        # conn.send(send_data.encode(FORMAT))
    return send_data


def delete_directory(conn, data, account, cursor):
    team_name = data[1]
    dir_path = data[2]
    dir_name = data[3]

    role = check_role(account, team_name, cursor)

    if role == "Team not exist":
        send_data = "2042"
        return send_data
    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        full_path = os.path.join(SERVER_DATA_PATH, team_name, dir_path, dir_name)
        print(full_path)

        if not os.path.exists(full_path):
            send_data = "2261"
            conn.send(send_data.encode(FORMAT))
            return send_data

        shutil.rmtree(full_path)
        send_data = "1270"

        # conn.send(send_data.encode(FORMAT))
    return send_data


def copy_directory(conn, data, account, cursor):
    team_name = data[1]
    src_path = data[2]
    dir_name = data[3]
    des_path = data[4]

    role = check_role(account, team_name, cursor)

    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    else:
        full_path_dir = os.path.join(SERVER_DATA_PATH, team_name, src_path, dir_name)
        full_des_path = os.path.join(SERVER_DATA_PATH, team_name, des_path, dir_name)

        print(full_path_dir)
        print(full_des_path)
        try:
            shutil.copytree(full_path_dir, full_des_path)
            send_data = "1280"
        except FileExistsError:
            send_data = "2281"

    return send_data


def move_directory(conn, data, account, cursor):
    team_name = data[1]
    src_path = data[2]
    dir_name = data[3]
    des_path = data[4]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    else:
        full_path_dir = os.path.join(SERVER_DATA_PATH, team_name, src_path, dir_name)
        full_des_path = os.path.join(SERVER_DATA_PATH, team_name, des_path, dir_name)

        try:
            shutil.copytree(full_path_dir, full_des_path)
            shutil.rmtree(full_path_dir)
            send_data = "1290"
        except FileExistsError:
            send_data = "2281"

    # conn.send(send_data.encode(FORMAT))
    return send_data


def show_my_teams(username, cursor):
    print("Show my teams: ~~~~~~~~~~~~~")

    with DB_CONNECTIONS_LOCK:
        cursor.execute(
            "SELECT team_name FROM team_member WHERE account = ?",
            (username,),
        )

    result = cursor.fetchall()

    if not result:
        send_data = "1051"
    else:
        send_data = "1050"

        for team_name in result:
            send_data += "\n" + team_name[0]

    # conn.send(send_data.encode(FORMAT))
    return send_data


def show_team_member(data, account, cursor):
    team_name = data[1]

    role = check_role(account, team_name, cursor)

    if role is None:
        send_data = "2101"
    else:
        send_data = "1100"
        print("To show team member")

        with DB_CONNECTIONS_LOCK:
            cursor.execute(
                "SELECT account FROM team_member WHERE team_name = ?", (team_name,)
            )
            result = cursor.fetchall()

        for account in result:
            send_data += "\n" + account[0]
        print("To return")
        # conn.send(send_data.encode(FORMAT))
    return send_data


#####################################################################
#####################################################################
#####################################################################


def login(conn, data, cursor, addr):
    username, password = data[1], data[2]

    if username == "" or password == "":
        send_data = "2011"
    else:
        with DB_CONNECTIONS_LOCK:
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
                            datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
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


def register(data, cursor, dbconn):
    username, password, name = data[1], data[2], data[3]
    if username == "" or password == "" or name == "":
        send_data = "2011"
    # elif is_valid_password(password) is False:
    #     send_data = "2012"
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
            # hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            with DB_CONNECTIONS_LOCK:
                cursor.execute(
                    "INSERT INTO Account (account, password, name) VALUES (?, ?, ?)",
                    (username, password, name),
                )
                dbconn.commit()

    # conn.send("{send_data}\r\n".encode(FORMAT))
    return send_data


def change_password(data, account, cursor, dbconn):
    password, new_password, cf_password = data[1], data[2], data[3]
    if account is not None:
        cursor.execute(
            "SELECT password FROM Account WHERE account = ?",
            (account,),
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

    # conn.send(send_data.encode(FORMAT))
    return send_data


#####################################################################
#####################################################################
#####################################################################


def quit_team(conn, data, account, cursor, dbconn):
    team_name = data[1]

    role = check_role(account, team_name, cursor)

    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Leader":
        send_data = "2111"
    else:
        cursor.execute(
            "DELETE FROM Team_member WHERE team_name=? AND account=?",
            (team_name, account),
        )
        send_data = "1110"  # Successfully quit the team
        dbconn.commit()

    # conn.send(send_data.encode(FORMAT))
    return send_data


def remove_member(conn, data, account, cursor, dbconn):
    team_name, member_name = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        # Remove the member from the team
        cursor.execute(
            "SELECT account FROM Team_member WHERE team_name = ? AND account = ?",
            (team_name, member_name),
        )
        result = cursor.fetchone()
        if result is None:
            send_data = "2122"
        else:
            if result[0] == account:
                send_data = "2123"
            else:
                cursor.execute(
                    "DELETE FROM Team_member WHERE team_name = ? AND account = ?",
                    (team_name, member_name),
                )
                dbconn.commit()
                send_data = "1120"  # Successfully removed the member

    # conn.send(send_data.encode(FORMAT))
    return send_data


def get_all_user(username, cursor):
    cursor.execute("SELECT account FROM Account WHERE account != ?", (username,))
    result = cursor.fetchall()
    user = [row[0] for row in result]
    send_data = "1130" + "\n".join(user)
    # conn.send(send_data.encode(FORMAT))
    return send_data


def invite_member(data, account, cursor, dbconn):
    team_name, member_name = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        cursor.execute("SELECT account FROM Account WHERE account = ?", (member_name,))
        user_result = cursor.fetchone()
        if user_result is None:
            send_data = "2141"
        else:
            # Check if the user is already a member of the team
            cursor.execute(
                "SELECT * FROM Team_member WHERE team_name = ? AND account = ?",
                (team_name, member_name),
            )
            user_existed = cursor.fetchone()

            if user_existed is not None:
                send_data = "2142"
            else:
                cursor.execute(
                    "INSERT INTO Invite_request (receiver, team_name) VALUES (?, ?)",
                    (member_name, team_name),
                )
                dbconn.commit()
                send_data = "1140"  # Invite request sent successfully

    # conn.send(send_data.encode(FORMAT))
    return send_data


def get_all_invitations(account, cursor):
    cursor.execute("SELECT team_name FROM Invite_request WHERE receiver=?", (account,))
    result = cursor.fetchall()

    print(result)
    if result:
        send_data = "1150\n" + "\n".join(row[0] for row in result)
    else:
        send_data = "2151"

    # conn.send(send_data.encode(FORMAT))
    return send_data


def accept_invitation(data, account, cursor, dbconn):
    team_name = data[1]

    cursor.execute(
        "SELECT team_name FROM Invite_request WHERE receiver=? AND team_name=?",
        (account, team_name),
    )
    result = cursor.fetchone()
    if result is None:
        send_data = "2161"
    else:
        cursor.execute(
            "INSERT INTO Team_member (account, team_name) VALUES (?, ?)",
            (account, team_name),
        )
        dbconn.commit()

        cursor.execute(
            "DELETE FROM Invite_request WHERE receiver=? AND team_name=?",
            (account, team_name),
        )
        dbconn.commit()

        send_data = "1160"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def decline_invitation(data, account, cursor, dbconn):
    team_name = data[1]

    cursor.execute(
        "SELECT team_name FROM Invite_request WHERE receiver=? AND team_name=?",
        (account, team_name),
    )
    result = cursor.fetchone()
    if result is None:
        send_data = "2161"
    else:
        cursor.execute(
            "DELETE FROM Invite_request WHERE receiver=? AND team_name=?",
            (account, team_name),
        )
        dbconn.commit()

        send_data = "1170"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def dir_information(data, account, cursor):
    team_name, dir_path = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    else:
        path = os.path.join(SERVER_DATA_PATH, team_name, dir_path)
        if not os.path.exists(path):
            send_data = "2181"
        else:
            files = os.listdir(path)

            if len(files) == 0:
                send_data = "2182"
            else:
                send_data = "1180\n" + "\n".join(f for f in files)
    # conn.send(send_data.encode(FORMAT))
    return send_data


####################################################################
####################################################################
####################################################################
# NAM
####################################################################
####################################################################
####################################################################
def write_client_message_log(addr, request, response, cursor, dbconn):
    with DB_CONNECTIONS_LOCK:
        cursor.execute(
            "Insert into log(time, client_address,request,response) values(datetime('now'),?,?,?)",
            (str(f"{addr[0]}:{addr[1]}"), request, response),
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


def create_team(data, account, cursor, dbconn):
    team_name = data[1]

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

    return send_data


def join_team(data, account, cursor, dbconn):
    team_code = data[1]
    if team_code == None or account == None:
        send_data = "2011"
    else:
        cursor.execute("SELECT team_name FROM team WHERE team_code = ?", (team_code,))
        result = cursor.fetchone()

        if result is None:
            send_data = "2061"
        else:
            team_name = result[0]
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
    return send_data


def get_join_request(data, account, cursor):
    team_name = data[1]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Member":
        send_data = "2214"

    else:
        cursor.execute(
            "SELECT sender from join_request where team_name = ?", (team_name,)
        )
        results = cursor.fetchall()
        send_data = "1070"
        for result in results:
            send_data = send_data + "\n" + result[0]
    return send_data


def accept_join_request(data, account, cursor, dbconn):
    team_name = data[1]
    request_sender = data[2]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Member":
        send_data = "2214"

    else:
        cursor.execute(
            "Select sender from join_request where sender = ? and team_name = ?",
            (request_sender, team_name),
        )
        result = cursor.fetchone()
        if result is None:
            send_data = "2081"
        else:
            send_data = "1080"
            cursor.execute("Insert into team_member values (?,?)", (request_sender, team_name))
            dbconn.commit()
            cursor.execute(
                "Delete from join_request where team_name = ? and sender = ?",
                (team_name, request_sender),
            )
            dbconn.commit()
    return send_data


def decline_join_request(data, account, cursor, dbconn):
    team_name = data[1]
    request_sender = data[2]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Member":
        send_data = "2214"

    else:
        cursor.execute(
            "Select sender from join_request where sender = ? and team_name = ?",
            (request_sender, team_name),
        )
        result = cursor.fetchone()
        if result is None:
            send_data = "2081"
        else:
            send_data = "1090"
            cursor.execute(
                "Delete from join_request where team_name = ? and sender = ?",
                (team_name, request_sender),
            )
            dbconn.commit()
    return send_data


def delete_file(data, account, cursor):
    team_name = data[1]
    dir_path = data[2]
    filename = data[3]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    else:
        file_path = os.path.join(SERVER_DATA_PATH, team_name, dir_path, filename)            
        try:
            os.remove(file_path)
            send_data = "1220"
        except FileNotFoundError:
            send_data = "2215"

    return send_data


def rename_file(data, account, cursor):
    team_name = data[1]
    dir_path = data[2]
    old_file_name = data[3]
    new_file_name = data[4]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Member":
        send_data = "2214"
    else:
        if not new_file_name:
            send_data = "2212"
        elif "/" in new_file_name or "\\" in new_file_name:
            send_data = "2212"
        elif new_file_name.endswith("."):
            send_data = "2212"
        else:
            new_file_extension = new_file_name.split(".")[-1]
            old_file_extension = old_file_name.split(".")[-1]

            if new_file_extension.lower() != old_file_extension.lower():
                send_data = "2213"
            else:
                file_path = os.path.join(
                    SERVER_DATA_PATH, team_name, dir_path, old_file_name
                )
                new_full_path = os.path.join(
                    SERVER_DATA_PATH, team_name, dir_path, new_file_name
                )
                try:
                    os.rename(file_path, new_full_path)
                    send_data = "1210"
                except FileNotFoundError:
                    send_data = "2215"
                except FileExistsError:
                    send_data = "2211"

    return send_data


def copy_file(data, account, cursor):
    team_name = data[1]
    src_dir = data[2]
    filename = data[3]
    destination_directory = data[4]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    else:
        destination_file_path = os.path.join(
            SERVER_DATA_PATH, team_name, destination_directory, filename
        )
        src_path = os.path.join(SERVER_DATA_PATH, team_name, src_dir, filename)
        if not os.path.exists(src_path):
            send_data = "2215"
        elif not os.path.exists(
            os.path.join(SERVER_DATA_PATH, team_name, destination_directory)
        ):
            send_data = "2232"
        else:
            try:
                shutil.copy2(src_path, destination_file_path)
                send_data = "1230"
            except shutil.SameFileError:
                send_data = "2231"

    return send_data


def move_file(data, account, cursor):
    team_name = data[1]
    src_dir = data[2]
    filename = data[3]
    destination_directory = data[4]
    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    else:
        destination_file_path = os.path.join(
            SERVER_DATA_PATH, team_name, destination_directory, filename
        )
        src_path = os.path.join(SERVER_DATA_PATH, team_name, src_dir, filename)
        if not os.path.exists(src_path):
            send_data = "2215"
        elif not os.path.exists(
            os.path.join(SERVER_DATA_PATH, team_name, destination_directory)
        ):
            send_data = "2232"
        else:
            try:
                shutil.move(src_path, destination_file_path)
                send_data = "1240"
            except shutil.SameFileError as e:
                print(e)
                send_data = "2231"

    return send_data


####################################################################
####################################################################
####################################################################


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
