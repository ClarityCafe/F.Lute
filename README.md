# F-Lute

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ClarityCafe/F.Lute)


F-Lute is a discord bot aiming to provide high-quality music with a fully customizable AudioFX set.

[Invite link](https://discordapp.com/oauth2/authorize?client_id=436026947974463488&scope=bot&permissions=36777040) 

## Features

Done:

- Role-based access to commands
- Reaction-based configuration

- AudioFX
  - Volume
  - EQ
  - Panning
  - Playback speed
  - Equal Loudness filter
  - Reversed
- Commands
  - Play
  - Skip
  - Queue
- Optional "Fair Queue"^1


### Notes

1: Fair queue rotates the songs it plays based on user that queued the songs, e.g. User A queues 3 songs and User B queues 1 after that,
    the songs will play in order A, B, A, A

## Self-hosting

To self-host this bot, you can use Heroku, Docker, or just run it on your VPS.

### Heroku

We provided the essential configuration for you to fill up on Heroku. To deploy your version of F-Lute, click on "Deploy to Heroku" on top of this README.

### Docker

as part of Heroku support, F-Lute provides a Docker container. However, as of 2019, we do not provide a DockerHub container for now.

If you wish to use F-Lute in a container, you will need to build it, and refer to `app.json`  for the environment variables F-Lute requires to run.

### Run it bare

If you choose not to use Docker or Heroku, you may also run it on a bare host (VM or bare metal). F-Lute requires Python 3.6 to work, so if you don't have it please install Python from their website or through your package manager. 

Once done, you will need to configure the bot using a `config.json`. Refer to `config.json.example` for the format for your configuration.

And to run the bot you will need to get the dependencies first:

```
$ pip install -r requirements.txt

```
Then finally run it using `python3` (for most distributions that still have `python` as Python 2.7)

```
$ python3 main.py

```

## Notes for Discord staff

Although it may seem I solo'd this project, Aine#0080 (sr229) was a great help in DM for helping me with audio features and overall design, hence why I listed her on the team. I could not have done this without her support.