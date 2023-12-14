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
        } else {
            document.querySelector('#p-message-create-team').style.display = "block";
        }
    });
});
