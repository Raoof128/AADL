"""Detection toolkit for ADCS misconfigurations in the simulated lab."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from rich.console import Console
from rich.table import Table

from adcs_lab.config_loader import CertificateTemplate, LabConfiguration

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class Finding:
    """Represents a misconfiguration finding."""

    template: str
    severity: str
    description: str
    recommendation: str


class TemplateAnalyzer:
    """Analyze certificate templates for common ESC conditions."""

    def __init__(self, configuration: LabConfiguration) -> None:
        self.configuration = configuration

    def evaluate_template(self, template: CertificateTemplate) -> List[Finding]:
        """Return a list of findings for a template."""

        findings: List[Finding] = []
        if template.subject_name_editable and not template.manager_approval_required:
            findings.append(
                Finding(
                    template=template.name,
                    severity="high",
                    description="Subject name is editable without manager approval (ESC1 risk).",
                    recommendation="Disable subject editing or require manager approval.",
                )
            )
        if "Client Authentication" in template.eku and "Smart Card Logon" in template.eku:
            findings.append(
                Finding(
                    template=template.name,
                    severity="medium",
                    description="Template issues certificates usable for interactive logon.",
                    recommendation="Restrict EKUs to intended purposes and enforce approvals.",
                )
            )
        if self._has_overly_permissive_rights(template.enrollment_rights):
            findings.append(
                Finding(
                    template=template.name,
                    severity="medium",
                    description="Enrollment rights allow broad domain groups (potential privilege escalation).",
                    recommendation="Restrict enrollment to dedicated security groups and require approvals.",
                )
            )
        if template.validity_days > 365:
            findings.append(
                Finding(
                    template=template.name,
                    severity="low",
                    description="Certificate lifetime exceeds 1 year.",
                    recommendation="Shorten lifetime to reduce exposure.",
                )
            )
        return findings

    def run(self, *, show_table: bool = True) -> List[Finding]:
        """Evaluate all templates and optionally print a summary table."""

        all_findings: List[Finding] = []
        table = Table(title="Template Misconfiguration Scan")
        table.add_column("Template")
        table.add_column("Severity")
        table.add_column("Description")
        for template in self.configuration.certificate_templates:
            findings = self.evaluate_template(template)
            all_findings.extend(findings)
            for finding in findings:
                table.add_row(finding.template, finding.severity, finding.description)
        if all_findings:
            if show_table:
                console.print(table)
        else:
            logger.info("No misconfigurations identified in loaded templates.")
        return all_findings

    @staticmethod
    def _has_overly_permissive_rights(enrollment_rights: List[str]) -> bool:
        """Flag templates that include broad domain groups in enrollment rights."""

        permissive_groups = {"domain users", "authenticated users", "everyone"}
        return any(right.lower() in permissive_groups for right in enrollment_rights)
