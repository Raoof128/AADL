"""Hardening helpers for simulated ADCS templates."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from rich.console import Console

from adcs_lab.config_loader import CertificateTemplate

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class HardeningAction:
    """Represents an action applied to a template."""

    template: str
    changes: List[str]


class EkuHardener:
    """Apply opinionated EKU and permission hardening to templates."""

    def __init__(self, templates: List[CertificateTemplate]) -> None:
        self.templates = templates

    def apply(self) -> List[HardeningAction]:
        """Enforce safer defaults for EKU and enrollment permissions."""

        actions: List[HardeningAction] = []
        for template in self.templates:
            changes: List[str] = []
            if template.subject_name_editable:
                template.subject_name_editable = False
                changes.append("Disabled subject name editing")
            if not template.manager_approval_required:
                template.manager_approval_required = True
                changes.append("Enabled manager approval requirement")
            if "Smart Card Logon" in template.eku and "Client Authentication" in template.eku:
                template.eku.remove("Smart Card Logon")
                changes.append("Removed Smart Card Logon EKU")
            if changes:
                actions.append(HardeningAction(template=template.name, changes=changes))
                logger.info("Hardened template %s: %s", template.name, "; ".join(changes))
        if not actions:
            logger.info("No templates required changes; already hardened.")
        else:
            for action in actions:
                console.log(f"Template {action.template} hardened", action.changes)
        return actions
