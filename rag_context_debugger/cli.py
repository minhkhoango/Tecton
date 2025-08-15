import json
from typing import Dict, Any
import click
from .config import config, ConfigError
from .mock_client import MockTectonDebuggerClient
from .analysis import analyze_retrieved_context, AnalysisResult
from .ui_components import format_cli_report

@click.command()
@click.option('--service-name', required=True, help='The Tecton Feature Service for RAG.')
@click.option('--join-keys', required=True, help='A JSON string of join keys.')
@click.option('--query', default="Analyze context quality and relevance", help='The user query to diagnose. (Optional, has default)')
@click.option('--mock', is_flag=True, default=False, help='Run in mock mode.')
def main(service_name: str, join_keys: str, query: str, mock: bool) -> None:
    """A 1-Click Debugger for RAG Context Quality."""
    try:
        if not mock and config is None:
            raise ConfigError("To run in Live Mode, set Tecton env vars. Use --mock to simulate.")

        join_keys_dict: Dict[str, Any] = json.loads(join_keys)
        
        mode = "MOCK" if mock else "LIVE"
        click.echo(f"🔬 Running in {click.style(mode, bold=True)} mode.")
        click.echo(f"💬 Diagnosing Query: {click.style(query, bold=True)}")
        
        if mock:
            client = MockTectonDebuggerClient()
        else:
            # Only import tecton_client when not in mock mode
            from .tecton_client import TectonDebuggerClient
            client = TectonDebuggerClient()
        
        click.echo("📡 Fetching context vector...")
        feature_vector = client.fetch_context_vector(service_name, join_keys_dict, {"query": query})
        click.echo("🔍 Analyzing context...")
        analysis: AnalysisResult = analyze_retrieved_context(feature_vector)

        # Check for analysis errors
        if analysis.get('error'):
            click.secho(f"Analysis Error: {analysis['error']}", fg="red", err=True)
            return

        click.echo("📊 Generating report...")
        # The CLI formatter is now responsible for all console output.
        report = format_cli_report(analysis)
        click.echo(report)

    except json.JSONDecodeError:
        click.secho("Error: Invalid JSON format in --join-keys parameter", fg="red", err=True)
    except (ConfigError, ConnectionError, ValueError, RuntimeError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)

if __name__ == "__main__":
    main()