"""Standalone ESC1 simulation wrapper for targeted demos.

This wrapper mirrors the behaviour of the unified CLI while remaining
lightweight for targeted ESC1 exercises. It validates configuration loading and
the requester principal before running the simulation to ensure predictable
outcomes in training environments.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List

from adcs_lab import Esc1Simulation, LabConfiguration

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


DEFAULT_CONFIG_PATH = Path("data/sample_templates.yaml")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the ESC1 simulation wrapper."""

    parser = argparse.ArgumentParser(description="Run ESC1 simulation against lab config")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to lab YAML config")
    parser.add_argument("--requester", type=str, default="alice", help="Security principal requesting enrollment")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    """Execute the ESC1 simulation and return a process exit code."""

    args = parse_args(argv)
    try:
        config = LabConfiguration(args.config)
        config.load()
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    requester = config.principal_by_name(args.requester)
    if not requester:
        LOGGER.error("Requester %s not defined in configuration", args.requester)
        return 1

    simulation = Esc1Simulation(config)
    result = simulation.run(requester)
    status = "SUCCESS" if result.success else "BLOCKED"
    LOGGER.info("%s: %s", status, result.message)
    return 0 if result.success else 2


if __name__ == "__main__":
    raise SystemExit(main())
