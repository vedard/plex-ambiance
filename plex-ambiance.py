#! /usr/bin/env python3

import signal
import click
import time
import requests
from datetime import datetime
from lxml import etree


@click.command()
@click.option("--plex-server",  required=True, envvar='PLEX_SERVER', help='The URI for the Plex Media Server')
@click.option("--plex-client", required=True, envvar='PLEX_CLIENT', help='The name of the Plex client')
@click.option("--plex-token", default="", envvar='PLEX_TOKEN', help='The plex API token')
@click.option("--hue-bridge", required=True, envvar='HUE_BRIDGE', help='The URI of the Hue Bridge')
@click.option("--hue-token", required=True, envvar='HUE_TOKEN', help='The Hue API token')
@click.option("--on", default=['0'], multiple=True, envvar='GROUPS_ON', help="The group of lights you want to turn on")
@click.option("--off", default=['0'], multiple=True, envvar='GROUPS_OFF', help="The group of lights you want to turn on")
@click.option("--trigger-after", default="00:00", envvar='TRIGGER_AFTER', help="Only trigger the lights when the local time has passed the set value")
def main(plex_server, plex_client, plex_token, hue_bridge, hue_token, on, off, trigger_after):
    """ Synchronize your Philips Hue lightbulbs with your Plex playback
    """

    last_state = None

    click.echo(f"Plex server: {plex_server}")
    click.echo(f"Hue bridge: {hue_bridge}")
    click.echo(f"Lights to turn on: {', '.join(on)}")
    click.echo(f"Lights to turn off: {', '.join(off)}")
    click.echo(f"Listening for this device: {plex_client}")

    trigger_after = datetime.strptime(trigger_after, "%H:%M").time()

    plex_url = f"{plex_server}/status/sessions"
    if plex_token:
        plex_url += f"?X-Plex-Token={plex_token}"

    while True:
        try:
            response = etree.parse(plex_url)
            new_state = response.xpath(f'string(/MediaContainer/Video/Player[@device="{plex_client}"]/@state)')

            # Fallback unknown value to stopped
            if not new_state in ["playing", "paused", "buffering"]:
                new_state = "stopped"

            # Ignore buffering state
            if new_state == "buffering":
                continue

            # Ignore when the state hasn't changed
            if last_state == new_state:
                continue

            click.echo(f"{plex_client} is now: " + new_state)

            # Only trigger after the specified local time
            if datetime.now().time() < trigger_after:
                last_state = new_state
                click.echo(f"Waiting for local time ({datetime.now().time()}) to reach {trigger_after}")
                continue

            # Turn off the lights when a media is played
            if new_state == "playing":
                click.echo("Turning the lights off")
                for group in off:
                    requests.put(f"{hue_bridge}/api/{hue_token}/groups/{group}/action", json={"on": False})

            # Turn on the lights when a media is stopped or paused (except the first time we start the service)
            elif last_state != None:
                click.echo("Turning the lights on")
                for group in on:
                    requests.put(f"{hue_bridge}/api/{hue_token}/groups/{group}/action", json={"on": True})

            last_state = new_state

        except Exception as ex:
            click.echo(ex)
        finally:
            time.sleep(1)


def handle_sigterm(*args):
    raise KeyboardInterrupt()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    main()
