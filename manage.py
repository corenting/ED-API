#!/usr/bin/env python

from app.services.community_goals import CommunityGoalsService
from click_loglevel import LogLevel
import click
import logging

@click.group()
@click.option("-l", "--log-level", type=LogLevel(), default=logging.INFO)
def cli(log_level: LogLevel):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level,
    )

@cli.command()
def community_goals_notifications():
    """Send FCM notifications for community goals state change."""
    community_goals_service = CommunityGoalsService()
    community_goals_service.send_notifications()

if __name__ == '__main__':
    cli()
