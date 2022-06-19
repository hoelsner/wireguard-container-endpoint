"""
command utility for integration testing
"""
import click

import utils


@click.group()
def cli():
    pass


@cli.command()
def create_scenario_1():
    """create containers for scenario 1
    """
    click.echo("create containers for scenario 1...")
    utils.create_scenario_1()
    click.echo("containers for scenario 1 created")


@cli.command()
def destroy_scenario_1():
    """create containers for scenario 1
    """
    click.echo("destroy containers for scenario 1...")
    utils.destroy_scenario_1()
    click.echo("containers for scenario 1 removed")


@cli.command()
def create_scenario_2():
    """create containers for scenario 2
    """
    click.echo("create containers for scenario 2...")
    utils.create_scenario_2()
    click.echo("containers for scenario 2 created")


@cli.command()
def destroy_scenario_2():
    """create containers for scenario 2
    """
    click.echo("destroy containers for scenario 2...")
    utils.destroy_scenario_2()
    click.echo("containers for scenario 2 removed")


if __name__ == "__main__":
    cli()
