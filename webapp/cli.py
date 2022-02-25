#!/usr/local/bin/python3.8
"""
Click command line utilties for management and development
"""
import os
import shutil
import click
import uvicorn
from functools import wraps
from tortoise import Tortoise


@click.group()
def cli():
    pass


@cli.command()
def clean_dev():
    """clean dev server files
    """
    os.remove("db.sqlite3")
    shutil.rmtree("tmp")
    click.echo("dev server resetted")


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
            "app.fast_api:create",
            host="0.0.0.0",
            factory=True,
            port=8000,
            debug=True
        )

    except:
        pass


if __name__ == "__main__":
    cli()
