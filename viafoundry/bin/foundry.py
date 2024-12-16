#!/usr/bin/env python3
import click
from viafoundry.auth import Auth
from viafoundry.client import ViaFoundryClient
import json
import logging

# Configure logging to capture unexpected errors
logging.basicConfig(filename="viafoundry_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

@click.group()
@click.option('--config', type=click.Path(), help="Path to a custom configuration file.")
@click.pass_context
def cli(ctx, config):
    """ViaFoundry CLI for configuration, endpoint discovery, and API requests."""
    ctx.ensure_object(dict)
    try:
        ctx.obj['client'] = ViaFoundryClient(config)
        ctx.obj['auth'] = Auth(config)
    except Exception as e:
        logging.error("Failed to initialize ViaFoundry client or authentication", exc_info=True)
        click.echo("Error: Failed to initialize the CLI. Please check your configuration file.", err=True)
        raise click.Abort()

@cli.command()
@click.option('--hostname', prompt="API Hostname", help="API Hostname, e.g., https://viafoundry.com")
@click.option('--username', prompt="Username", help="Login username")
@click.option('--password', prompt="Password", hide_input=True, help="Login password")
@click.option('--identity-type', default=1, type=int, help="Identity type (default: 1)")
@click.option('--redirect-uri', default="https://viafoundry.com/user", help="Redirect URI (default: https://viafoundry.com/user)")
@click.pass_context
def configure(ctx, hostname, username, password, identity_type, redirect_uri):
    """Configure the SDK."""
    auth = ctx.obj['auth']
    try:
        auth.configure(hostname, username, password, identity_type, redirect_uri)
        click.echo("Configuration saved successfully.")
    except Exception as e:
        logging.error("Failed to configure authentication", exc_info=True)
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--as-json', is_flag=True, help="Output the endpoints in JSON format.")
@click.pass_context
def discover(ctx, as_json):
    """List all available API endpoints."""
    client = ctx.obj['client']
    try:
        endpoints = client.discover()  # Assume `discover()` returns a dictionary: {endpoint: description}.
        if as_json:
            # Output as JSON
            click.echo(json.dumps(endpoints, indent=4))
        else:
            # Output as plaintext
            click.echo("Available API Endpoints:\n")
            for endpoint, description in endpoints.items():
                click.echo(f"Endpoint: {endpoint}")
                click.echo(f"Description: {description}\n")
    except Exception as e:
        logging.error("Failed to discover endpoints", exc_info=True)
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--endpoint', prompt="API Endpoint", help="The API endpoint to call (e.g., /api/some/endpoint).")
@click.option('--method', default="GET", help="HTTP method to use (GET, POST, etc.).")
@click.option('--params', default=None, help="Query parameters as JSON.")
@click.option('--data', default=None, help="Request body as JSON.")
@click.pass_context
def call(ctx, endpoint, method, params, data):
    """Call a specific API endpoint."""
    client = ctx.obj['client']
    try:
        params = json.loads(params) if params else None
        data = json.loads(data) if data else None
        response = client.call(method, endpoint, params=params, data=data)
        click.echo(json.dumps(response, indent=4))
    except json.JSONDecodeError as e:
        click.echo("Error: Invalid JSON format for parameters or data.", err=True)
    except Exception as e:
        logging.error("Failed to call API endpoint", exc_info=True)
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logging.critical("Critical error in CLI execution", exc_info=True)
        click.echo("A critical error occurred. Please check the logs for more details.", err=True)
