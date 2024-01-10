import os
import random
import shutil
import string
import sys
from quan_server import check_role

sys.path.append("../")

from config import (
    SERVER_DATA_PATH,
)

def write_client_message_log(addr, request, response, cursor, dbconn):
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

    cursor.execute("Select team_code from team WHERE team_code = ?", (code,))

    result = cursor.fetchone()
    if result:
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
                "SELECT account from team_member where team_name = ? AND account = ?",
                (team_name, account),
            )
            result = cursor.fetchone()
            if result:
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
            cursor.execute(
                "Insert into team_member values (?,?)", (request_sender, team_name)
            )
            dbconn.commit()
            cursor.execute(
                "Delete from join_request where team_name = ? and sender = ?",
                (team_name, request_sender),
            )
            dbconn.commit()

            cursor.execute(
                "Delete from invite_request where team_name = ? and receiver = ?",
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
