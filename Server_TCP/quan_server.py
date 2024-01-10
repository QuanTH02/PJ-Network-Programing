import os
import shutil
import sys

sys.path.append("../")

from config import (
    FORMAT,
    SERVER_DATA_PATH,
    FILE_BLOCK_SIZE,
)


def check_role(account, team_name, cursor):
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

        cursor.execute(
            "SELECT account FROM team_member WHERE team_name = ?", (team_name,)
        )
        result = cursor.fetchall()

        for account in result:
            send_data += "\n" + account[0]
        print("To return")
        # conn.send(send_data.encode(FORMAT))
    return send_data
