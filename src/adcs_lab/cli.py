"""Unified CLI for ADCS lab simulations, detection, and hardening."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Callable

from adcs_lab import Esc1Simulation, LabConfiguration, TemplateAnalyzer, EkuHardener

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def _load_configuration(path: Path) -> LabConfiguration:
    """Load and validate lab configuration from a YAML file."""

    configuration = LabConfiguration(path)
    configuration.load()
    return configuration


def _handle_simulate(args: argparse.Namespace) -> int:
    try:
        config = _load_configuration(args.config)
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    requester = config.principal_by_name(args.requester)
    if not requester:
        LOGGER.error("Requester %s not found in configuration", args.requester)
        return 1

    simulation = Esc1Simulation(config)
    result = simulation.run(requester)
    LOGGER.info("%s", result.message)
    return 0 if result.success else 2


def _handle_detect(args: argparse.Namespace) -> int:
    try:
        config = _load_configuration(args.config)
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    analyzer = TemplateAnalyzer(config)
    findings = analyzer.run(show_table=not args.output_json)
    if args.output_json:
        print(json.dumps([finding.__dict__ for finding in findings], indent=2))
    LOGGER.info("Completed scan with %d findings", len(findings))
    return 0


def _handle_harden(args: argparse.Namespace) -> int:
    try:
        config = _load_configuration(args.config)
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    hardener = EkuHardener(config.certificate_templates)
    actions = hardener.apply()
    LOGGER.info("Applied %d hardening actions", len(actions))
    if args.output_json:
        print(json.dumps([action.__dict__ for action in actions], indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ADCS Lab toolkit")
    parser.add_argument("--config", type=Path, default=Path("data/sample_templates.yaml"), help="Path to lab config")

    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="Run safe attack simulations")
    simulate.add_argument("--requester", required=True, help="Requester principal name")
    simulate.set_defaults(func=_handle_simulate)

    detect = subparsers.add_parser("detect", help="Scan certificate templates for issues")
    detect.add_argument("--output-json", action="store_true", help="Emit JSON findings")
    detect.set_defaults(func=_handle_detect)

    harden = subparsers.add_parser("harden", help="Apply EKU and permission hardening")
    harden.add_argument("--output-json", action="store_true", help="Emit JSON for applied actions")
    harden.set_defaults(func=_handle_harden)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: Callable[[argparse.Namespace], int] = args.func
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
