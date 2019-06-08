// Setup basic express server
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

let usernames = new Set();

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
      arr_usernames: Array.from(usernames)
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
