// Setup basic express server
let fs = require('fs');
let request = require('request').defaults({ encoding: null });
let cheerio = require('cheerio');
let randomPuppy = require('random-puppy');

let express = require('express');
let app = express();
let path = require('path');
let server = require('http').createServer(app);
let io = require('socket.io')(server);
let port = process.env.PORT || 3000;

server.listen(port, () => {
  console.log('Server listening at port %d', port);
});

app.use(express.static(path.join(__dirname, 'public')));


// Init constants

const PLAYERS = "PLAYERS";
const START   = "START";
const SUBMIT  = "SUBMIT";
const VOTE    = "VOTE";
const WINNER  = "WINNER";

const STATES = {
  PLAYERS: {"time": -1, "next": START},
  START:   {"time": 5,  "next": SUBMIT},
  SUBMIT:  {"time": 30, "next": VOTE},
  VOTE:    {"time": 30, "next": WINNER},
  WINNER:  {"time": 10, "next": START}
};

const SUBREDDITS = [
    "reactionpics",
    "mfw",
    "ReactionMemes"
];

// Init variables

let usernames = new Set();
let current_state = "";
let current_time = -1;
let current_image = null;
let attempting_download = false;


setInterval(() => {
  if(current_time >= 0)
    current_time -= 1;

  // Not enough players
  if (usernames.size < 2) {
    if (current_state !== PLAYERS)
      stateTransition(PLAYERS);

  } else {
    // When enough players arrive, notify new game starting
    if(current_state === PLAYERS) {
      current_image = null;
      stateTransition(START);

    } else if(current_state === START) {
      // New image has been downloaded
      if (current_image) {
        // Wait for countdown, then start
        if(current_time < 0)
          stateTransition(SUBMIT, {
            image: current_image
          });

      } else getNewImage(); // keep trying to get new image

    } else {
      if (current_time < 0) {
        // TODO
      }
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


const getRandomItem = (items) => {
  return items[Math.floor(Math.random() * items.length)];
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
  /*
  fs.readFile(path.resolve(__dirname, './public/img/fried.png'), function(err, data) {
    current_image = "data:image/png;base64,"+ data.toString("base64");
  });
  */
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
      current_time: current_time
    });

    socket.broadcast.emit('user_joined', {
      username: socket.username
    });
  });

  // when the user disconnects.. perform this
  socket.on('disconnect', () => {
    if (addedUser) {
      usernames.delete(socket.username);

      // echo globally that this client has left
      socket.broadcast.emit('user_left', {
        username: socket.username
      });
    }
  });
});
