#!/usr/bin/env python

import logging

import typer

from app.services.community_goals import CommunityGoalsService

cli_app = typer.Typer()


@cli_app.callback()
def main() -> None:
    """Initialize the CLI."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


@cli_app.command()
def community_goals_notifications() -> None:
    """Send FCM notifications for community goals state change."""
    community_goals_service = CommunityGoalsService()
    community_goals_service.send_notifications()


if __name__ == "__main__":
    cli_app()
