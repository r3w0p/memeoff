$(function() {

    SOCKET.on(CONNECTION, () => {
        console.log('Connected.');
    });

    SOCKET.on(DISCONNECT, () => {
        console.log('Disconnected.');
    });

    SOCKET.on(LOGIN_SUCCESS, (data) => {
        console.log('Login success.');
        onLoginSuccess(data.nickname, data.array_players);
    });

    SOCKET.on(LOGIN_FAILURE, (data) => {
        console.log('Login failed.');
        onLoginFailure(data.nickname, data.error);
    });

});
