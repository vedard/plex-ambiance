#! /usr/bin/env python3

import signal
import click
import time
import requests
from lxml import etree


@click.command()
@click.option("--plex-server",  required=True, help='The URI for the Plex Media Server')
@click.option("--plex-client", required=True, help='The name of the Plex client')
@click.option("--hue-bridge", required=True, help='The URI of the Hue Bridge')
@click.option("--hue-token", required=True, help='The Hue API token')
@click.option("--on", default=['0'], multiple=True, help="The group of lights you want to turn on")
@click.option("--off", default=['0'], multiple=True, help="The group of lights you want to turn on")
def main(plex_server, plex_client, hue_bridge, hue_token, on, off):
    """ Synchronize your Philips Hue lightbulbs with your Plex playback
    """

    last_state = None
    click.echo(f"Plex server: {plex_server}")
    click.echo(f"Hue bridge: {hue_bridge}")
    click.echo(f"Lights to turn on: {', '.join(on)}")
    click.echo(f"Lights to turn off: {', '.join(off)}")
    click.echo(f"Listening for this device: {plex_client}")
    while True:
        try:

            response = etree.parse(f"{plex_server}/status/sessions")
            new_state = response.xpath(
                f'string(/MediaContainer/Video/Player[@device="{plex_client}"]/@state)')

            if not new_state in ["playing", "paused", "buffering"]:
                new_state = "stopped"

            if last_state != new_state:
                click.echo(f"{plex_client} is now: " + new_state)
                if new_state in ["playing", "buffering"]:
                    click.echo("Turning the lights off")
                    for group in off:
                        requests.put(
                            f"{hue_bridge}/api/{hue_token}/groups/{group}/action", json={"on": False})
                else:
                    click.echo("Turning the lights on")
                    for group in on:
                        requests.put(
                            f"{hue_bridge}/api/{hue_token}/groups/{group}/action", json={"on": True})

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
