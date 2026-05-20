"""GHL Publisher — direct REST workflow for the Social Planner.

Modules:
  ghl_client  REST client (Private Integration Token, services.leadconnectorhq.com)
  render      HTML -> PNG via Playwright with size presets (default ig_portrait 1080x1350)
  config      Per-client TOML + .env token loading
  cli         setup / publish / verify subcommands

Entry point:
  python -m publisher.cli <subcommand> ...
"""
__version__ = "0.1.0"
