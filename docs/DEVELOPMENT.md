# Development Guide

This project treats the ADCS lab simulator as a production-grade codebase. Use the commands below to maintain quality and reproducibility.

## Environment Setup
1. Install Python 3.11 (or newer).
2. Install dependencies and dev tools:
   ```bash
   make install
   ```

## Quality Gates
- **Lint**: `make lint` (flake8, black --check, mypy)
- **Format**: `make format`
- **Tests**: `make test`

CI runs the same gates via GitHub Actions. New contributions should pass all checks locally before opening a PR.

## Code Style
- PEP 8 compliant, 4-space indentation.
- Keep line length at 120 characters (enforced by `.editorconfig` and Black config in `pyproject.toml`).
- Prefer descriptive names, explicit typing, and docstrings for every public function/class.

## Logging & Errors
- Use structured logging via the module-level logger instances.
- Validate inputs aggressively and surface actionable error messages.
- Wrap file I/O and parsing (`yaml.safe_load`) with exception handling to avoid noisy tracebacks.

## Testing Guidance
- Unit tests live under `tests/` and use `pytest`.
- Add regression tests alongside new features, especially for CLI exit codes and configuration validation paths.

## Security Posture
- Never embed real credentials or keys; configuration files must stay synthetic.
- Keep network operations disabled by default; the lab is designed for isolated environments only.
