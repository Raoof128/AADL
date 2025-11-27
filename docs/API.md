# API & Module Reference

This project exposes a small Python API for working with the simulated ADCS lab. The entrypoints are intentionally minimal to keep the lab portable and easy to reason about.

## Package Overview

### `adcs_lab.config_loader`
- `LabConfiguration(config_path: str | Path)`
  - `load()` – Parse and validate YAML configuration.
  - `template_by_name(name)` / `principal_by_name(name)` – Lookup helpers.
- `CertificateTemplate`, `CertificateAuthority`, `SecurityPrincipal` – Typed data classes used across the toolkit.

### `adcs_lab.attack_simulator`
- `Esc1Simulation` – Safe simulation of ESC1-style subject/SAN abuse.
- `SimulationResult` – Structured result including success flag and impacted templates.

### `adcs_lab.detection`
- `TemplateAnalyzer` – Flags misconfigurations including editable subjects, permissive EKUs, permissive enrollment rights, and long validity.
- `Finding` – Data class describing a finding, severity, and recommendation.

### `adcs_lab.hardening`
- `EkuHardener` – Applies opinionated controls (disable subject editing, require manager approval, remove Smart Card Logon EKU).
- `HardeningAction` – Data class describing modifications applied to a template.

### CLI (`adcs_lab.cli`)
- `adcs-lab simulate --requester <user>` – Run ESC1 simulation.
- `adcs-lab detect [--output-json]` – Scan template catalog.
- `adcs-lab harden [--output-json]` – Apply hardening to in-memory templates.

> All commands operate solely on local YAML configuration and do **not** touch real directory services.
