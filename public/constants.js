/* CONSTANTS */

let SOCKET = io();

const CONNECTION = 'connection';
const DISCONNECT = 'disconnect';

const LOGIN_REQUEST = 'login_request';
const LOGIN_FAILURE = 'login_failure';
const LOGIN_SUCCESS = 'login_success';

const ERROR_PLAYER_LIMIT_REACHED = 'error_player_limit_reached';
const ERROR_NICKNAME_TAKEN = 'error_nickname_taken';
const ERROR_INVALID_NICKNAME_LENGTH = 'error_invalid_nickname_length';
const ERROR_INVALID_NICKNAME_UNCLEAN = 'error_invalid_nickname_unclean';

const USER_JOINED = 'user_joined';
const USER_LEFT   = 'user_left';
