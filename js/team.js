$(document).ready(function () {
    // Popup Add Member
    document.getElementById("add-member-btn").addEventListener("click", function () {
        document.getElementById("addMemberPopupInvite").style.display = "block";
    });

    document.getElementById("addMemberPopupInvite").addEventListener("click", function (event) {
        if (event.target === this) {
            var divInviteMember = document.querySelectorAll('.name-add');
            divInviteMember.forEach(function (divInviteMember) {
                divInviteMember.innerHTML = "";
            });
            this.style.display = "none";
        }
    });

    // Tắt Popup Invite và hiển thị successfully
    document.querySelector('.invite-btn').addEventListener('click', function () {
        document.getElementById("addMemberPopupInvite").style.display = "none";
        document.getElementById("inviteSentSuccessPopup").style.display = "block";

        setTimeout(function () {
            document.getElementById("inviteSentSuccessPopup").style.display = "none";
        }, 1000);
    });

    // Hover div and close icon
    // Lấy tham chiếu đến input và button
    const teamCodeInput = document.getElementById("teamCode");
    const copyButton = document.getElementById("copyButton");

    teamCodeInput.addEventListener("mouseover", function () {
        copyButton.style.display = "block";
    });

    teamCodeInput.addEventListener("mouseout", function () {
        // Ẩn button khi di chuột ra khỏi input
        copyButton.style.display = "none";
    });

    var nameExitList;
    nameExitList = document.querySelectorAll('.name-exit');

    nameExitList.forEach(function (nameExit) {
        var faXmark = nameExit.querySelector('.fa-xmark');

        nameExit.addEventListener('mouseenter', function () {
            faXmark.style.opacity = 1;
        });

        nameExit.addEventListener('mouseleave', function () {
            faXmark.style.opacity = 0;
        });
    });


    // Test

    var inputElement = document.getElementById('add-member-invite-member-inp-team');
    var dropdownList = document.getElementById('dropdown-list-team');
    var userNames = ["User1", "User2", "User3", "Tran Hong Quan 20205114"]; // Thay thế bằng danh sách tên người dùng thực tế

    inputElement.addEventListener('input', function () {
        var inputValue = inputElement.value.toLowerCase();
        var divInviteMember = document.querySelectorAll('.name-add');
        dropdownList.innerHTML = ''; // Xóa danh sách dropdown cũ

        // Tìm và hiển thị các gợi ý
        userNames.forEach(function (userName) {
            if (userName.toLowerCase().includes(inputValue)) {
                var listItem = document.createElement('li');
                listItem.textContent = userName;

                // Click chuột vào 1 thẻ li
                listItem.addEventListener('click', function () {
                    var nameDiv = document.createElement('div');
                    nameDiv.classList.add('name-exit');

                    var nameInviteDiv = document.createElement('div');
                    nameInviteDiv.classList.add('name-invite');
                    nameInviteDiv.textContent = userName;

                    var xIcon = document.createElement('i');
                    xIcon.classList.add('fa-solid', 'fa-xmark');
                    xIcon.style.marginTop = '6px';
                    xIcon.style.marginLeft = '-11px';

                    nameDiv.appendChild(nameInviteDiv);
                    nameDiv.appendChild(xIcon);

                    inputElement.value = "";

                    divInviteMember.forEach(function (divInviteMember) {
                        divInviteMember.appendChild(nameDiv);
                    });

                    nameExitList = document.querySelectorAll('.name-exit');

                    nameExitList.forEach(function (nameExit) {
                        var faXmark = nameExit.querySelector('.fa-xmark');

                        nameExit.addEventListener('mouseenter', function () {
                            faXmark.style.opacity = 1;
                        });

                        nameExit.addEventListener('mouseleave', function () {
                            faXmark.style.opacity = 0;
                        });

                        faXmark.addEventListener('click', function () {
                            nameExit.remove();
                        });

                    });

                    // Sự kiện click chuột ra ngoài thì ul biến mất và ngược lại
                    document.addEventListener("click", function (e) {
                        if (!inputElement.contains(e.target) && !dropdownList.contains(e.target)) {
                            dropdownList.style.display = "none";
                        } else {
                            if (dropdownList.innerHTML != "") {
                                dropdownList.style.display = "block";
                            } else {
                                dropdownList.style.display = "none";
                            }
                        }
                    });


                    dropdownList.innerHTML = ''; // Đóng dropdown sau khi chọn
                    dropdownList.style.display = "none";
                });

                // Kiểm tra xem listItem có rỗng hay không
                if (listItem.textContent.trim() !== "") {
                    dropdownList.appendChild(listItem); // Append listItem vào dropdownList
                }


            }

            // Sau khi kiểm tra xong, kiểm tra số lượng phần tử con bên trong dropdownList
            if (dropdownList.children.length > 0) {
                dropdownList.style.display = "block"; // Hiển thị dropdownList
            } else {
                dropdownList.style.display = "none"; // Ẩn dropdownList
            }
        });
    });


    // Block Members and Block Pending and Block navbar
    var navBarMembers = document.querySelectorAll('.nav-bar-member');

    navBarMembers.forEach(function (navBarMember) {
        var aElements = navBarMember.querySelectorAll("a");

        aElements.forEach(function (aElement) {
            aElement.addEventListener('click', function (event) {
                event.preventDefault();

                // Loại bỏ borderBottom từ tất cả các thẻ <a> trong cùng một .nav-bar-member
                aElements.forEach(function (element) {
                    element.style.borderBottom = "none";
                });

                // Áp dụng borderBottom cho thẻ <a> hiện tại
                aElement.style.borderBottom = "3px solid var(--color-bg-sidebar-li)";

                // Kiểm tra nội dung của thẻ <h6>
                var h6Element = aElement.querySelector('h6');

                if (h6Element && h6Element.textContent === "Members") {
                    // Nếu nội dung của thẻ <h6> là "Members", hiển thị .members
                    document.querySelector('#members').style.display = "block";
                    document.querySelector('#pending-requests').style.display = "none";
                } else {
                    // Nếu không, hiển thị .pending-requests
                    document.querySelector('#members').style.display = "none";
                    document.querySelector('#pending-requests').style.display = "block";
                }
            });
        });
    });

    const clickMemberPending = document.getElementById("click-member-pending");
    clickMemberPending.addEventListener("click", function () {
        document.getElementById("id-list-folder").style.display = "none";
        document.getElementById("id-nav-bar-member").style.display = "flex";
        document.getElementById("list-member-pending").style.display = "block";
        getTotalPending();

        // Đặt thuộc tính href cho phần tử có lớp là "back-to-home"
        const backToHome = document.getElementsByClassName("back-to-home")[0];
        backToHome.href = "team.php";


    });


    function getTotalPending() {
        var trElements = document.querySelectorAll('#pending-requests tr');
        var totalCount = trElements.length;
        totalCount--;
        var totalPendingRequestElement = document.querySelector('.total-pending-request');
        totalPendingRequestElement.textContent = totalCount.toString();
    }

    // Remove folder and remove file
    var iconRemoves = document.getElementsByClassName("icon-remove");
    var iconArray = Array.from(iconRemoves);

    iconArray.forEach(function (iconRemove) {
        iconRemove.addEventListener("click", function () {
            document.getElementById("doYouWantToDeleted").style.display = "block";
            var yesButtons = document.getElementsByClassName("yes-btn");
            var yesButtonArray = Array.from(yesButtons);

            yesButtonArray.forEach(function (yesButton) {
                yesButton.addEventListener("click", function () {
                    document.getElementById("doYouWantToDeleted").style.display = "none";
                    document.getElementById("folderDeletedPopup").style.display = "block";

                    setTimeout(function () {
                        document.getElementById("folderDeletedPopup").style.display = "none";
                    }, 1000);
                });
            });
        });
    });




});