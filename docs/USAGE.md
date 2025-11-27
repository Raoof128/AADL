# Usage Examples

## Local Simulations (Unified CLI)
- Run ESC1 simulation for a standard user:
  ```bash
  adcs-lab simulate --requester alice
  ```
- Scan templates:
  ```bash
  adcs-lab detect --output-json
  ```
- Apply hardening:
  ```bash
  adcs-lab harden --output-json
  ```

Exit codes:
- `0` – success.
- `1` – requester missing from configuration.
- `2` – simulation ran but no vulnerable templates accessible.
- `3` – configuration failed to load or validate (file missing, duplicate names, or invalid parent references).

## IaC Workflow
1. `cd infra/terraform && terraform init && terraform apply` (uses placeholders; replace with your provider modules).
2. `cd ../ansible && ansible-playbook -i inventory.ini setup-lab.yml` to configure roles.

## Dashboard
Open `dashboard/index.html` in your browser; extend `pki_graph.js` to point at generated JSON from detections.
