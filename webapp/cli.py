#!/usr/local/bin/python3.8
"""
Click command line utilties for management and development
"""
import asyncio
import click
import uvicorn
from functools import wraps
from tortoise import Tortoise

import utils


@click.group()
def cli():
    pass


@cli.command()
def run_prod_server():
    """
    instructions how to start a production server
    """
    click.echo("Please use uvicorn directly to start a server for non-development purpose")
    click.echo("    uvicorn app:create --factory --host=0.0.0.0 --port=8000")
    click.echo("")


@cli.command()
def run_dev_server():
    """
    start the developmentserver
    """
    try:
        uvicorn.run(
            "app:create",
            host="0.0.0.0",
            factory=True,
            port=8000,
            debug=True,
            log_config=utils.LoggingUtil().log_config
        )
    except:
        pass


if __name__ == "__main__":
    cli()
