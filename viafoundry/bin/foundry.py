#!/usr/bin/env python3
import click
from viafoundry.auth import Auth
from viafoundry.client import ViaFoundryClient
from viafoundry import __version__  # Import the version
import json
import logging
import os

# Configure logging
logging.basicConfig(filename="viafoundry_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help="Show the version of the ViaFoundry CLI.")
@click.option('--config', type=click.Path(), help="Path to a custom configuration file.")
@click.pass_context
def cli(ctx, version, config):
    """ViaFoundry CLI for configuration, endpoint discovery, and API requests."""
    if version:
        click.echo(f"ViaFoundry CLI version {__version__}")
        return

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
def configure(ctx, hostname, username, password, identity_type=1, redirect_uri="https://viafoundry.com/user"):
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
@click.option('--search', default=None, help="Search term to filter endpoints. Use freely or as 'key=value'.")
@click.pass_context
def discover(ctx, as_json, search):
    """List all available API endpoints with optional filtering."""
    client = ctx.obj['client']
    try:
        endpoints = client.discover()  # Assume this returns a dictionary {endpoint: methods}.
        filtered_endpoints = {}

        # Parse search term
        search_key, search_value = None, None
        if search:
            if '=' in search:
                search_key, search_value = search.split('=', 1)
            else:
                search_value = search.lower()

        # Filter endpoints
        for endpoint, methods in endpoints.items():
            for method, details in methods.items():
                description = details.get('description', '').lower()
                include = False

                # Filter logic
                if search_key and search_value:
                    if search_key == 'endpoint' and search_value in endpoint.lower():
                        include = True
                    elif search_key == 'description' and search_value in description:
                        include = True
                elif search_value:  # Search all fields freely
                    if (search_value in endpoint.lower() or
                            search_value in description or
                            search_value in method.lower()):
                        include = True
                else:
                    include = True  # No search term provided, include all

                if include:
                    if endpoint not in filtered_endpoints:
                        filtered_endpoints[endpoint] = {}
                    filtered_endpoints[endpoint][method] = details

        # Output results
        if as_json:
            # Output filtered data as JSON
            click.echo(json.dumps(filtered_endpoints, indent=4))
        else:
            # Output filtered data in formatted text
            click.echo("Available API Endpoints:\n")
            for endpoint, methods in filtered_endpoints.items():
                for method, details in methods.items():
                    description = details.get('description', 'No description available')
                    click.echo(f"Endpoint: {endpoint}")
                    click.echo(f"Method: {method}")
                    click.echo(f"Description: '{description}'")
                    
                    # If the method is POST, print the required data
                    if method.lower() == 'post':
                        request_body = details.get('requestBody', {})
                        if 'application/json' in request_body.get('content', {}):
                            schema = request_body['content']['application/json'].get('schema', {})
                            click.echo(f"Data to send: {json.dumps(schema, indent=4)}")
                        else:
                            click.echo("Data to send: No specific schema provided.\n")
                    click.echo()  # Add a newline for readability
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

@cli.group()
@click.pass_context
def reports(ctx):
    """Commands related to reports."""
    pass

@reports.command()
@click.argument("report_id", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.pass_context
def fetch(ctx, report_id, reportid):
    """Fetch JSON data for a report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    if not report_id:
        click.echo("Error: Report ID is required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        click.echo(json.dumps(report_data, indent=4))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@reports.command()
@click.argument("report_id", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.pass_context
def list_processes(ctx, report_id, reportid):
    """List unique processes in a report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    if not report_id:
        click.echo("Error: Report ID is required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        process_names = client.reports.get_process_names(report_data)
        click.echo("\n".join(process_names))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@reports.command()
@click.argument("report_id", required=False)
@click.argument("process_name", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.option("--processName", help="Process name (alternative to positional argument).")
@click.pass_context
def list_files(ctx, report_id, process_name, reportid, processname):
    """List files for a specific process."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    process_name = process_name or processname
    if not report_id or not process_name:
        click.echo("Error: Report ID and Process Name are required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        files = client.reports.get_file_names(report_data, process_name)
        click.echo(files.to_string())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@reports.command()
@click.argument("report_id", required=False)
@click.argument("process_name", required=False)
@click.argument("file_name", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.option("--processName", help="Process name (alternative to positional argument).")
@click.option("--fileName", help="File name (alternative to positional argument).")
@click.option("--download-dir", default=os.getcwd(), help="Directory to save the file.")
@click.pass_context
def download_file(ctx, report_id, process_name, file_name, reportid, processname, filename, download_dir):
    """Download a file from a report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    process_name = process_name or processname
    file_name = file_name or filename
    if not report_id or not process_name or not file_name:
        click.echo("Error: Report ID, Process Name, and File Name are required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        file_path = client.reports.download_file(report_data, process_name, file_name, download_dir)
        click.echo(f"File downloaded to: {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@reports.command()
@click.argument("report_id", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.pass_context
def list_all_files(ctx, report_id, reportid):
    """List all files for a specific report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    if not report_id:
        click.echo("Error: Report ID is required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        all_files = client.reports.get_all_files(report_data)
        click.echo(all_files.to_string())
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logging.critical("Critical error in CLI execution", exc_info=True)
        click.echo("A critical error occurred. Please check the logs for more details.", err=True)
