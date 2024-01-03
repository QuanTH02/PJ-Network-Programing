$(document).ready(function () {
    // Popup Join Team
    let openPopupJoinTeamBtn = document.getElementById("openPopupJoinTeamBtn");
    let joinTeamPopup = document.getElementById("joinTeamPopup");

    if (openPopupJoinTeamBtn && joinTeamPopup) {
        openPopupJoinTeamBtn.addEventListener("click", function () {
            joinTeamPopup.style.display = "block";
        });
    }

    if (joinTeamPopup) {
        joinTeamPopup.addEventListener("click", function (event) {
            if (event.target === this) {
                this.style.display = "none";
            }
        });
    }

    // Popup Create Team
    let openPopupCreateTeamBtn = document.getElementById("openPopupcreateTeamBtn");
    let createTeamPopup = document.getElementById("createTeamPopup");

    if (openPopupCreateTeamBtn && createTeamPopup) {
        openPopupCreateTeamBtn.addEventListener("click", function () {
            createTeamPopup.style.display = "block";
        });
    }

    if (createTeamPopup) {
        createTeamPopup.addEventListener("click", function (event) {
            if (event.target === this) {
                this.style.display = "none";
            }
        });
    }


    // Popup Add Member
    let skipBtn = document.querySelector('.skip-btn');
    let addMemberPopup = document.getElementById("addMemberPopup");

    if (skipBtn && addMemberPopup) {
        skipBtn.addEventListener("click", function () {
            addMemberPopup.style.display = "none";
        });
    }



    // Popup Join team
    let codeTeamInput = document.querySelector('.code-team-inp');
    let joinTeamBtn = document.querySelector('.join-team-btn');

    if (codeTeamInput) {
        codeTeamInput.addEventListener('input', function () {
            let inputValue = this.value.trim();

            if (inputValue === "") {
                joinTeamBtn.style.backgroundColor = "#4D4D4D";
            } else {
                joinTeamBtn.style.backgroundColor = "var(--color-bg-sidebar-li)";
            }
        });
    }


    let messageCodeTeam = document.querySelector('#p-message-code-team');

    if (joinTeamBtn) {
        joinTeamBtn.addEventListener('click', function () {
            let inputValue = codeTeamInput.value.trim();  // Loại bỏ các khoảng trắng từ đầu và cuối chuỗi

            if (inputValue === "123456") {
                console.log("Successfully entered");
                messageCodeTeam.style.display = "none";
            } else {
                messageCodeTeam.style.display = "block";
            }
        });
    }

    // Popup Create team
    let createTeamInput = document.querySelector('.create-team-inp');
    let createTeamBtn = document.querySelector('.create-team-btn');

    if (createTeamBtn) {
        createTeamInput.addEventListener('input', function () {
            let inputValue = this.value.trim();  // Loại bỏ các khoảng trắng từ đầu và cuối chuỗi

            if (inputValue === "") {
                createTeamBtn.style.backgroundColor = "#4D4D4D";
            } else {
                createTeamBtn.style.backgroundColor = "var(--color-bg-sidebar-li)";
            }
        });
    }

    let teamNameInput = document.querySelector('.create-team-inp');
    let messageCreateTeam = document.querySelector('#p-message-create-team');

    if (createTeamBtn) {
        createTeamBtn.addEventListener('click', function () {
            let inputValue = teamNameInput.value.trim();  // Loại bỏ các khoảng trắng từ đầu và cuối chuỗi
    
            if (inputValue === "123456") {
                console.log("Successfully entered");
                messageCreateTeam.style.display = "none";
                createTeamPopup.style.display = "none";
                addMemberPopup.style.display = "block";
            } else {
                messageCreateTeam.style.display = "block";
            }
        });
    }

    // Filter input
    document.querySelector('.search-box input').addEventListener('keyup', filterTeams);

    function filterTeams() {
        var input = document.querySelector('.search-box input');
        var filter = input.value.toUpperCase();
        var teams = document.querySelectorAll('.team');

        for (var i = 0; i < teams.length; i++) {
            var h6 = teams[i].querySelector('h6');
            if (h6) {
                var text = h6.textContent || h6.innerText;
                if (text.toUpperCase().indexOf(filter) > -1) {
                    teams[i].style.display = '';
                } else {
                    teams[i].style.display = 'none';
                }
            }
        }
    }

    // Background filter transparent and check none
    function bgFilterTransparent() {
        var ulFilterTeam = document.querySelector(".ul-filter-team"); // Sử dụng querySelector để lấy phần tử cụ thể
        var liElements = ulFilterTeam.querySelectorAll("li");

        liElements.forEach(function (liElement) {
            var aElementsInLi = liElement.querySelectorAll("a");

            aElementsInLi.forEach(function (aElement) {
                var iElementsInA = aElement.querySelectorAll("i");

                iElementsInA.forEach(function (iElement) {
                    iElement.style.display = "none";
                });

                aElement.style.backgroundColor = "transparent";
            });
        });
    }

    // Filter All
    // Lắng nghe sự kiện click vào thẻ "filter-all"
    var initialTeamList = [];

    document.getElementById('filter-all').addEventListener('click', function (event) {
        event.preventDefault(); // Ngăn chặn trang web chuyển hướng khi click vào thẻ "filter-all"
        bgFilterTransparent();
        document.getElementById('filter-all').style.backgroundColor = '#5A5A72';
        document.getElementById('check-filter-all').style.display = "block";
        // Lấy danh sách các phần tử ".team"
        var teams = document.querySelectorAll('.team');

        // Lấy danh sách ban đầu từ một biến đã lưu trữ

        // Hiển thị lại danh sách ban đầu
        teams.forEach(function (team, index) {
            if (initialTeamList[index]) {
                team.style.display = initialTeamList[index].style.display;
            } else {
                team.style.display = ''; // Nếu không có trong danh sách ban đầu, hiển thị lại
            }
        });
    });

    // Filter A -> Z
    // Lắng nghe sự kiện click vào thẻ "filter-alpha"
    document.getElementById('filter-alpha').addEventListener('click', function (event) {
        event.preventDefault(); // Ngăn chặn trang web chuyển hướng khi click vào thẻ "filter-alpha"
        bgFilterTransparent();

        document.getElementById('filter-alpha').style.backgroundColor = '#5A5A72';
        document.getElementById('check-filter-alpha').style.display = "block";
        // Lấy danh sách các phần tử ".team"
        var teams = document.querySelectorAll('.team');

        // Chuyển NodeList thành mảng để có thể sử dụng phương thức sort()
        var teamsArray = Array.from(teams);

        // Sắp xếp lại các phần tử theo thứ tự A đến Z dựa vào nội dung của thẻ "h6"
        teamsArray.sort(function (a, b) {
            var textA = a.querySelector('h6').textContent.toUpperCase();
            var textB = b.querySelector('h6').textContent.toUpperCase();
            if (textA < textB) {
                return -1;
            }
            if (textA > textB) {
                return 1;
            }
            return 0;
        });

        // Xóa các phần tử hiện tại trong ".div-list-team"
        var divListTeam = document.querySelector('.div-list-team');
        divListTeam.innerHTML = '';

        // Thêm lại các phần tử đã được sắp xếp
        teamsArray.forEach(function (team) {
            divListTeam.appendChild(team);
        });
    });

    // Filter Z -> A
    // Lắng nghe sự kiện click vào thẻ "filter-reverse-alpha"
    document.getElementById('filter-reverse-alpha').addEventListener('click', function (event) {
        event.preventDefault(); // Ngăn chặn trang web chuyển hướng khi click vào thẻ "filter-reverse-alpha"
        bgFilterTransparent();
        document.getElementById('filter-reverse-alpha').style.backgroundColor = '#5A5A72';
        document.getElementById('check-filter-reverse-alpha').style.display = "block";
        // Lấy danh sách các phần tử ".team"
        var teams = document.querySelectorAll('.team');

        // Chuyển NodeList thành mảng để có thể sử dụng phương thức sort()
        var teamsArray = Array.from(teams);

        // Sắp xếp lại các phần tử theo thứ tự ngược từ Z đến A dựa vào nội dung của thẻ "h6"
        teamsArray.sort(function (a, b) {
            var textA = a.querySelector('h6').textContent.toUpperCase();
            var textB = b.querySelector('h6').textContent.toUpperCase();
            if (textA > textB) {
                return -1;
            }
            if (textA < textB) {
                return 1;
            }
            return 0;
        });

        // Xóa các phần tử hiện tại trong ".div-list-team"
        var divListTeam = document.querySelector('.div-list-team');
        divListTeam.innerHTML = '';

        // Thêm lại các phần tử đã được sắp xếp
        teamsArray.forEach(function (team) {
            divListTeam.appendChild(team);
        });
    });

});
