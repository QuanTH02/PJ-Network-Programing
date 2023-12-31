<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Movie Website</title>

    <link href='https://fonts.googleapis.com/css?family=Poppins' rel='stylesheet'>


    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

    <link rel="stylesheet" href="templates/home.css">


    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.10.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="js/home.js"></script>
    <script src="js/team.js"></script>

    <link href="https://getbootstrap.com/docs/5.3/assets/css/docs.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</head>

<body>
    <div class="sidebar">
        <div class="row mr-0">
            <div class="col-2 col-sidebar pl-4" style="height: 100vh; ">
                <?php include "sidebar.php"; ?>
            </div>

            <div class="col-10">
                <div class="header ml-5 mb-4">
                    <div style="display: flex; flex-direction: column;">
                        <a href="home.php" class="back-to-home">
                            <i class="fa-solid fa-angle-left" style="display: inline; margin-right: 10px;"></i>
                            <h5 style="display: inline;">Back</h5>
                        </a>

                        <div class="team-component" style="display: flex;">
                            <div class="div-team-img" style="display: inline;"></div>
                            <div class="team-right-img" style="display: inline;">
                                <h4>Network Programing</h4>
                                <div class="team-bottom-name" style="display: flex;">
                                    <div style="width: 100%; display: flex; ">
                                        <div class="member-plus-icon" style="display: flex;">
                                            <a id="click-member-pending" href="#" style="display: flex;">
                                                <p class="num-member" style="margin-right: 5px;">27</p>
                                                <p style="margin-right: 20px;">members</p>
                                            </a>

                                            <!-- If Member -->
                                            <!-- <button id="add-member-btn"><i class="fa-solid fa-right-from-bracket"></i></button> -->

                                            <!-- If Leader -->
                                            <button id="add-member-btn"><i class="fa-solid fa-user-plus"></i></button>

                                        </div>


                                        <div class="upload-and-new-folder" style="margin-left: auto;">
                                            <button class="upload-btn">
                                                <div class="upload">
                                                    <i class="fa-solid fa-upload"></i>
                                                    <p>Upload</p>
                                                </div>
                                            </button>

                                            <button class="new-folder-btn">
                                                <div class="new-folder">
                                                    <i class="fa-solid fa-folder-open"></i>
                                                    <p>New folder</p>
                                                </div>
                                            </button>

                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="nav-bar-member" id="id-nav-bar-member" style="display: none;">
                            <a href="#" style="border-bottom: 3px solid var(--color-bg-sidebar-li);">
                                <h6>Members</h6>
                            </a>
                            <a href="#" style="display: flex;">
                                <h6>Pending requests</h6>
                                <p class="total-pending-request"></p>
                            </a>
                        </div>
                    </div>

                </div>

                <!-- Container list team -->
                <div class="list-folder" id="id-list-folder">
                    <!-- <div class="row table-folder" style="width: 100%; height: 100%; justify-content: space-between; padding-left: 25px;">
                        <div class="col-1 icon-folder"></div>
                        <div class="col-2 name"></div>
                        <div class="col-2 none-col"></div>
                        <div class="col-2 modified"></div>
                        <div class="col-2 modified-by"></div>
                        <div class="col-2 edit-remove"></div>
                    </div> -->

                    <table style="width: 91.8%; margin-left: 3.8%;">
                        <!-- Title -->
                        <tr>
                            <td class="table-img-folder"></td>
                            <td class="table-name-folder" style="font-size: 12px;">Name <button class="icon-down"><i
                                        class="fa-solid fa-chevron-down"></i></button></td>
                            <td class="table-copy-move-download"></td>
                            <td class="table-modified" style="font-size: 12px;">Modified <button class="icon-down"><i
                                        class="fa-solid fa-chevron-down"></i></button></td>
                            <td class="table-modified-by" style="font-size: 12px;">Modified by<button
                                    class="icon-down"><i class="fa-solid fa-chevron-down"></i></button></td>
                            <td class="table-edit"></td>
                            <td class="table-remove"></td>
                        </tr>

                        <!-- Content -->
                        <?php
                        $userData = json_decode($_GET['data'], true);
                        ?>

                            <!-- Các tiêu đề của bảng -->
                            <!-- ... -->
                            <!-- Các dòng trong bảng sẽ được thêm vào đây -->
                            <?php foreach ($userData as $user): ?>
                                <tr class="tr-folder-list">
                                    <td class="table-img-folder"><i class="fa-regular fa-file"></i></td>
                                    <td class="table-name-folder">
                                        Main folder
                                    </td>
                                    <td class="table-copy-move-download">
                                        <button class="folder-copy"><i class="fa-regular fa-copy"></i></button>
                                        <button class="folder-download"><i class="fa-solid fa-download"></i></button>
                                        <button class="folder-move"><img src="img/move-folder.svg" alt=""></button>
                                    </td>
                                    <td class="table-modified">Oct 10, 2023</td>
                                    <td class="table-modified-by">
                                        <?= $user['account'] ?>
                                    </td>
                                    <td class="table-edit"><button class="icon-edit"><i
                                                class="fa-regular fa-pen-to-square"></i></button></td>
                                    <td class="table-remove"><button class="icon-remove"><i class="fa fa-trash-o"
                                                style="font-size:16px;"></i></button></td>
                                </tr>
                            <?php endforeach; ?>



                    </table>
                </div>

                <!-- Pending requests -->
                <div id="pending-requests" style="display: none; height: 360px;">
                    <table style="width: 91.8%; margin-left: 3.8%;">
                        <!-- Title -->
                        <tr>
                            <td class="table-img-folder"></td>
                            <td class="table-name-member-invite" style="font-size: 12px;">Name <button
                                    class="icon-down"><i class="fa-solid fa-chevron-down"></i></button></td>
                            <td class="table-invite-date" style="font-size: 12px;">Date <button class="icon-down"><i
                                        class="fa-solid fa-chevron-down"></i></button></td>
                            <td class="table-accept"></td>
                            <td class="table-decline"></td>
                        </tr>
                        <!-- Content -->
                        <tr class="tr-folder-list">
                            <td class="table-img-folder"><img src="img/vebinh1.jpg" alt="Img"></td>
                            <td class="table-name-member-invite">Username</td>
                            <td class="table-invite-date">Oct 10, 2023</td>
                            <td class="table-accept"><button class="icon-table-accept"><i
                                        class="fa-solid fa-check"></i></button></td>
                            <td class="table-decline"><button class="icon-table-decline"><i class="fa-solid fa-xmark"
                                        style="opacity: 1;"></i></button></td>
                        </tr>
                        <tr class="tr-folder-list">
                            <td class="table-img-folder"><img src="img/vebinh1.jpg" alt="Img"></td>
                            <td class="table-name-member-invite">Username</td>
                            <td class="table-invite-date">Oct 10, 2023</td>
                            <td class="table-accept"><button class="icon-table-accept"><i
                                        class="fa-solid fa-check"></i></button></td>
                            <td class="table-decline"><button class="icon-table-decline"><i class="fa-solid fa-xmark"
                                        style="opacity: 1;"></i></button></td>
                        </tr>
                        <tr class="tr-folder-list">
                            <td class="table-img-folder"><img src="img/vebinh1.jpg" alt="Img"></td>
                            <td class="table-name-member-invite">Username</td>
                            <td class="table-invite-date">Oct 10, 2023</td>
                            <td class="table-accept"><button class="icon-table-accept"><i
                                        class="fa-solid fa-check"></i></button></td>
                            <td class="table-decline"><button class="icon-table-decline"><i class="fa-solid fa-xmark"
                                        style="opacity: 1;"></i></button></td>
                        </tr>
                        <tr class="tr-folder-list">
                            <td class="table-img-folder"><img src="img/vebinh1.jpg" alt="Img"></td>
                            <td class="table-name-member-invite">Username</td>
                            <td class="table-invite-date">Oct 10, 2023</td>
                            <td class="table-accept"><button class="icon-table-accept"><i
                                        class="fa-solid fa-check"></i></button></td>
                            <td class="table-decline"><button class="icon-table-decline"><i class="fa-solid fa-xmark"
                                        style="opacity: 1;"></i></button></td>
                        </tr>
                        <tr class="tr-folder-list">
                            <td class="table-img-folder"><img src="img/vebinh1.jpg" alt="Img"></td>
                            <td class="table-name-member-invite">Username</td>
                            <td class="table-invite-date">Oct 10, 2023</td>
                            <td class="table-accept"><button class="icon-table-accept"><i
                                        class="fa-solid fa-check"></i></button></td>
                            <td class="table-decline"><button class="icon-table-decline"><i class="fa-solid fa-xmark"
                                        style="opacity: 1;"></i></button></td>
                        </tr>


                    </table>
                </div>

            </div>

        </div>
    </div>
    </div>

    <!-- Popup Add Member -->
    <div class="popup" id="addMemberPopupInvite">
        <div class="popup-content">
            <i class="fa-solid fa-users" style="font-size: 16px;"></i>
            <h5>Add members</h5>
            <div class="div-add-member" style="display:flex; margin-top: 20px; flex-direction: column;">
                <div class="add-member-team-code" style="display: flex;">
                    <div class="team-code" style="display: flex;" id="teamCode">
                        <input type="text" placeholder="123456" readonly>
                        <button id="copyButton"><i class="fa-regular fa-copy"></i></button>
                    </div>
                    <button class="refresh-btn"><i class="fa-solid fa-rotate-left"></i></button>
                </div>
                <p>Share this code so people can join the team directly</p>

                <!-- Add member -->
                <div class="add-member-invite-member" style="display: flex; ">
                    <div class="div-invite-member">
                        <div class="name-add" style="display: flex;">

                        </div>

                        <div class="div-invite-inp">
                            <input type="text" id="add-member-invite-member-inp-team" placeholder="Invite member">
                            <ul id="dropdown-list-team" style="position: absolute;"></ul>
                        </div>
                    </div>

                </div>
                <br>
                <button class="btn btn-success invite-btn" style="margin-left: auto; width: 100px;">Invite</button>
            </div>
        </div>
    </div>

    <!-- Popup Create new Folder -->
    <div class="popup" id="createFolderPopup">
        <div class="popup-content">
            <i class="fa-solid fa-folder" style="font-size: 24px;"></i>
            <h5>Create new folder</h5>
            <div class="div-add-member" style="display:flex; margin-top: 20px; flex-direction: column;">
                <!-- Add member -->
                <div class="add-member-invite-member" style="display: flex; ">
                    <div class="div-invite-member">
                        <div class="name-add" style="display: flex;">

                        </div>

                        <div class="div-invite-inp">
                            <input type="text" id="---" placeholder="Folder name">
                            <ul id="---" style="position: absolute;"></ul>
                        </div>
                    </div>

                </div>

                <br>
                <div class="btn-cancel-and-invite" style="display: flex;">
                    <button class="btn btn-success invite-btn" style="margin-left: auto; width: 100px;">Cancel</button>
                    <button class="btn btn-success invite-btn" style="margin-left: auto; width: 100px;">Invite</button>
                </div>
            </div>
        </div>
    </div>



    <!-- Notification -->

    <!-- Do you want to delete the folder? -->
    <div class="popup" id="doYouWantToDeleted">
        <div class="popup-content popup-border-bot" style="padding: 5px 20px;">
            <div style="display: flex;" class="deleted">
                <h6>Do you want to delete the folder?</h6>
            </div>
            <div class="yesNoPopup" style="width: 80%; margin-left: 9%; display: flex; justify-content: space-between;">
                <button class="yes-btn">Yes</button>
                <button class="no-btn">No</button>
            </div>
        </div>
    </div>

    <!-- Folder delete  -->
    <div class="popup" id="folderDeletedPopup">
        <div class="popup-content popup-border-bot" style="padding: 5px 20px;">
            <div style="display: flex;" class="deleted">
                <i class="fa-solid fa-check"></i>
                <h6>The folder ... was deleted</h6>
            </div>
        </div>
    </div>

    <!-- File delete  -->
    <div class="popup" id="fileDeletedPopup">
        <div class="popup-content popup-border-bot" style="padding: 5px 20px;">
            <div style="display: flex;" class="deleted">
                <i class="fa-solid fa-check"></i>
                <h6>The file ... was deleted</h6>
            </div>
        </div>
    </div>

    <!-- Invitations sent successfully  -->
    <div class="popup" id="inviteSentSuccessPopup">
        <div class="popup-content popup-border-bot" style="padding: 5px 20px;">
            <div style="display: flex;" class="deleted">
                <i class="fa-solid fa-check"></i>
                <h6>Invitations sent successfully</h6>
            </div>
        </div>
    </div>

    <!-- Folder created successfully  -->
    <div class="popup" id="folderCreateSuccessPopup">
        <div class="popup-content popup-border-bot" style="padding: 5px 20px;">
            <div style="display: flex;" class="deleted">
                <i class="fa-solid fa-check"></i>
                <h6>Folder created successfully</h6>
            </div>
        </div>
    </div>

</body>

</html>