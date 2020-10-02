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
const USER_VOTE           = 'user_vote';

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
let $gameSubmitImageContainer = $('#submit-image-container');
let gameCurrentImage = "";

// Vote
let $gameVoteImageContainer = $('#vote-image-container');

// Winner
let $gameWinnerImageContainer = $('#winner-image-container');

// Other
let $window = $(window);
let $inputCurrent = $loginUsernameInput.focus();

let waitingForLoginResponse = false;
let username = "";
let auth = false;
let usernames = new Set();
let socket = io();