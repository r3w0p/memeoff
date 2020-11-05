'use strict';

const minimist = require('minimist');
const randomPuppy = require('random-puppy');
const request = require('request').defaults({ encoding: null });
const Jimp = require('jimp');
const fs = require('fs');

const express = require('express');
const app = express();
const path = require('path');
const server = require('http').createServer(app);
const io = require('socket.io')(server);


/* ARGUMENTS */

let args = minimist(process.argv.slice(2), {
    default: {
        port: 3000,
        min_players: 1,
        max_players: 10,

        dur_load: 5,  // todo validate arguments
        dur_game: 30,
        dur_winner: 15,
        min_nickname: 3,
        max_nickname: 10,

        max_width: 400,
        max_height: 400,
        subreddits: 'subreddits.txt',
        delimiter: '\n'
    },
});

const validateArgument = (invalidCondition, messageOnTrue) => {
    if (invalidCondition) {
        console.error(messageOnTrue);
        process.exit(1);
    }
};

// --port
validateArgument(args.port < 0 || args.port > 65535,
    "Port must be in the range 0 <= n <= 65535.");

// --min_players
validateArgument(args.min_players < 1 || args.min_players > 100,
    "Minimum players must be in the range 0 <= n <= 100.");

// --max_players
validateArgument(args.max_players < args.min_players || args.max_players > 100,
    "Maximum players must be in the range min_players <= n <= 100.");

// todo validate arguments

// --max_width
validateArgument(args.max_width < 100 || args.max_width > 2000,
    "Maximum image width must be in the range 100 <= n <= 2000.");

// --max_height
validateArgument(args.max_height < 100 || args.max_height > 2000,
    "Maximum image height must be in the range 100 <= n <= 2000.");

// --subreddits
validateArgument(!args.subreddits,
    "A subreddit file must be specified.");

// --delimiter
validateArgument(!args.delimiter,
    "A subreddit file delimiter must be specified.");


/* SERVER SETUP */

server.listen(args.port, () => {
    console.log('Server listening at port %d', args.port);
});

app.use(express.static(path.join(__dirname, 'public')));


/* CONSTANTS */

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

const ROOM_GAME = "room_game";


/* VARIABLES */

let nickname_set = new Set();


/* SOCKET EVENTS */

io.on(CONNECTION, (socket) => {
    let auth = false;
    console.log(CONNECTION + ": " + socket.id);

    socket.on(DISCONNECT, () => {
        if (!auth) return;

        // Remove nickname from the server
        nickname_set.delete(socket.nickname);
        delete nickname_set[socket.nickname];

        // Nickname is no longer authorised to be in the game room
        socket.leave(ROOM_GAME);
        auth = false;

        // Notify players that the user has left
        io.to(ROOM_GAME).emit(USER_LEFT, {
            nickname: socket.nickname
        });

        console.log(DISCONNECT + ": " + socket.nickname);
    });

    socket.on(LOGIN_REQUEST, (nickname) => {
        if (auth) return;

        // Sanitise nickname string
        nickname = nickname.trim();

        // Reject login attempt nickname is invalid
        if (nickname.length < args.min_nickname || nickname.length > args.max_nickname) {
            socket.emit(LOGIN_FAILURE, {
                nickname: nickname,
                error: ERROR_INVALID_NICKNAME_LENGTH
            });

            console.log(LOGIN_FAILURE + ": " + nickname);
            return;
        }

        let nickname_clean = nickname.replace(/[^a-z0-9áéíóúñü \.,_-]/gim, "");

        // Reject unclean nickname
        if(nickname.length !== nickname_clean.length) {
            socket.emit(LOGIN_FAILURE, {
                nickname: nickname,
                error: ERROR_INVALID_NICKNAME_UNCLEAN
            });

            console.log(LOGIN_FAILURE + ": " + nickname);
            return;
        }

        // Reject login attempt if game already has maximum amount of players allowed
        if (nickname_set.size >= args.max_players) {
            socket.emit(LOGIN_FAILURE, {
                nickname: nickname,
                error: ERROR_PLAYER_LIMIT_REACHED
            });

            console.log(LOGIN_FAILURE + ": " + nickname);
            return;
        }

        // Reject login attempt if nickname is already in use by another player
        if (nickname_set.has(nickname)) {
            socket.emit(LOGIN_FAILURE, {
                nickname: nickname,
                error: ERROR_NICKNAME_TAKEN
            });

            console.log(LOGIN_FAILURE + ": " + nickname);
            return;
        }

        // Accept login attempt and add nickname to the server list
        socket.nickname = nickname;
        nickname_set.add(nickname);

        // Nickname is authorised to be in the game room
        socket.join(ROOM_GAME);
        auth = true;

        // Notify new player of login attempt success
        socket.emit(LOGIN_SUCCESS, {
            nickname: socket.nickname,
            array_players: Array.from(nickname_set)
        });

        // Notify existing players of login attempt success
        io.to(ROOM_GAME).emit(USER_JOINED, {
            nickname: socket.nickname
        });

        console.log(LOGIN_SUCCESS + ": " + socket.nickname);
    });

});
