# memeoff

![3 or more players](https://img.shields.io/badge/players-3%20or%20more-red.svg)
[<img src="https://img.shields.io/badge/donate-buy%20me%20a%20coffee-orange.svg">](https://www.buymeacoffee.com/r3w0p)
[<img src="https://img.shields.io/badge/donate-PayPal-blue.svg">](https://www.paypal.me/apowpow)

Meme battling with friends.


## How to Play

1) Players are shown a random [reaction image](https://knowyourmeme.com/memes/reaction-images)
scraped from the web.
2) They submit a caption to go with the image.
3) Players vote for their favourite meme by choosing the reaction they had when seeing it: 😍 😆 😮 😢 😠
4) The meme(s) with the most votes wins.


## Setup

1) Install packages using `npm install`
2) Run `npm start`, or `node index.js` to specify parameters (below)
3) Go to `http://localhost:<port>`


### Parameters

| Argument        | Minimum       | Maximum       | Default | Description                                    |
|:----------------|:--------------|:--------------|:--------|:-----------------------------------------------|
| `--port`        | 0             | 65535         | 3000    | The port.                                      |
| `--min_players` | 3             | 100           | 3       | Minimum number of players to start a game.     |
| `--max_players` | `min_players` | 100           | 10      | Maximum number of players.                     |
| `--min_submit`  | 2             | `min_players` | 2       | Minimum number of submissions to start a vote. |
| `--dur_submit`  | 1             | 1800          | 60      | Seconds in which players can make submissions. |
| `--dur_vote`    | 1             | 1800          | 30      | Seconds in which players can vote.             |
| `--dur_winner`  | 1             | 1800          | 15      | Seconds to show the winning meme(s).           |
| `--img_width`   | 100           | 2000          | 400     | Width to resize image, in pixels.              |



