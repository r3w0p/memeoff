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

  // Init variables
  let $window = $(window);
  
  let $inputGame = $('#input-game');
  let $inputUsername = $('#input-username');
  let $inputCurrent = $inputUsername.focus();

  let $loginPage = $('#login-page');
  let $gamePage = $('#game-page');

  let username;
  let connected = false;
  let usernames = new Set();
  let socket = io();

  let current_state = "";
  let timer_seconds = -1;



  /* TOOLS */

  setInterval(function() {
    if (!username) return;

    if (connected) {
      if (timer_seconds > -1)
        timer_seconds -= 1;

      setNotif(timer_seconds > -1 ? timer_seconds + "..." : "...", true);
    } else
      setNotif("Disconnected.", false);
  }, 1000);

  const setNotif = (message, show_loading) => {
    if (show_loading)
      $('#nav-timer-loading').show();
    else
      $('#nav-timer-loading').hide();

    $('#nav-timer').html(message);
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
    let username = cleanInput($inputUsername.val().trim());

    if (username)
      socket.emit('login_request', username);
    else
      $("#login-page-error").html("Invalid username.");
  };

  // Show error message on login failure
  const showLoginErrorMessage = (message) => {
    $("#login-page-error").html(message);
  };

  // Sets the client's username
  const removeLoginPage = () => {
    if (username) {
      $loginPage.off('click');
      $gamePage.show();
      $loginPage.fadeOut();
      $inputCurrent = $inputGame.focus();
    }
  };




  /* GAME */

  const resetGame = () => {
    // TODO
  }

  // Sends a chat message
  const sendUserSubmission = () => {
    if(!username) return;

    let text = cleanInput($inputGame.val().trim());

    if (text && connected) {
      socket.emit('user_submission', {
        username: username,
        text: text
      });
    }
  };
  
  // Refresh the names in the player list
  const refreshPlayerList = () => {
    let arr_usernames = Array.from(usernames).sort();
    let li_str = "";

    arr_usernames.forEach(function (item, index) {
      li_str += '<li class="pure-menu-item"><span class="pure-menu-link">' + item + '</span></li>';
    });

    $("#player-list-link").html("Players (" + arr_usernames.length + ")");
    $("#player-list").html(li_str);
  };

  const stateTransition = (name, time) => {
    if (current_state === name) return;

    for(let key in STATES)
      if (key !== name) {
        let state = STATES[key];
        state.off('click');
        state.fadeOut();
      }

    STATES[name].on('click');
    STATES[name].fadeIn();

    timer_seconds = time;
    current_state = name;
  };




  /* KEYBOARD EVENTS */

  $window.keydown(event => {
    // auto-focus current input when key is pressed
    if (!(event.ctrlKey || event.metaKey || event.altKey)) {
      $inputCurrent.focus();
    }

    // on ENTER key
    if (event.which === 13) {
      if ($inputCurrent === $inputUsername)
        sendLoginRequest();
    }
  });


  /* CLICK EVENTS */

  $("#input-game-submit").click(function(){
    sendUserSubmission();
  });



  /* SOCKET EVENTS */

  socket.on('transition', (data) => {
    log('Transition: ' + data.current_state);

    if (data.current_state in STATES) {

      if(data.current_state === START) {
        resetGame();
      }

      if(data.current_state === SUBMIT) {
        log("Loading image...");

        $('#submit-image-container').html(
            $('<img>',{
              class: 'img-responsive',
              src: data.bundle.image,
              width: '100%'
            })
        );
      }

      stateTransition(data.current_state, data.current_time);
    }
  });

  socket.on('submission_received', (data) => {
    $('#input-game').prop('disabled', true);
    $('#input-game').val(data.text);
    $('#input-game-submit').addClass('disabled');
  });

  socket.on('login_success', (data) => {
    connected = true;
    username = data.username;
    log('Login success.');

    data.all_usernames.forEach(item => usernames.add(item));
    refreshPlayerList();
    removeLoginPage();
    stateTransition(data.current_state, data.current_time);
  });

  socket.on('login_failure', (data) => {
    log('Login failed.');
    showLoginErrorMessage(data.message)
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
