const ELEM_ID_SIGNIN_ERROR_MESSAGE = "id_signin_error_message"
const ELEM_ID_SIGNIN_BUTTON = "id_signin_button"
const ELEM_ID_INPUT_NICKNAME = "id_input_nickname"

const onLoginSuccess = (nickname, array_players) => {
    document.getElementById(ELEM_ID_SIGNIN_ERROR_MESSAGE).style.visibility = "hidden";
    document.getElementById(ELEM_ID_SIGNIN_BUTTON).disabled = true;
    document.getElementById(ELEM_ID_SIGNIN_BUTTON).innerHTML = "Loading...";

    // todo
}

const onLoginFailure = (nickname, error) => {
    switch (error) {
        case ERROR_PLAYER_LIMIT_REACHED:
            error_message = "Player limit reached."
            break;
        case ERROR_NICKNAME_TAKEN:
            error_message = "Nickname already taken."
            break;
        case ERROR_INVALID_NICKNAME_LENGTH:
            error_message = "Invalid nickname length.";
            break;
        case ERROR_INVALID_NICKNAME_UNCLEAN:
            error_message = "Nickname not allowed.";
            break;
        default:
            error_message = "Unknown error occurred.";
    }

    document.getElementById(ELEM_ID_SIGNIN_ERROR_MESSAGE).innerHTML = error_message;
    document.getElementById(ELEM_ID_SIGNIN_ERROR_MESSAGE).style.visibility = "visible";
}

$(function() {
    document.getElementById(ELEM_ID_SIGNIN_BUTTON).onclick = function() {
        let nickname = document.getElementById(ELEM_ID_INPUT_NICKNAME).value;
        console.log(nickname);
        SOCKET.emit(LOGIN_REQUEST, nickname);
    };
});