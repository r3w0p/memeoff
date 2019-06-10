'use strict';

const minimist = require('minimist');
const request = require('request').defaults({ encoding: null });
const randomPuppy = require('random-puppy');

const express = require('express');
const app = express();
const path = require('path');
const server = require('http').createServer(app);
const io = require('socket.io')(server);


let args = minimist(process.argv.slice(2), {
  default: {
    port: 3000,
    submit: 60,
    vote: 30,
    winner: 15
  },
});


/* SERVER SETUP */

server.listen(args.port, () => {
  console.log('Server listening at port %d', args.port);
});

app.use(express.static(path.join(__dirname, 'public')));


/* CONSTANTS */

const MIN_PLAYERS = 3;
const MIN_SUBMISSIONS = 2;

const PLAYERS = "PLAYERS";
const START   = "START";
const SUBMIT  = "SUBMIT";
const VOTE    = "VOTE";
const WINNER  = "WINNER";

const STATES = {
  PLAYERS: {"time": -1},
  START:   {"time": 5},
  SUBMIT:  {"time": args.submit},
  VOTE:    {"time": args.vote},
  WINNER:  {"time": args.winner}
};

const SUBREDDITS = [
    "reactionpics",
    "reactiongifs",
    "shittyreactiongifs"
];


/* VARIABLES */

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
  if (usernames.size < MIN_PLAYERS) {
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

  io.emit('transition', {
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
    io.emit('new_image', {
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
    if (num_submissions < MIN_SUBMISSIONS)
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
  if(!attempting_download && !current_image) {
    attempting_download = true;

    randomPuppy(getRandomItem(SUBREDDITS)).then(url => {
      request.get(url, function (error, response, body) {
        if (!error && response.statusCode === 200) {
          current_image = "data:" + response.headers["content-type"] + ";base64," + new Buffer(body).toString('base64');
        }

        attempting_download = false;
      });
    });
  }
};



io.on('connection', (socket) => {
  let addedUser = false;

  // attempts to add new username
  socket.on('login_request', (username) => {
    if (addedUser) return;
    
    if (usernames.has(username)) {
      socket.emit('login_failure', {
        username: username,
        message: "Username already taken."
      });

      return;
    }

    // store username in socket session for this client
    socket.username = username;
    usernames.add(username);

    addedUser = true;

    socket.emit('login_success', {
      username: socket.username,
      all_usernames: Array.from(usernames),
      current_state: current_state,
      current_time: current_time,
      current_image: current_image
    });

    socket.broadcast.emit('user_joined', {
      username: socket.username
    });
  });

  // when the user disconnects.. perform this
  socket.on('disconnect', () => {
    if (addedUser) {
      usernames.delete(socket.username);
      delete submissions[socket.username];

      // echo globally that this client has left
      socket.broadcast.emit('user_left', {
        username: socket.username
      });
    }
  });

  socket.on('user_submission', (data) => {
    if (addedUser) {
      submissions[data.username] = data.text;
      console.log(submissions);

      socket.emit('submission_received', {
        username: socket.username,
        text: data.text
      });

      io.emit('submission_count', {
        submission_count: Object.keys(submissions).length
      });
    }
  });

  socket.on('user_skip', () => {
    if (addedUser) {
      skip_count += 1;

      io.emit('skip_count', {
        skip_count: skip_count
      });
    }
  });

});
