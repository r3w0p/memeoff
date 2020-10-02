$(function() {

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
        $loginErrorMessage.html("Joining...");
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


  /* SOCKET EVENTS */

  socket.on(TRANSITION, (data) => {
    if(!auth) return;

    if (data.current_state in STATES) {
      log('Transition: ' + data.current_state + '.');

      if (data.current_state === START)
        onTransitionStart();

      else if (data.current_state === VOTE)
        onTransitionVote(data.bundle.submissions);

      else if (data.current_state === WINNER)
        onTransitionWinner(data.bundle.winners);

      stateTransition(data.current_state, data.current_time);
    }
  });

  socket.on(NEW_IMAGE, (data) => {
    if(!auth) return;

    log("New image.");
    gameCurrentImage = data.image;
    setGameImage();
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
    onTransitionVote(data.submissions);

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
    $loginErrorMessage.html("😵");
  });

  socket.on(RECONNECT, () => {
    log('Reconnected. Refreshing...');
    window.location.reload();
  });

  socket.on(RECONNECT_ERROR, () => {
    log('Reconnect failed.');
    $loginErrorMessage.html("😵");
  });

});
