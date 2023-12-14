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
        <?php include "sidebar.php" ?>
      </div>



      <div class="col-10">
        <div class="header ml-5 mb-4">
          <div class="search-and-filter" style="display: inline-flex;">
            <div class="search-box" style="display: inline;">
              <button type="search"> <i class="material-icons"
                  style="vertical-align: middle; font-size: 24px;">search</i>
              </button>
              <input type="text" placeholder="Search team">
            </div>
            <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
              aria-expanded="false" id="filter-btn"><i class="material-icons"
                style="font-size:24px; vertical-align: middle;">filter_list</i></button>
            <ul class="dropdown-menu mt-2" style="width: 100px;">
              <li><a class="dropdown-item" id="filter-all" href="#">All<i class="fa-solid fa-check" style="float: right; margin-top: 3px;"></i></a></li>
              <li><a class="dropdown-item" id="filter-alpha" href="#">A-Z<i class="fa-solid fa-check" style="float: right; margin-top: 3px;"></i></a></li>
              <li><a class="dropdown-item" id="filter-reverse-alpha" href="#">Z-A<i class="fa-solid fa-check" style="float: right; margin-top: 3px;"></i></a></li>
            </ul>
          </div>

          <div class="dropdown-center btn-join-team" style="float: right;">
            <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
              aria-expanded="false">
              <i class="fa-solid fa-user-plus mr-3" style="display: inline;"></i>
              <p style="display: inline; font-size: 14px;">Join or create team</p>
            </button>
            <ul class="dropdown-menu mt-2" style="width: 237px;">
              <li><a class="dropdown-item" id="openPopupJoinTeamBtn" href="#">Join team with a code</a></li>
              <li><a class="dropdown-item" id="openPopupcreateTeamBtn" href="#">Create team</a></li>
            </ul>
          </div>
        </div>

        <!-- Container list team -->
        <div class="list-team">
          <div>
            <div class="row div-list-team">
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Network Programing</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Viet Nhat</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Tran Hong Quan</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Hoang Minh Nguyet</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Nguyen Hai Nam</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Team A</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Team B</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Team C</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Team D</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Network Programing</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Network Programing</h6>
              </a>
              <a href="team.php" class="col-2 team" style="margin-bottom: 34px; margin-right: 16px; margin-left: 18px;">
                <div class="team-element">
                  <div class="img-div"></div>
                </div>
                <br>
                <h6>Network Programing</h6>
              </a>

            </div>



          </div>
        </div>
      </div>
    </div>

    <!-- Popup Join team -->
    <div class="popup" id="joinTeamPopup">
      <div class="popup-content">
        <i class="fa-solid fa-users" style="font-size: 16px;"></i>
        <h5>Join team with a code</h5>
        <div style="display: inline-flex; margin-top: 20px;">
          <input type="text" placeholder="Code" class="code-team-inp">
          <button class="btn btn-success join-team-btn" style="background-color: #4D4D4D;">Join team</button>
        </div>

        <p class="p-message" id="p-message-code-team">Code team does not exist</p>
      </div>
    </div>

    <!-- Popup Create team -->
    <div class="popup" id="createTeamPopup">
      <div class="popup-content">
        <i class="fa-solid fa-users" style="font-size: 16px;"></i>
        <h5>Create your team</h5>
        <div class="div-create-team" style="display:flex; margin-top: 20px; flex-direction: column;">
          <input type="text" placeholder="Team name" class="create-team-inp">
          <input type="text" id="create-team-des" placeholder="Description" style="margin-bottom: 3px;">
          <p class="p-message" id="p-message-create-team">The team name already exists</p>
          <button class="btn btn-success next-btn create-team-btn"
            style="margin-left: auto; background-color: #4D4D4D; margin-top: 18px ">Next</button>
        </div>


      </div>
    </div>

</body>

</html>