# Strict typing imports
from typing import Dict, Any
import json

# Library imports
import click

# Local application imports
from .config import config, ConfigError
from .tecton_client import TectonDebuggerClient
from .mock_client import MockTectonDebuggerClient
from .analysis import analyze_feature_vector, AnalysisResult
from .ui_components import format_cli_report

@click.command()
@click.option('--service-name', required=True, help='The name of the Tecton Feature Service.')
@click.option('--join-keys', required=True, help='A JSON string of the join keys (e.g., \'{"user_id": "123"}\').')
@click.option('--request-data', default='{}', help='A JSON string of request-time context (optional).')
@click.option('--mock', is_flag=True, default=False, help='Run in mock mode without a live Tecton connection.')
def main(service_name: str, join_keys: str, request_data: str, mock: bool) -> None:
    """
    A 1-Click RAG Context Debugger for Tecton.
    """
    try:
        if not mock and config is None:
            raise ConfigError("To run in Live Mode, Tecton environment variables must be set. Use --mock to simulate.")

        join_keys_dict: Dict[str, Any] = json.loads(join_keys)
        request_data_dict: Dict[str, Any] = json.loads(request_data)

        mode = "MOCK" if mock else "LIVE"
        click.echo(f"🔬 Running in {click.style(mode, bold=True)} mode.")
        click.echo(f"🔍 Debugging Feature Service: {click.style(service_name, bold=True)}")
        
        # --- CONDITIONAL CLIENT INITIALIZATION ---
        if mock:
            client: Any = MockTectonDebuggerClient()
        else:
            client = TectonDebuggerClient()
        
        feature_vector = client.fetch_context_vector(service_name, join_keys_dict, request_data_dict)
        analysis: AnalysisResult = analyze_feature_vector(feature_vector)

        click.echo(format_cli_report(analysis))

    except json.JSONDecodeError:
        click.secho("Error: Invalid JSON provided in --join-keys or --request-data.", fg="red", err=True)
    except (ConfigError, ConnectionError, ValueError, RuntimeError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)

if __name__ == '__main__':
    main()