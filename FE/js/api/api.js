
$(document).ready(function () {
    const BASE_URL = "http://127.0.0.1:5000/";

    // Login
    document.addEventListener("DOMContentLoaded", function () {
        const signInButton = document.querySelector(".submit-account-password");

        signInButton.addEventListener("click", function () {
            const account = document.querySelector(".input-enter-account").value;
            const password = document.querySelector(".input-enter-password").value;

            // Gửi yêu cầu POST đến server
            fetch(BASE_URL + "api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ account: account, password: password })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Login successful") {
                        // Chuyển hướng đến trang home.php
                        window.location.href = "home.php";
                    } else {
                        // Hiển thị thông báo lỗi
                        alert(data.error);
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("An error occurred while logging in.");
                });
        });
    });

    // List folder
    $(".team").click(function (e) {
        e.preventDefault();
        $.get(BASE_URL + "api/get_all_user", function (data) {
            window.location.href = `team.php?data=${JSON.stringify(data)}`;
        });
    });
});
