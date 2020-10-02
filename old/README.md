
<p>
  <img alt="memeoff" src="https://raw.githubusercontent.com/r3w0p/memeoff/master/public/img/logo/400.png">
</p>

<p>
  <a href="javascript:;" alt="Players">
    <img src="https://img.shields.io/badge/players-3+-red.svg"/></a>
  <a href="javascript:;" alt="Version">
     <img src="https://img.shields.io/github/package-json/v/r3w0p/memeoff.svg"/></a>
  <a href="https://github.com/r3w0p/memeoff/blob/master/LICENSE" alt="License">
     <img src="https://img.shields.io/github/license/r3w0p/memeoff.svg"/></a>
  <a href="https://github.com/r3w0p/memeoff/graphs/commit-activity" alt="Last Commit">
     <img src="https://img.shields.io/github/last-commit/r3w0p/memeoff.svg"/></a>
  <a href="https://www.buymeacoffee.com/r3w0p" alt="Buy Me A Coffee">
     <img src="https://img.shields.io/badge/donate-buy%20me%20a%20coffee-orange.svg"/></a>
  <a href="https://www.paypal.me/apowpow" alt="PayPal">
     <img src="https://img.shields.io/badge/donate-PayPal-blue.svg"/></a>
</p>


Meme battling with friends.


## How to Play

1) Players are shown a random image from a random subreddit in `subreddits.txt`.
2) They submit a caption to go with the image.
3) Players vote for their favourite meme by choosing a reaction: 😍 😆 😮 😢 😠
4) The meme(s) with the most votes win.


## Setup

1) Install `node` (tested on version `14.12.0`)
2) Install packages using `npm install`.
3) Run `npm start` for default configuration, or `node index.js` to specify arguments (below).
4) Go to `http://localhost:<port>`.


### Arguments

|Argument         |Minimum      |Maximum      |Default         |Description                                      |
|:----------------|:------------|:------------|:---------------|:------------------------------------------------|
|`--port`         |0            |65535        |3000            |The port.                                        |
|`--min_players`  |3            |100          |3               |Minimum number of players to start a game.       |
|`--max_players`  |`min_players`|100          |10              |Maximum number of players.                       |
|`--min_submit`   |2            |`min_players`|2               |Minimum number of submissions to start a vote.   |
|`--dur_submit`   |1            |1800         |30              |Seconds in which players can make submissions.   |
|`--min_vote`     |1            |`min_players`|1               |Minimum number of votes that need to be cast.    |
|`--dur_vote`     |1            |1800         |30              |Seconds in which players can vote.               |
|`--dur_winner`   |1            |1800         |10              |Seconds to show the winning meme(s).             |
|`--max_width`    |100          |2000         |400             |Maximum width of image, in pixels.               |
|`--max_height`   |100          |2000         |300             |Maximum height of image, in pixels.              |
|`--subreddits`   |             |             |`subreddits.txt`|Path to list of subreddits.                      |
|`--delimiter`    |             |             |`\n`            |Delimiter that separates subreddits in `subreds`.|


