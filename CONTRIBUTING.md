# Contributing Guidelines

Thank you for contributing to the ADCS Attack & Defence Lab! Contributions should keep the project safe, self-contained, and enterprise-grade.

## Development Workflow

1. Fork and branch from `work`.
2. Install dependencies: `pip install -r requirements.txt -e .[dev]`.
3. Run formatting and tests:
   ```bash
   flake8 src tests
   pytest
   ```
4. Update documentation and examples for any user-facing change.
5. Ensure new code includes type hints, docstrings, and logging.
6. Submit a pull request with a clear description and reference to any issues.

## Code Style

- Python: PEP 8, type hints required.
- IaC: Terraform fmt and Ansible lint before committing.
- Avoid hard-coded secrets and external network calls.

## Security

- The lab must remain **simulation-only**. Do not add code that interacts with production AD or PKI.
- Follow the [Security Policy](SECURITY.md) for reporting vulnerabilities.

## Documentation

- Maintain `README.md`, `ARCHITECTURE.md`, and relevant docs in `docs/`.
- Include diagrams (Mermaid) where architecture changes.
- Provide examples and usage notes for new scripts.

## Testing

- Add unit tests for new Python modules under `tests/`.
- Use sample data in `data/` to avoid external dependencies.

Thank you for helping keep this lab professional, safe, and useful!
