# ADCS Attack & Defence Training Manual

## PKI Basics
- Enterprise PKI relies on a trusted root CA, optional subordinate CAs, and certificate templates that define issuance policy.
- ADCS integrates with Active Directory to publish templates, NTAuth entries, and enrollment services.

## ESC Scenarios (Summary)
- **ESC1**: Editable subject names + no manager approval enables impersonation.
- **ESC2**: Enrollment policy service allows arbitrary requestor identities.
- **ESC3**: Misissued subordinate CA certs enabling rogue signing.
- **ESC4**: NTAuth store trusts unvetted CAs.
- **ESC6**: EKU misconfiguration enables authentication with unintended certificates.
- **ESC7**: Request tampering during submission or approval.
- **ESC8**: Dangerous template permissions (ENROLL/AUTOENROLL + owner rights).

## Attack Chain Walkthrough (Simulation)
1. Attacker enumerates templates and identifies ESC1-Template allowing subject editing.
2. Using `attacks/esc1_simulation.py`, attacker requests a certificate with a privileged UPN.
3. Certificate is minted locally (simulated), granting attacker ability to authenticate as privileged user.
4. Detection toolkit flags editable subject and dual EKU; hardening removes risky EKUs and enforces approval.

## Hardening Playbook (Zero Trust PKI)
- Enforce **manager approval** and disable **subject editing** on all logon-capable templates.
- Restrict EKUs to the minimal required set; avoid combining `Smart Card Logon` with `Client Authentication` unless audited.
- Publish only trusted CAs to **NTAuth**; regularly review contents.
- Disable legacy protocols (HTTP enrollment without TLS, DCOM where possible) in favor of mTLS.
- Use strong key sizes (RSA 4096/ECC) and short validity periods.
- Monitor enrollment events for unusual requesters and template usage.

## DFIR Analyst Playbook
- Collect ADCS logs (event IDs 4886-4890) and Sysmon network events.
- Correlate certificate requesters with Kerberos/NTLM authentications.
- Flag templates where `ENROLL` is granted to broad groups with subject editing enabled.
- Validate NTAuth contents against expected CA list.

## Administrator Checklist
- Run `python detection/template_scanner.py` weekly against exported template data.
- Apply `python defence/eku_lockdown.py` after validating impact in a test lab.
- Reconcile Terraform/Ansible state with desired hardening baselines.
- Keep the dashboard up to date with current detections and hardening score.
