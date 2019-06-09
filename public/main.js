$(function() {

  // Init constants
  const LOGGING = true;

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

  let timer_seconds = 10;



  /* TOOLS */

  setInterval(function() {
    if (!username) return;

    if (connected) {
      if (timer_seconds > -1)
        timer_seconds -= 1;

      $('#nav-timer-loading').show();
      $('#nav-timer').html(timer_seconds > -1 ? timer_seconds + "..." : "Waiting...");

    } else {
      $('#nav-timer-loading').hide();
      $('#nav-timer').html("Disconnected.");
    }
  }, 1000);

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
  };

  // Show error message on login failure
  const showLoginErrorMessage = (message) => {
    $("#login-page-error").html(message);
  };

  // Sets the client's username
  const transitionGamePage = () => {
    if (username) {
      $loginPage.off('click');
      $gamePage.show();
      $loginPage.fadeOut();
      $inputCurrent = $inputGame.focus();
    }
  };




  /* GAME */

  // Sends a chat message
  const sendGameText = () => {
    let text = cleanInput($inputGame.val().trim());

    if (text && connected) {
      socket.emit('game text', text);
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


  

  /* KEYBOARD EVENTS */

  $window.keydown(event => {
    // auto-focus current input when key is pressed
    if (!(event.ctrlKey || event.metaKey || event.altKey)) {
      $inputCurrent.focus();
    }

    // on ENTER key
    if (event.which === 13) {
      if ($inputCurrent === $inputGame)
        sendGameText();

      else if ($inputCurrent === $inputUsername)
        sendLoginRequest();
    }
  });




  /* SOCKET EVENTS */

  socket.on('login_success', (data) => {
    connected = true;
    username = data.username;
    log('Login success (%s).', username);

    data.arr_usernames.forEach(item => usernames.add(item));
    refreshPlayerList();
    transitionGamePage();
  });

  socket.on('login_failure', (data) => {
    log('Login failed (%s).', data.username);
    showLoginErrorMessage(data.message)
  });

  socket.on('user_joined', (data) => {
    if (data.username !== username) {
      log('User joined (%s).', data.username);
      usernames.add(data.username);
      refreshPlayerList();
    }
  });

  socket.on('user_left', (data) => {
    if (data.username !== username) {
      log('User left (%s).', data.username);
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
