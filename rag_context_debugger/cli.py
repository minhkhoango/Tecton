import json
from typing import Dict, Any, Optional
import click
from .config import config, ConfigError
from .mock_client import MockTectonDebuggerClient
from .analysis import analyze_retrieved_context, AnalysisResult
from .ui_components import format_cli_report

@click.command()
@click.option('--status', help='The Tecton Feature status for RAG. Required for mock mode, optional for live mode.')
@click.option('--quality', type=click.Choice(['Green', 'Yellow', 'Red', 'Repetitive', 'Irrelevant', 'Fail']), help='Quality level for mock mode (alias for --status).')
@click.option('--join-keys', default='{"user_id": "test"}', help='A JSON string of join keys.')
@click.option('--query', default="How do I reset my password?", help='The user query to diagnose. (Optional, has default)')
@click.option('--seed', type=int, help='Optional seed for deterministic mock output.')
@click.option('--mock', is_flag=True, default=False, help='Run in mock mode.')
def main(status: str, quality: str, join_keys: str, query: str, seed: Optional[int], mock: bool) -> None:
    """A 1-Click Debugger for RAG Context Quality."""
    try:
        # Validate status/quality parameter based on mode
        if mock and not status and not quality:
            click.secho("Error: --status or --quality is required when running in mock mode.", fg="red", err=True)
            click.echo("Available mock qualities: Green, Yellow, Red, Irrelevant, Repetitive, Fail")
            return
        
        # Prefer quality over status if both are provided
        if quality:
            status = quality
        
        if not mock and config is None:
            raise ConfigError("To run in Live Mode, set Tecton env vars. Use --mock to simulate.")

        join_keys_dict: Dict[str, Any] = json.loads(join_keys)
        
        mode = "MOCK" if mock else "LIVE"
        click.echo(f"🔬 Running in {click.style(mode, bold=True)} mode.")
        
        if mock:
            click.echo(f"🎭 Mock Status: {click.style(status, bold=True)}")
        click.echo(f"💬 Diagnosing Query: {click.style(query, bold=True)}")
        
        if mock:
            client = MockTectonDebuggerClient()
        else:
            # Only import tecton_client when not in mock mode
            from .tecton_client import TectonDebuggerClient
            client = TectonDebuggerClient()
        
        click.echo("📡 Fetching context vector...")
        # For live mode, status might be None, so we need to handle that
        request_data: Dict[str, Any] = {"query": query}
        if seed is not None:
            request_data["seed"] = seed
            
        if mock:
            feature_vector = client.fetch_context_vector(status, join_keys_dict, request_data)
        else:
            # In live mode, status is not used by the real client
            feature_vector = client.fetch_context_vector("", join_keys_dict, request_data)
        
        click.echo("🔍 Analyzing context...")
        analysis: AnalysisResult = analyze_retrieved_context(feature_vector)

        # Check for analysis errors
        if analysis.get('error') is not None:
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