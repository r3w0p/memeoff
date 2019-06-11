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


let args = minimist(process.argv.slice(2), {
  default: {
    port: 3000,
    min_players: 3,
    max_players: 10,
    min_submit: 2,
    dur_submit: 60,
    dur_vote: 30,
    dur_winner: 15,
    img_width: 400,
    subreds: 'subreddits.txt',
    delim: '\n'
  },
});

const validateArgument = (invalidCondition, messageOnTrue) => {
  if (invalidCondition) {
    console.error(messageOnTrue);
    process.exit(1);
  }
};

const getSubreddits = (file_subred, delim) => {
  let subred;

  try {
    subred = fs.readFileSync(file_subred, 'utf8')
        .split(delim)
        .map(function(item) {
          return item.trim();
        })
        .filter(function (item) {
          return item;
        });

  } catch (err) {
    console.error("Failed to get subreddits from '" + args.subreds + "': " + err.message);
    process.exit(1);
  }

  if (!subred || subred.length === 0) {
    console.error("No subreddits found in '" + args.subreds + "'.");
    process.exit(1);
  }

  return subred;
};



// --port
validateArgument(args.port < 0 || args.port > 65535,
    "Port must be in the range 0 <= n <= 65535.");

// --min_players
validateArgument(args.min_players < 3 || args.min_players > 100,
    "Minimum players must be in the range 0 <= n <= 100.");

// --max_players
validateArgument(args.max_players < args.min_players || args.max_players > 100,
    "Maximum players must be in the range min_players <= n <= 100.");

// --min_submit
validateArgument(args.min_submit < 2 || args.min_submit > args.min_players,
    "Minimum submissions must be in the range 2 <= n <= min_players.");

// --dur_submit
validateArgument(args.dur_submit < 1 || args.dur_submit > 1800,
    "Submit duration must be in the range 1 <= n <= 1800.");

// --dur_vote
validateArgument(args.dur_vote < 1 || args.dur_vote > 1800,
    "Vote duration must be in the range 1 <= n <= 1800.");

// --dur_winner
validateArgument(args.dur_winner < 1 || args.dur_winner > 1800,
    "Winner duration must be in the range 1 <= n <= 1800.");

// --img_width
validateArgument(args.img_width < 100 || args.img_width > 2000,
    "Image width must be in the range 100 <= n <= 2000.");

// --subreds
validateArgument(!args.subreds,
    "A subreddit file must be specified.");

// --delim
validateArgument(!args.delim,
    "A subreddit file delimiter must be specified.");



/* SERVER SETUP */

server.listen(args.port, () => {
  console.log('Server listening at port %d', args.port);
});

app.use(express.static(path.join(__dirname, 'public')));


/* CONSTANTS */

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

const ROOM_AUTH = "room_auth";

const PLAYERS = "PLAYERS";
const START   = "START";
const SUBMIT  = "SUBMIT";
const VOTE    = "VOTE";
const WINNER  = "WINNER";

const STATES = {
  PLAYERS: {"time": -1},
  START:   {"time": 5},
  SUBMIT:  {"time": args.dur_submit},
  VOTE:    {"time": args.dur_vote},
  WINNER:  {"time": args.dur_winner}
};




/* VARIABLES */
let subreddits = getSubreddits(args.subreds, args.delim);
let usernames = new Set();
let current_state = "";
let current_time = -1;

let current_image = "";
let sent_new_image = false;
let attempting_download = false;
let submissions = {};
let skip_count = 0;


setInterval(() => {
  if(current_time >= 0)
    current_time -= 1;

  // Not enough players
  if (usernames.size < args.min_players) {
    waitForMorePlayers();

  } else {
    if(current_state === PLAYERS) {
      resetGame();

    } else if(current_state === START) {
      handleStart();

    } else if(current_state === SUBMIT) {
      handleSubmit();

    } else if(current_state === VOTE) {
      handleVote();

    } else if(current_state === WINNER) {
      resetGame();
    }
  }
}, 1000);


const stateTransition = (state_name, bundle) => {
  current_state = state_name;
  current_time = STATES[current_state].time;

  io.emit(TRANSITION, {
    current_state: current_state,
    current_time: current_time,
    bundle: bundle || {}
  });
};


const waitForMorePlayers = () => {
  if (current_state !== PLAYERS)
    stateTransition(PLAYERS);
};


