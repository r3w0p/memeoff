$(function() {

  // Init constants
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


  /* LOGIN */
  let $loginPage = $('#login-page');
  let $loginUsernameInput = $('#input-username');
  let $loginErrorMessage = $("#login-page-error");

  /* GAME */
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

  /* ALL */
  let $window = $(window);
  let $inputCurrent = $loginUsernameInput.focus();

  let waitingForLoginResponse = false;
  let username;
  let connected = false;
  let usernames = new Set();
  let socket = io();




  /* TOOLS */

  setInterval(function() {
    if (!username) return;

    if (connected) {
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
    let username = cleanInput($loginUsernameInput.val().trim());

    if (username)
      socket.emit('login_request', username);
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





  // Sends a chat message
  const sendUserSubmission = () => {
    if(!username) return;

    let text = cleanInput($gameSubmitInput.val().trim());

    if (text && connected) {
      socket.emit('user_submission', {
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
      if ($inputCurrent === $loginUsernameInput) {
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
    socket.emit('user_skip');
  });

  $navbarLogo.click(function() {
    window.open('https://github.com/r3w0p/memeoff', '_blank');
  });


  /* SOCKET EVENTS */

  socket.on('transition', (data) => {
    log('Transition: ' + data.current_state);

    if (data.current_state in STATES) {
      if(data.current_state === START)
        resetGame();

      stateTransition(data.current_state, data.current_time);
    }
  });

  socket.on('new_image', (data) => {
    log("New image.");
    setGameImage(data.image);
  });

  socket.on('submission_received', (data) => {
    $gameSubmitInput.prop('disabled', true);
    $gameSubmitInput.val(data.text);
    $gameSubmitSend.addClass('disabled');
    $gameSubmitSkip.addClass('disabled');
  });

  socket.on('submission_count', (data) => {
    $gameSubmitSend.attr('data-badge', data.submission_count);
  });

  socket.on('skip_count', (data) => {
    $gameSubmitSkip.attr('data-badge', data.skip_count);
  });

  socket.on('login_success', (data) => {
    connected = true;
    username = data.username;
    log('Login success.');

    data.all_usernames.forEach(item => usernames.add(item));
    setGameImage(data.current_image);
    refreshPlayerList();

    removeLoginPage();
    stateTransition(data.current_state, data.current_time);
    waitingForLoginResponse = false;
  });

  socket.on('login_failure', (data) => {
    log('Login failed.');
    $loginErrorMessage.html(data.message);
    waitingForLoginResponse = false;
  });

  socket.on('user_joined', (data) => {
    if (data.username !== username) {
      log('User joined: ' + data.username);
      usernames.add(data.username);
      refreshPlayerList();
    }
  });

  socket.on('user_left', (data) => {
    if (data.username !== username) {
      log('User left: ' + data.username);
      usernames.delete(data.username);
      refreshPlayerList();
    }
  });

  socket.on('disconnect', () => {
    log('Disconnected.');
    connected = false;
  });

  socket.on('reconnect', () => {
    log('Reconnected. Refreshing...');
    window.location.reload();
  });

  socket.on('reconnect_error', () => {
    log('Reconnect failed.');
  });

});
