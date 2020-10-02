// Sends a chat message
const sendLoginRequest = () => {
    let clean_username = cleanInput($loginUsernameInput.val().trim());

    if (clean_username)
        socket.emit(LOGIN_REQUEST, clean_username);
    else {
        $loginErrorMessage.html("Invalid username.");
        waitingForLoginResponse = false;
    }
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