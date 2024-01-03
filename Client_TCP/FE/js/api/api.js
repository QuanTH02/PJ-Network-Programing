
$(document).ready(function () {
    const BASE_URL = "http://127.0.0.1:5000/";

    

    // List folder
    $(".team").click(function (e) {
        e.preventDefault();
        $.get(BASE_URL + "api/get_all_user", function (data) {
            window.location.href = `team.php?data=${JSON.stringify(data)}`;
        });
    });
});
