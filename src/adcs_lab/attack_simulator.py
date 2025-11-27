"""Simulated ADCS attack modules.

The simulations use lab configuration data to demonstrate ESC-style issues
without touching real Active Directory environments.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from rich.table import Table
from rich.console import Console

from adcs_lab.config_loader import LabConfiguration, CertificateTemplate, SecurityPrincipal

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class SimulationResult:
    """Represents the outcome of a simulated attack."""

    success: bool
    message: str
    impacted_templates: List[str]


class Esc1Simulation:
    """Simulate ESC1 (user certificate mapping abuse).

    ESC1 occurs when an attacker can request a certificate that allows
    arbitrary subject alternative names (SAN) or subject names. This
    simulation checks for templates that allow subject editing and lack
    manager approval.
    """

    def __init__(self, configuration: LabConfiguration) -> None:
        self.configuration = configuration

    def _template_is_esc1(self, template: CertificateTemplate) -> bool:
        """Assess whether a template is ESC1-like."""

        return template.subject_name_editable and not template.manager_approval_required

    def run(self, requester: SecurityPrincipal) -> SimulationResult:
        """Execute the simulation for a given security principal."""

        logger.info("Running ESC1 simulation for requester %s", requester.name)
        vulnerable_templates = [
            template for template in self.configuration.certificate_templates if self._template_is_esc1(template)
        ]

        eligible_templates = [
            template
            for template in vulnerable_templates
            if any(group in template.enrollment_rights for group in requester.groups)
        ]

        if not eligible_templates:
            return SimulationResult(
                success=False,
                message="No ESC1-prone templates are accessible to the requester.",
                impacted_templates=[],
            )

        table = Table(title="ESC1 Simulation")
        table.add_column("Template")
        table.add_column("Reason")
        for template in eligible_templates:
            reason = "Subject editable; manager approval disabled"
            table.add_row(template.name, reason)
        console.print(table)

        return SimulationResult(
            success=True,
            message="Requester can enroll in ESC1-prone templates leading to privilege escalation.",
            impacted_templates=[template.name for template in eligible_templates],
        )
