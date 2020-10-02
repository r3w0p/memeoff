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