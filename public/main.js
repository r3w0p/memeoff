$(function() {

  /* CONSTANTS */

  const CONNECTION          = 'connection';
  const DISCONNECT          = 'disconnect';
  const RECONNECT           = 'reconnect';
  const RECONNECT_ERROR     = 'reconnect_error';
  const LOGIN_REQUEST       = 'login_request';
  const LOGIN_FAILURE       = 'login_failure';
  const LOGIN_SUCCESS       = 'login_success';
  const USER_JOINED         = 'user_joined';
  const USER_LEFT           = 'user_left';
  const USER_SUBMISSION     = 'user_submission';
  const SUBMISSION_RECEIVED = 'submission_received';
  const SUBMISSION_COUNT    = 'submission_count';
  const USER_SKIP           = 'user_skip';
  const SKIP_COUNT          = 'skip_count';
  const TRANSITION          = 'transition';
  const NEW_IMAGE           = 'new_image';

  const LOGGING = true;

  const PLAYERS = "PLAYERS";
  const START   = "START";
  const SUBMIT  = "SUBMIT";
  const VOTE    = "VOTE";
  const WINNER  = "WINNER";

  const STATES = {
      PLAYERS: $('#game-area-players'),
      START:   $('#game-area-start'),
      SUBMIT:  $('#game-area-submit'),
      VOTE:    $('#game-area-vote'),
      WINNER:  $('#game-area-winner')
  };


  /* VARIABLES */

  // Login
  let $loginPage = $('#login-page');
  let $loginUsernameInput = $('#input-username');
  let $loginErrorMessage = $("#login-page-error");

  // Game
  let $gamePage = $('#game-page');
  let gameCurrentState = "";

  // Navbar
  let $navbarTimer = $('#nav-timer');
  let $navbarLogo = $('#nav-logo');
  let $navbarPlayerListText = $("#player-list-text");
  let $navbarPlayerList = $("#player-list");
  let navbarTimerSeconds = -1;

  // Submit
  let $gameSubmitInput = $('#input-game');
  let $gameSubmitSend = $('#input-game-submit');
  let $gameSubmitSkip = $('#input-game-skip');
  let $gameSubmitImgContainer = $('#submit-image-container');
  let gameCurrentImage = "";

  // Vote
  let $gameVoteCardContainer = $('#vote-card-container');

  // Other
  let $window = $(window);
  let $inputCurrent = $loginUsernameInput.focus();

  let waitingForLoginResponse = false;
  let username = "";
  let auth = false;
  let usernames = new Set();
  let socket = io();




  /* TOOLS */

  setInterval(function() {
    if (!username) return;

    if (auth) {
      if (navbarTimerSeconds > -1)
        navbarTimerSeconds -= 1;

      $navbarTimer.html(navbarTimerSeconds > -1 ? navbarTimerSeconds + "..." : "...", true);
    } else
      $navbarTimer.html("😵", false);
  }, 1000);

  // Refresh the names in the player list
  const refreshPlayerList = () => {
    let arr_usernames = Array.from(usernames).sort();
    let li_str = "";

    arr_usernames.forEach(function (item, index) {
      li_str += '<li class="menu-item nav-text">' + item + '</li>'
    });

    $navbarPlayerListText.html(arr_usernames.length > 10 ? "10+" : arr_usernames.length);
    $navbarPlayerList.html(li_str);
  };

  const log = (message) => {
    if (LOGGING)
      console.log(message);
  };

  // Prevents input from having injected markup
  const cleanInput = (input) => {
    return $('<div/>').text(input).html();
  };




  /* LOGIN */

  // Sends a chat message
  const sendLoginRequest = () => {
    let clean_username = cleanInput($loginUsernameInput.val().trim());

    if (clean_username)
      socket.emit(LOGIN_REQUEST, clean_username);
    else
      $loginErrorMessage.html("Invalid username.");
  };

  // Sets the client's username
  const removeLoginPage = () => {
    if (username) {
      $loginPage.off('click');
      $gamePage.show();
      $loginPage.fadeOut();
      $inputCurrent = $gameSubmitInput.focus();
    }
  };




  /* GAME */

  const resetGame = () => {
    // TODO reset all game variables
    resetNavbar();
    resetSubmit();
    resetVote();
  };


  const resetNavbar = () => {
    $navbarTimer.html("");
    navbarTimerSeconds = -1;
  };


  const resetSubmit = () => {
    // Text box
    $gameSubmitInput.prop('disabled', false);
    $gameSubmitInput.val("");

    // Send button
    $gameSubmitSend.removeClass('disabled');
    $gameSubmitSend.attr('data-badge', "0");

    // Skip button
    $gameSubmitSkip.removeClass('disabled');
    $gameSubmitSkip.attr('data-badge', "0");

    // Image
    $gameSubmitImgContainer.html("");
    gameCurrentImage = "";
  };

  const resetVote = () => {
    // TODO
    $gameVoteCardContainer.html("");
  }


  // Sends a chat message
  const sendUserSubmission = () => {
    if(!username) return;

    let text = cleanInput($gameSubmitInput.val().trim());

    if (text && auth) {
      socket.emit(USER_SUBMISSION, {
        username: username,
        text: text
      });
    }
  };

  const setGameImage = (image) => {
    gameCurrentImage = image;

    if(gameCurrentImage)
      $gameSubmitImgContainer.html(
          $('<img>',{
            class: 'img-responsive',
            src: gameCurrentImage,
            width: '100%'
          })
      );
    else
      $gameSubmitImgContainer.html("");
  };

  const addVoteCard = (sub_id, title) => {
    $gameVoteCardContainer.append(
        $('<div>', {
          class: 'column col-4 col-xl-12 memecard vote'
        }).html(
            $('<div>', {
              class: 'card shadow'
            }).html(
                $('<div>', {
                  class: 'card-header'
                }).html(
                    $('<div>', {
                      class: 'card-title h3 text'
                    }).html(title)
                )
            ).append(
                $('<div>', {
                  class: 'card-image image'
                }).html(
                    $('<img>',{
                      class: 'img-responsive',
                      src: gameCurrentImage,
                      width: '100%'
                    })
                )
            ).append(
                $('<div>', {
                  class: 'card-footer memereact-container'
                }).html(
                    $('<table>').html(
                        $('<td>').html(
                            $('<button>', {
                              class: 'btn btn-link memereact'
                            }).html('😍').attr('data-sub-id', sub_id).attr('data-react', 'love')
                        ).append(
                            $('<button>', {
                              class: 'btn btn-link memereact'
                            }).html('😆').attr('data-sub-id', sub_id).attr('data-react', 'funny')
                        ).append(
                            $('<button>', {
                              class: 'btn btn-link memereact'
                            }).html('😮').attr('data-sub-id', sub_id).attr('data-react', 'shock')
                        ).append(
                            $('<button>', {
                              class: 'btn btn-link memereact'
                            }).html('😢').attr('data-sub-id', sub_id).attr('data-react', 'sad')
                        ).append(
                            $('<button>', {
                              class: 'btn btn-link memereact'
                            }).html('😠').attr('data-sub-id', sub_id).attr('data-react', 'angry')
                        )
                    )
                )
            )
        )
    );
  };


  const appendSubmissions = (subs) => {
    for(let i = 0; i < subs.length; i++) {
      if(subs[i].name !== username)
        addVoteCard(i, subs[i].text);
    }
  };


  const stateTransition = (name, time) => {
    if (gameCurrentState === name) return;

    for(let key in STATES)
      if (key !== name) {
        let state = STATES[key];
        state.off('click');
        state.fadeOut();
      }

    STATES[name].on('click');
    STATES[name].fadeIn();

    navbarTimerSeconds = time;
    gameCurrentState = name;
  };




  /* KEYBOARD EVENTS */

  $window.keydown(event => {
    // auto-focus current input when key is pressed
    if (!(event.ctrlKey || event.metaKey || event.altKey)) {
      $inputCurrent.focus();
    }

    // on ENTER key
    if (event.which === 13) {
      if (!waitingForLoginResponse && $inputCurrent === $loginUsernameInput) {
        waitingForLoginResponse = true;
        $loginErrorMessage.html("Logging in...");
        sendLoginRequest();
      }
    }
  });




  /* CLICK EVENTS */

  $gameSubmitSend.click(function() {
    sendUserSubmission();
  });

  $gameSubmitSkip.click(function() {
    $gameSubmitSkip.addClass('disabled');
    socket.emit(USER_SKIP);
  });

  $navbarLogo.click(function() {
    window.open('https://github.com/r3w0p/memeoff', '_blank');
  });




  /* SOCKET EVENTS */

  socket.on(TRANSITION, (data) => {
    if(!auth) return;

    if (data.current_state in STATES) {
      log('Transition: ' + data.current_state + '.');

      if (data.current_state === START)
        resetGame();

      else if (data.current_state === VOTE)
        appendSubmissions(data.bundle.submissions);

      stateTransition(data.current_state, data.current_time);
    }
  });

  socket.on(NEW_IMAGE, (data) => {
    if(!auth) return;

    log("New image.");
    setGameImage(data.image);
  });

  socket.on(SUBMISSION_RECEIVED, (data) => {
    if(!auth) return;

    $gameSubmitInput.prop('disabled', true);
    $gameSubmitInput.val(data.text);
    $gameSubmitSend.addClass('disabled');
    $gameSubmitSkip.addClass('disabled');
  });

  socket.on(SUBMISSION_COUNT, (data) => {
    if(!auth) return;

    $gameSubmitSend.attr('data-badge', data.submission_count);
  });

  socket.on(SKIP_COUNT, (data) => {
    if(!auth) return;

    $gameSubmitSkip.attr('data-badge', data.skip_count);
  });

  socket.on(LOGIN_SUCCESS, (data) => {
    if(auth) return;

    username = data.username;
    auth = true;
    log('Login success.');

    for(let i = 0; i < data.all_usernames.length; i++)
      usernames.add(data.all_usernames[i]);

    refreshPlayerList();
    setGameImage(data.current_image);
    appendSubmissions(data.submissions);

    removeLoginPage();
    stateTransition(data.current_state, data.current_time);
    waitingForLoginResponse = false;
  });

  socket.on(LOGIN_FAILURE, (data) => {
    if(auth) return;

    log('Login failed.');
    $loginErrorMessage.html(data.message);
    waitingForLoginResponse = false;
  });

  socket.on(USER_JOINED, (data) => {
    if (auth && username !== data.username) {
      log('User joined: ' + data.username);
      usernames.add(data.username);
      refreshPlayerList();
    }
  });

  socket.on(USER_LEFT, (data) => {
    if (auth && username !== data.username) {
      log('User left: ' + data.username);
      usernames.delete(data.username);
      refreshPlayerList();
    }
  });

  socket.on(DISCONNECT, () => {
    log('Disconnected.');
    auth = false;
  });

  socket.on(RECONNECT, () => {
    log('Reconnected. Refreshing...');
    window.location.reload();
  });

  socket.on(RECONNECT_ERROR, () => {
    log('Reconnect failed.');
  });

});