const resetGame = (force) => {
  if(force || current_time < 0) {
    // TODO reset all game variables
    current_image = "";
    sent_new_image = false;
    attempting_download = false;
    submissions = {};
    skip_count = 0;

    stateTransition(START);
  }
};


const handleStart = () => {
  if (!current_image) {
    // keep trying to get a new image
    getNewImage();

  } else if (!sent_new_image) {
    // send new image
    io.emit(NEW_IMAGE, {
      image: current_image
    });

    sent_new_image = true;
  }

  // transition when new image sent and timer elapse
  if(sent_new_image && current_time < 0)
    stateTransition(SUBMIT);
};


const handleSubmit = () => {
  let num_submissions = Object.keys(submissions).length;
  let num_users = usernames.size;

  if (num_users === num_submissions) {
    // everybody has submitted
    stateTransition(VOTE);

  } else if (skip_count > (num_users / 2)) {
    // majority want to skip current image
    resetGame(true);

  } else if(current_time < 0) {
    if (num_submissions < args.min_submit)
      resetGame();
    else
      stateTransition(VOTE);
  }
};


const handleVote = () => {
  if(current_time < 0)
    if(!areNoVotes())
      stateTransition(WINNER);
    else
      resetGame();
};


const getRandomItem = (items) => {
  return items[Math.floor(Math.random() * items.length)];
};


const isEmpty = (obj) => {
  for(let key in obj)
    if (obj.hasOwnProperty(key))
      return false;

  return true;
};


const areNoVotes = () => {
  // TODO
  return false;
};


const getNewImage = () => {
  // try to download new image if not already doing so
  // and one hasn't already been downloaded
  if(!attempting_download && !current_image) {
    attempting_download = true;

    // get random image url from random subreddit
    randomPuppy(getRandomItem(subreddits))
        .then(imageURL => {

      // download the image
      request.get(imageURL, function (error, response, body) {
        if (!error && response.statusCode === 200) {

          // modify image
          Jimp.read(new Buffer(body))
              .then(img => {

                // resize image and convert to base64
                img.resize(args.img_width, Jimp.AUTO).getBase64(Jimp.AUTO, function(e, img64) {
                  if(!e)
                    current_image = img64; // store base64 image

                  attempting_download = false;
                });

              }).catch(err => { attempting_download = false; }); // jimp read

        } else attempting_download = false; // request error
      });

    }).catch(err => { attempting_download = false; }); // randomPuppy
  }
};




io.on(CONNECTION, (socket) => {
  let auth = false;

  // attempts to add new username
  socket.on(LOGIN_REQUEST, (username) => {
    if (auth) return;

    if (usernames.size >= args.max_players) {
      socket.emit(LOGIN_FAILURE, {
        username: username,
        message: "Player limit reached. Try again later."
      });

      return;
    }

    if (usernames.has(username)) {
      socket.emit(LOGIN_FAILURE, {
        username: username,
        message: "Username already taken."
      });

      return;
    }

    // add user to game
    socket.username = username;
    usernames.add(username);
    socket.join(ROOM_AUTH);
    auth = true;

    socket.emit(LOGIN_SUCCESS, {
      username: socket.username,
      all_usernames: Array.from(usernames),
      current_state: current_state,
      current_time: current_time,
      current_image: current_image
    });

    // notify players
    io.to(ROOM_AUTH).emit(USER_JOINED, {
      username: socket.username
    });
  });

  socket.on(DISCONNECT, () => {
    if (!auth) return;

    // remove user from game
    usernames.delete(socket.username);
    delete usernames[socket.username];
    socket.leave(ROOM_AUTH);

    auth = false;

    // notify players
    io.to(ROOM_AUTH).emit(USER_LEFT, {
      username: socket.username
    });
  });

  socket.on(USER_SUBMISSION, (data) => {
    if (!auth) return;

    submissions[data.username] = data.text;
    console.log(submissions);

    socket.emit(SUBMISSION_RECEIVED, {
      username: socket.username,
      text: data.text
    });

    io.to(ROOM_AUTH).emit(SUBMISSION_COUNT, {
      submission_count: Object.keys(submissions).length
    });
  });

  socket.on(USER_SKIP, () => {
    if (!auth) return;

    skip_count += 1;

    io.to(ROOM_AUTH).emit(SKIP_COUNT, {
      skip_count: skip_count
    });
  });

});

