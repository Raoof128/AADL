"""CLI wrapper that applies EKU and permission hardening in the lab config."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List

from adcs_lab import EkuHardener, LabConfiguration

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


DEFAULT_CONFIG_PATH = Path("data/sample_templates.yaml")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the EKU hardener wrapper."""

    parser = argparse.ArgumentParser(description="Harden EKU and permissions for lab templates")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to lab config")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    """Run EKU hardening and return a process exit code."""

    args = parse_args(argv)
    try:
        config = LabConfiguration(args.config)
        config.load()
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    hardener = EkuHardener(config.certificate_templates)
    actions = hardener.apply()
    LOGGER.info("Applied %d hardening actions", len(actions))
    return 0 if actions else 1


if __name__ == "__main__":
    raise SystemExit(main())
