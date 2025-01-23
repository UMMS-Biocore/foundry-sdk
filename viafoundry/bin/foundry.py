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
@click.argument("file_path", required=False)
@click.argument("download_dir", required=False, default=os.getcwd())
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.option("--filePath", help="File Path dir/filename in pubweb directory (alternative to positional argument).")
@click.option("--downloadDir", default=os.getcwd(), help="Directory to save the file.")

@click.pass_context
def download_file(ctx, report_id, file_path, download_dir, reportid, filepath, downloaddir, ):
    """Download a file from a report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    download_dir = download_dir or downloaddir
    file_path = file_path or filepath
    if not report_id or not file_path :
        click.echo("Error: Report ID, and File Name are required.", err=True)
        return
    try:
        report_data = client.reports.fetch_report_data(report_id)
        download_file_path = client.reports.download_file(report_data, file_path, download_dir)
        click.echo(f"File downloaded to: {download_file_path}")
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

@reports.command()
@click.argument("report_id", required=False)
@click.option("--reportID", help="Report ID (alternative to positional argument).")
@click.pass_context
def get_report_dirs(ctx, report_id, reportid):
    """List all dirs for a specific report."""
    client = ctx.obj["client"]
    report_id = report_id or reportid
    if not report_id:
        click.echo("Error: Report ID is required.", err=True)
        return
    try:
        report_dirs = client.reports.get_report_dirs(report_id)
        click.echo(report_dirs)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@reports.command()
@click.argument("report_id", required=False, type=str)
@click.argument("local_file_path", required=False, type=click.Path(exists=True))
@click.argument("remote_dir", required=False, type=str)
@click.option("--reportID", type=str, help="Report ID (alternative to positional argument).")
@click.option("--localFilePath", type=click.Path(exists=True), help="Local file path (alternative to positional argument).")
@click.option("--remoteDir", type=str, help="Directory name for organizing files (alternative to positional argument).")
@click.pass_context
def upload_report_file(ctx, report_id, local_file_path, remote_dir, reportid, localfilepath, remotedir):
    """
    Upload a file to a report.

    REPORT_ID: The ID of the report .
    FILE_PATH: The local file path of the file to upload (optional; can be specified with --filePath).
    REMOTE_DIR: Directory name for organizing files (optional; can be specified with --remoteDir).

    Examples:
      viafoundry upload-report-file <report_id> <file_path> <directory>
      viafoundry upload-report-file --reportID <report_id> --filePath <path_to_file> --remoteDir <directory>
    """
    try:
        # Fallback to options if arguments are not provided
        report_id = report_id or reportid
        local_file_path = local_file_path or localfilepath
        remote_dir = remote_dir or remotedir

        # Ensure mandatory fields are present
        if not local_file_path:
            raise ValueError("File path is required. Provide it as an argument or use the --filePath option.")
        
        # Initialize client and call upload
        client = ctx.obj["client"]
        response = client.reports.upload_report_file(report_id, local_file_path, remote_dir)
        click.echo(f"File uploaded successfully: {response}")
    except Exception as e:
        click.echo(f"Failed to upload file: {e}", err=True)

@cli.group()
@click.pass_context
def process(ctx):
    """Commands related to process."""
    pass

@process.command()
@click.pass_context
def list_processes(ctx):
    """List all processes."""
    client = ctx.obj["client"]
    processes = client.process.list_processes()
    click.echo(processes)

@process.command()
@click.argument("process_id", required=False, type=str)
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.pass_context
def get_process(ctx, process_id, processid):
    """Get details of a specific process."""
    client = ctx.obj["client"]
    process_id = process_id or processid
    process_info = client.process.get_process(process_id)
    click.echo(process_info)

@process.command()
@click.argument("process_id", required=False, type=str)
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.pass_context
def get_revisions(ctx, process_id, processid):
    """Get revisions for a specific process."""
    client = ctx.obj["client"]
    process_id = process_id or processid
    revisions = client.process.get_process_revisions(process_id)
    click.echo(revisions)

@process.command()
@click.argument("process_id", required=False, type=str)
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.pass_context
def check_usage(ctx, process_id, processid):
    """Check if a process is used in pipelines or runs."""
    client = ctx.obj["client"]
    process_id = process_id or processid
    usage = client.process.check_process_usage(process_id)
    click.echo(usage)

@process.command()
@click.argument("process_id", required=False, type=str)
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.pass_context
def duplicate_process(ctx, process_id, processid):
    """Duplicate a process."""
    client = ctx.obj["client"]
    process_id = process_id or processid
    response = client.process.duplicate_process(process_id)
    click.echo(response)

@process.command()
@click.argument("menu_name", required=False, type=str)
@click.option("--menuName", type=str, help="Menu Name (alternative to positional argument).")
@click.pass_context
def create_menu_group(ctx, menu_name, menuname):
    """Create a new menu group."""
    client = ctx.obj["client"]
    menu_name = menu_name or menuname
    response = client.process.create_menu_group(menu_name)
    click.echo(response)

@process.command()
@click.argument("process_data", required=False, type=click.File('r'))
@click.option("--processData", type=click.File('r'), help="Process Data (alternative to positional argument).")

@click.pass_context
def create_process(ctx, process_data, processdata):
    """Create a new process from a JSON file."""
    client = ctx.obj["client"]
    process_data = process_data or processdata
    process_data = json.load(process_data)
    response = client.process.create_process(process_data)
    click.echo(response)

@process.command()
@click.argument("menu_group_id", required=False, type=int)
@click.argument("menu_name", required=False, type=str)
@click.option("--menuGroupID", type=int, help="Menu Group ID (alternative to positional argument).")
@click.option("--menuName", type=str, help="Menu Name (alternative to positional argument).")
@click.pass_context
def update_menu_group(ctx, menu_group_id, menu_name, menugroupid, menuname):
    """Update an existing menu group."""
    client = ctx.obj["client"]
    menu_group_id = menu_group_id or menugroupid
    menu_name = menu_name or menuname

    if not menu_group_id or not menu_name:
        click.echo("Error: Both Menu Group ID and Menu Name are required.", err=True)
        return

    response = client.process.update_menu_group(menu_group_id, menu_name)
    click.echo(response)


@process.command()
@click.argument("process_id", required=False, type=str)
@click.argument("process_data", required=False, type=click.File('r'))
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.option("--processData", type=click.File('r'), help="Process Data (alternative to positional argument).")
@click.pass_context
def update_process(ctx, process_id, process_data, processid, processdata):
    """Update an existing process."""
    client = ctx.obj["client"]
    process_id = process_id or processid
    process_data = process_data or processdata

    if not process_id or not process_data:
        click.echo("Error: Both Process ID and Process Data are required.", err=True)
        return

    process_data = json.load(process_data)
    response = client.process.update_process(process_id, process_data)
    click.echo(response)


@process.command()
@click.argument("process_id", required=False, type=str)
@click.option("--processID", type=str, help="Process ID (alternative to positional argument).")
@click.pass_context
def delete_process(ctx, process_id, processid):
    """Delete an existing process."""
    client = ctx.obj["client"]
    process_id = process_id or processid

    if not process_id:
        click.echo("Error: Process ID is required.", err=True)
        return

    response = client.process.delete_process(process_id)
    click.echo(response)


@process.command()
@click.argument("pipeline_id", required=False, type=str)
@click.option("--pipelineID", type=str, help="Pipeline ID (alternative to positional argument).")
@click.pass_context
def get_pipeline_parameters(ctx, pipeline_id, pipelineid):
    """Get parameters for a pipeline."""
    client = ctx.obj["client"]
    pipeline_id = pipeline_id or pipelineid

    if not pipeline_id:
        click.echo("Error: Pipeline ID is required.", err=True)
        return

    response = client.process.get_pipeline_parameters(pipeline_id)
    click.echo(response)


@process.command()
@click.pass_context
def list_parameters(ctx):
    """List all parameters."""
    client = ctx.obj["client"]
    response = client.process.list_parameters()
    click.echo(response)


@process.command()
@click.argument("parameter_data", required=False, type=click.File('r'))
@click.option("--parameterData", type=click.File('r'), help="Parameter Data (alternative to positional argument).")
@click.pass_context
def create_parameter(ctx, parameter_data, parameterdata):
    """Create a new parameter."""
    client = ctx.obj["client"]
    parameter_data = parameter_data or parameterdata

    if not parameter_data:
        click.echo("Error: Parameter Data is required.", err=True)
        return

    parameter_data = json.load(parameter_data)
    response = client.process.create_parameter(parameter_data)
    click.echo(response)


@process.command()
@click.argument("parameter_id", required=False, type=str)
@click.argument("parameter_data", required=False, type=click.File('r'))
@click.option("--parameterID", type=str, help="Parameter ID (alternative to positional argument).")
@click.option("--parameterData", type=click.File('r'), help="Parameter Data (alternative to positional argument).")
@click.pass_context
def update_parameter(ctx, parameter_id, parameter_data, parameterid, parameterdata):
    """Update an existing parameter."""
    client = ctx.obj["client"]
    parameter_id = parameter_id or parameterid
    parameter_data = parameter_data or parameterdata

    if not parameter_id or not parameter_data:
        click.echo("Error: Both Parameter ID and Parameter Data are required.", err=True)
        return

    parameter_data = json.load(parameter_data)
    response = client.process.update_parameter(parameter_id, parameter_data)
    click.echo(response)


@process.command()
@click.argument("parameter_id", required=False, type=str)
@click.option("--parameterID", type=str, help="Parameter ID (alternative to positional argument).")
@click.pass_context
def delete_parameter(ctx, parameter_id, parameterid):
    """Delete an existing parameter."""
    client = ctx.obj["client"]
    parameter_id = parameter_id or parameterid

    if not parameter_id:
        click.echo("Error: Parameter ID is required.", err=True)
        return

    response = client.process.delete_parameter(parameter_id)
    click.echo(response)
if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logging.critical("Critical error in CLI execution", exc_info=True)
        click.echo("A critical error occurred. Please check the logs for more details.", err=True)
