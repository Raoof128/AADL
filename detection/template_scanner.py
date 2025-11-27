"""CLI utility to scan certificate templates for misconfigurations."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List

from adcs_lab import LabConfiguration, TemplateAnalyzer

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


DEFAULT_CONFIG_PATH = Path("data/sample_templates.yaml")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the template scanner."""

    parser = argparse.ArgumentParser(description="Scan template definitions for ESC risks")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to lab config")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    """Run the template scanner and return a process exit code."""

    args = parse_args(argv)
    try:
        config = LabConfiguration(args.config)
        config.load()
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Unable to load configuration: %s", exc)
        return 3

    analyzer = TemplateAnalyzer(config)
    findings = analyzer.run()
    LOGGER.info("Completed scan with %d findings", len(findings))
    return 0 if findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
