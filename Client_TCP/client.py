import socket
import os
import sys

sys.path.append("../")

from config import SIZE, FORMAT, FILE_BLOCK_SIZE
from quan_client import (
    show_my_teams,
    upload_file,
    download_file,
    show_team_member,
    create_directory,
    rename_directory,
    delete_directory,
    copy_directory,
    move_directory,
)
from nam_client import (
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
from nguyet_client import (
    login,
    signup,
    change_password,
    logout,
    quit_team,
    remove_member,
    get_all_user,
    invite_member,
    get_all_invitations,
    accept_invitation,
    decline_invitation,
    dir_information,
)

def responseFromServer(client):
    # print("Go to responseFromServer")
    requests = client.recv(SIZE).decode(FORMAT)

    responses = [request for request in requests.split("\r\n") if request]

    for response in responses:
        # SIGNUP
        if response.startswith("1010"):
            print("Signed up successfully!")
        elif response.startswith("2012"):
            print("Incorrect format!")
        elif response.startswith("2013"):
            print("Account has existed!")

        # CHANGE_PASSWORD
        elif response.startswith("1020"):
            print("Changed password successfully!")
        elif response.startswith("2021"):
            print("The new password can't be the same as the old password!")
        elif response.startswith("2022"):
            print("The passwords do not match!")
        elif response.startswith("2023"):
            print("The new password is not in the correct format!")
        elif response.startswith("2024"):
            print("Incorrect old password!")

        # LOGIN
        elif response.startswith("1030"):
            print("Logged in successfully!")
        elif response.startswith("2011"):
            print("Missing information!")
        elif response.startswith("2031"):
            print("Account doesn't exist!")
        elif response.startswith("2032"):
            print("Incorrect password!")

        # CREATE_TEAM
        elif response.startswith("1040"):
            print("Created team successfully!")
        elif response.startswith("2041"):
            print("Team name has existed!")
        elif response.startswith("2042"):
            print("Tên nhóm không tồn tại!")

        # SHOW_MY_TEAMS
        elif response.startswith("1050"):
            print("Showed my teams successfully!")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("1051"):
            print("You haven't attended any team!")

        # JOIN_TEAM
        elif response.startswith("1060"):
            print("Joined team successfully!")
        elif response.startswith("2061"):
            print("Wrong team code!")
        elif response.startswith("2062"):
            print("You have already joined this team!")

        # GET_JOIN_REQUEST
        elif response.startswith("1070"):
            print("Pending join requests:")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)

        # ACCEPT_JOIN_REQUEST
        elif response.startswith("1080"):
            print("Accepted join request successfully!")
        elif response.startswith("2081"):
            print("No pending requests!")

        # DECLINE_JOIN_REQUEST
        elif response.startswith("1090"):
            print("Declined join request successfully!")

        # GET_MEMBER
        elif response.startswith("1100"):
            print("Showed team member successfully!")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2101"):
            print("You are not a member of this team!")

        # QUIT_TEAM
        elif response.startswith("1110"):
            print("Quit team successfully")
        elif response.startswith("2111"):
            print("Leader can't quit team!")

        # REMOVE_MEMBER
        elif response.startswith("1120"):
            print("Removed member successfully!")
        elif response.startswith("2122"):
            print("Account doesn't exist!")
        elif response.startswith("2123"):
            print("You can't remove yourself!")

        # GET_ALL_USER
        elif response.startswith("1130"):
            print("Got all user successfully!")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)

        # INVITE_MEMBER
        elif response.startswith("1140"):
            print("Invited member successfully")
        elif response.startswith("2141"):
            print("Account doesn't exist!")
        elif response.startswith("2142"):
            print("Account has already been invited!")

        # GET_ALL_INVITATIONS
        elif response.startswith("1150"):
            print("Got all invitations successfully!")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2151"):
            print("No pending invitations!")

        # ACCEPT_INVITATION
        elif response.startswith("1160"):
            print("Accepted invitation successfully!")
        elif response.startswith("2161"):
            print("You do not have an invitation from this group!")

        # DECLINE_INVITATION
        elif response.startswith("1170"):
            print("Declined invitation successfully!")

        # FOLDER_INFORMATION
        elif response.startswith("1180"):
            print("Got folder information successfully!")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2181"):
            print("Folder doesn't exist!")
        elif response.startswith("2182"):
            print("Folder is empty!")

        # UPLOAD
        elif response.startswith("1190"):
            print("Uploaded file successfully!")

        # DOWNLOAD
        elif response.startswith("1200"):
            print("Downloaded file successfully!")
        elif response.startswith("2201"):
            print("File doesn't exist!")

        # RENAME_FILE
        elif response.startswith("1210"):
            print("Renamed file successfully!")
        elif response.startswith("2211"):
            print("Filename has existed!")
        elif response.startswith("2212"):
            print("Invalid filename!")
        elif response.startswith("2213"):
            print(
                "Filename has an extension that does not match the original file extension!"
            )
        elif response.startswith("2215"):
            print("File not found in root folder!")

        # DELETE_FILE
        elif response.startswith("1220"):
            print("Deleted file successfully!")

        # COPY_FILE
        elif response.startswith("1230"):
            print("Copied file successfully!")
        elif response.startswith("2231"):
            print("File has existed in destination folder!")
        elif response.startswith("2232"):
            print("Destination folder doesn't exist!")
        # MOVE_FILE
        elif response.startswith("1240"):
            print("Moved file successfully!")

        # CREATE_FOLDER
        elif response.startswith("1250"):
            print("Created folder successfully!")
        elif response.startswith("2251"):
            print("Folder has existed!")
        elif response.startswith("2252"):
            print("Invalid folder name!")

        # RENAME_FOLDER
        elif response.startswith("1260"):
            print("Renamed folder successfully")
        elif response.startswith("2261"):
            print("Folder doesn't exist!")
        elif response.startswith("2214"):
            print("You don't allowed to rename this folder!")

        # DELETE_FOLDER
        elif response.startswith("1270"):
            print("Deleted folder successfully!")

        # COPY_FOLDER
        elif response.startswith("1280"):
            print("Copied folder successfully!")
        elif response.startswith("2281"):
            print("Folder has existed in destination folder!")

        # MOVE_FOLDER
        elif response.startswith("1290"):
            print("Moved folder successfully!")

        # END
        elif response.startswith("3000"):
            print("Unknown message!")
        elif response.startswith("3001"):
            print("The message isn't in the correct format!")

        elif response.startswith("2321"):
            print("You have already logged in!")
        elif response.startswith("2322"):
            print("You haven't logged in yet!")
        elif response.startswith("1320"):
            print("Log out successfully!")

