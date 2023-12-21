$(document).ready(function () {
    // Popup Join Team
    document.getElementById("openPopupJoinTeamBtn").addEventListener("click", function () {
        document.getElementById("joinTeamPopup").style.display = "block";
    });

    document.getElementById("joinTeamPopup").addEventListener("click", function (event) {
        if (event.target === this) {
            this.style.display = "none";
        }
    });

    // Popup Create Team
    document.getElementById("openPopupcreateTeamBtn").addEventListener("click", function () {
        document.getElementById("createTeamPopup").style.display = "block";
    });

    document.getElementById("createTeamPopup").addEventListener("click", function (event) {
        if (event.target === this) {
            this.style.display = "none";
        }
    });

    // Popup Add Member
    document.querySelector('.skip-btn').addEventListener("click", function () {
        document.getElementById("addMemberPopup").style.display = "none";
    });


    // Popup Join team
    document.querySelector('.code-team-inp').addEventListener('input', function () {
        var inputValue = this.value.trim(); // Trim để loại bỏ các khoảng trắng

        var joinTeamBtn = document.querySelector('.join-team-btn');
        if (inputValue === "") {
            joinTeamBtn.style.backgroundColor = "#4D4D4D";
        } else {
            joinTeamBtn.style.backgroundColor = "var(--color-bg-sidebar-li)";
        }
    });

    document.querySelector('.join-team-btn').addEventListener('click', function () {
        var codeTeam = document.querySelector('.code-team-inp');
        var inputValue = codeTeam.value;
        if (inputValue == "123456") {
            console.log("Successfully entered");
            document.querySelector('#p-message-code-team').style.display = "none";
        } else {
            document.querySelector('#p-message-code-team').style.display = "block";
        }
    });

    // Popup Create team
    document.querySelector('.create-team-inp').addEventListener('input', function () {
        var inputValue = this.value.trim(); // Trim để loại bỏ các khoảng trắng

        var nextBtn = document.querySelector('.create-team-btn');
        if (inputValue === "") {
            nextBtn.style.backgroundColor = "#4D4D4D";
        } else {
            nextBtn.style.backgroundColor = "var(--color-bg-sidebar-li)";
        }
    });

    document.querySelector('.create-team-btn').addEventListener('click', function () {
        var teamName = document.querySelector('.create-team-inp');
        var inputValue = teamName.value;
        if (inputValue == "123456") {
            console.log("Successfully entered");
            document.querySelector('#p-message-create-team').style.display = "none";
            document.getElementById("createTeamPopup").style.display = "none";
            document.getElementById("addMemberPopup").style.display = "block";

        } else {
            document.querySelector('#p-message-create-team').style.display = "block";
        }
    });

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
