# Plex-Ambiance
Synchronize your Philips Hue lightbulbs with your Plex playback.

## Description
plex-ambiance is a service that will:
- Turn off your lights when you start or resume a media in Plex
- Turn on your lights when you stop or pause a media in Plex

## Usage
```
Usage: plex-ambiance.py [OPTIONS]

  Synchronize your Philips Hue lightbulbs with your Plex playback

Options:
  --plex-server TEXT  The URI for the Plex Media Server  [required]
  --plex-client TEXT  The name of the Plex client  [required]
  --hue-bridge TEXT   The URI of the Hue Bridge  [required]
  --hue-token TEXT    The Hue API token  [required]
  --on TEXT           The group of lights you want to turn on
  --off TEXT          The group of lights you want to turn on
  --help              Show this message and exit.
```

## Docker
You can run plex-ambiance via the official Docker container
```yaml
---
version: "3"
services:
  plex-ambiance:
    image: plex-ambiance
    container_name: plex-ambiance
    command: >
      --plex-server "http://xxx.xxx.x.x"
      --plex-client "SHIELD Android TV"
      --hue-bridge "http://xxx.xxx.x.x"
      --hue-token "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      --on 7
      --off 6
      --off 7
```

## How to create the Hue API Token
1. Press the link button on the Hue bridge
2. Run this command with the correct IP
    ```sh
    curl http://BRIDGE_IP/api --data '{"devicetype":"plex-ambiance"}' 
    ```
## How to find the name of my Plex client
1. Start a media playback
2. Run this command with the correct IP
    ```sh
    curl http://PLEX_IP/status/sessions 2> /dev/null | grep -oP 'device=".*?"'
    ```