def main():
    global client
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        return
    IP = socket.gethostbyname(socket.gethostname())
    PORT = int(sys.argv[1])
    ADDR = (IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print(f"{data}")

    while True:
        data = input("> ")
        if len(data) == 0:
            break
        data = data.split("|")
        cmd = data[0]

        if cmd == "LOGIN":
            if len(data) != 3:
                print("Usage: LOGIN|<account>|<password>")
                continue
            else:
                login(client, data[1], data[2])
        elif cmd == "SIGNUP":
            if len(data) != 4:
                print("Usage: SIGNUP|<account>|<password>|<name>")
                continue
            else:
                signup(client, data[1], data[2], data[3])
        elif cmd == "CHANGE_PASSWORD":
            if len(data) != 4:
                print("Usage: CHANGE_PASSWORD|<password>|<new_password>|<cf_password>")
                continue
            else:
                change_password(client, data[1], data[2], data[3])
        elif cmd == "LOGOUT":
            if len(data) != 1:
                print("Usage: LOGOUT")
                continue
            else:
                logout(client)
        elif cmd == "SHOW_MY_TEAMS":
            if len(data) != 1:
                print("Usage: SHOW_MY_TEAMS")
                continue
            else:
                show_my_teams(client)
        elif cmd == "UPLOAD":
            if len(data) != 4:
                print("Usage: UPLOAD|<src_path>|<team_name>|<des_path>")
                continue
            else:
                upload_file(client, data[1], data[2], data[3])
        elif cmd == "DOWNLOAD":
            if len(data) != 4:
                print("Usage: DOWNLOAD|<team_name>|<src_path>|<des_path>")
                continue
            else:
                download_file(client, data[1], data[2], data[3])
        elif cmd == "GET_MEMBER":
            if len(data) != 2:
                print("Usage: GET_MEMBER|<team_name>")
                continue
            else:
                show_team_member(client, data[1])
        elif cmd == "CREATE_FOLDER":
            if len(data) != 4:
                print("Usage: CREATE_FOLDER|<team_name>|<des_path>|<name_folder>")
                continue
            else:
                create_directory(client, data[1], data[2], data[3])
        elif cmd == "RENAME_FOLDER":
            if len(data) != 5:
                print(
                    "Usage: RENAME_FOLDER|<team_name>|<des_path>|<name_folder>|<new_name_folder>"
                )
                continue
            else:
                rename_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "DELETE_FOLDER":
            if len(data) != 4:
                print("Usage: DELETE_FOLDER|<team_name>|<dir_path>|<dir_name>")
                continue
            else:
                delete_directory(client, data[1], data[2], data[3])
        elif cmd == "COPY_FOLDER":
            if len(data) != 5:
                print("Usage: COPY_FOLDER|<team_name>|<src_path>|<dir_name>|<des_path>")
                continue
            else:
                copy_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "MOVE_FOLDER":
            if len(data) != 5:
                print("Usage: MOVE_FOLDER|<team_name>|<src_path>|<dir_name>|<des_path>")
                continue
            else:
                move_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "QUIT_TEAM":
            if len(data) != 2:
                print("Usage: QUIT_TEAM|<team_name>")
                continue
            else:
                quit_team(client, data[1])
        elif cmd == "REMOVE_MEMBER":
            if len(data) != 3:
                print("Usage: REMOVE_MEMBER|<team_name>|<member_name>")
                continue
            else:
                remove_member(client, data[1], data[2])
        elif cmd == "GET_ALL_USER":
            if len(data) != 1:
                print("Usage: GET_ALL_USER")
                continue
            else:
                get_all_user(client)
        elif cmd == "INVITE_MEMBER":
            if len(data) != 3:
                print("Usage: INVITE_MEMBER|<team_name>|<member_name>")
                continue
            else:
                invite_member(client, data[1], data[2])
        elif cmd == "GET_ALL_INVITATIONS":
            if len(data) != 1:
                print("Usage: GET_ALL_INVITATIONS")
                continue
            else:
                get_all_invitations(client)
        elif cmd == "ACCEPT_INVITATION":
            if len(data) != 2:
                print("Usage: ACCEPT_INVITATION|<team_name>")
                continue
            else:
                accept_invitation(client, data[1])
        elif cmd == "DECLINE_INVITATION":
            if len(data) != 2:
                print("Usage: DECLINE_INVITATION|<team_name>")
                continue
            else:
                decline_invitation(client, data[1])
        elif cmd == "FOLDER_INFORMATION":
            if len(data) != 3:
                print("Usage: FOLDER_INFORMATION|<team_name>|<path>")
                continue
            else:
                dir_information(client, data[1], data[2])
        elif cmd == "JOIN_TEAM":
            if len(data) != 2:
                print("Usage: JOIN_TEAM|<team_code>")
                continue
            else:
                join_team(client, data[1])
        elif cmd == "CREATE_TEAM":
            if len(data) != 2:
                print("Usage: CREATE_TEAM|<team_name>")
                continue
            else:
                create_team(client, data[1])
        elif cmd == "GET_JOIN_REQUEST":
            if len(data) != 2:
                print("Usage: GET_JOIN_REQUEST|<team_name>")
                continue
            else:
                get_join_request(client, data[1])
        elif cmd == "ACCEPT_JOIN_REQUEST":
            if len(data) != 3:
                print("Usage: ACCEPT_JOIN_REQUEST|<team_name>|<sender>")
                continue
            else:
                accept_join_request(client, data[1], data[2])
        elif cmd == "DECLINE_JOIN_REQUEST":
            if len(data) != 3:
                print("Usage: DECLINE_JOIN_REQUEST|<team_name>|<sender>")
                continue
            else:
                decline_join_request(client, data[1], data[2])
        elif cmd == "DELETE_FILE":
            if len(data) != 4:
                print("Usage: DELETE_FILE|<team_name>|<dir_path>|<filename>")
                continue
            else:
                delete_file(client, data[1], data[2], data[3])
        elif cmd == "RENAME_FILE":
            if len(data) != 5:
                print(
                    "Usage: RENAME_FILE|<team_name>|<dir_path>|<old_file_name>|<new_file_name>"
                )
                continue
            else:
                rename_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "COPY_FILE":
            if len(data) != 5:
                print("Usage: COPY_FILE|<team_name>|<src_dir>|<filename>|<dest_dir>")
                continue
            else:
                copy_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "MOVE_FILE":
            if len(data) != 5:
                print("Usage: MOVE_FILE|<team_name>|<src_dir>|<filename>|<dest_dir>")
                continue
            else:
                move_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "QUIT":
            if len(data) != 1:
                print("Usage: QUIT")
                continue
            else:
                client.send(f"QUIT\r\n".encode(FORMAT))
                break
        else:
            send_data = "\n".join(data) + "\r\n"
            client.send(send_data.encode(FORMAT))

        responseFromServer(client)

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
