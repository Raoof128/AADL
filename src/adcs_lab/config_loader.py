"""Configuration loading utilities for the ADCS Lab.

This module provides safe parsing of YAML configuration files that define
certificate authorities, certificate templates, and security principals used
throughout the simulated lab. The configuration format intentionally mirrors
high-level ADCS concepts without attempting to modify real directory services.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class CertificateTemplate:
    """Represents a certificate template in the simulated lab."""

    name: str
    eku: List[str]
    enrollment_rights: List[str]
    manager_approval_required: bool
    subject_name_editable: bool
    superseded_templates: List[str]
    validity_days: int
    owner: str


@dataclass
class CertificateAuthority:
    """Represents a CA definition in the lab."""

    name: str
    role: str
    location: str
    nt_auth_published: bool
    eku: List[str]
    parent: str | None = None


@dataclass
class SecurityPrincipal:
    """Represents a user or group with enrollment permissions."""

    name: str
    groups: List[str]
    can_edit_subject: bool


class LabConfiguration:
    """Loads and stores lab configuration data.

    The class centralises access to templates, certificate authorities, and
    principals for use by attack simulations, detection tooling, and
    hardening recommendations.
    """

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
        self.certificate_templates: List[CertificateTemplate] = []
        self.certificate_authorities: List[CertificateAuthority] = []
        self.security_principals: List[SecurityPrincipal] = []

    def load(self) -> None:
        """Load YAML configuration from disk with validation.

        The loader enforces presence and type correctness for the expected
        collections so that downstream modules can rely on structured data.
        """

        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ValueError(f"YAML parsing error in {self.config_path}: {exc}") from exc

        if loaded is None:
            raise ValueError("Configuration file is empty; expected YAML content.")
        if not isinstance(loaded, dict):
            raise ValueError("Configuration root must be a mapping/dictionary.")

        required_root_keys = {"certificate_templates", "certificate_authorities", "security_principals"}
        if not required_root_keys.issubset(loaded):
            missing = required_root_keys.difference(loaded)
            raise ValueError("Configuration is missing required sections: " + ", ".join(sorted(missing)))

        self.data = loaded
        self.certificate_templates = [
            self._build_template(template) for template in self._validate_collection(loaded, "certificate_templates")
        ]
        self._ensure_unique_names(self.certificate_templates, "certificate template")
        self.certificate_authorities = [
            self._build_ca(ca) for ca in self._validate_collection(loaded, "certificate_authorities")
        ]
        self._ensure_unique_names(self.certificate_authorities, "certificate authority")
        self.security_principals = [
            self._build_principal(principal) for principal in self._validate_collection(loaded, "security_principals")
        ]
        self._ensure_unique_names(self.security_principals, "security principal")
        self._validate_ca_relationships()

        logger.info(
            "Loaded configuration: %d templates, %d CAs, %d principals",
            len(self.certificate_templates),
            len(self.certificate_authorities),
            len(self.security_principals),
        )

    def template_by_name(self, name: str) -> CertificateTemplate | None:
        """Retrieve a certificate template by name."""

        for template in self.certificate_templates:
            if template.name.lower() == name.lower():
                return template
        return None

    def principal_by_name(self, name: str) -> Optional[SecurityPrincipal]:
        """Retrieve a security principal by name."""

        for principal in self.security_principals:
            if principal.name.lower() == name.lower():
                return principal
        return None

    @staticmethod
    def _validate_collection(data: Dict[str, Any], key: str) -> Iterable[Dict[str, Any]]:
        """Validate that a collection key exists and is iterable.

        Parameters
        ----------
        data: Dict[str, Any]
            Parsed YAML data.
        key: str
            Expected key containing a list of dictionaries.
        """

        collection = data.get(key, [])
        if collection is None:
            return []
        if not isinstance(collection, list):
            raise ValueError(f"Expected list for '{key}' but received {type(collection).__name__}")
        for element in collection:
            if not isinstance(element, dict):
                raise ValueError(f"Each item in '{key}' must be a mapping; received {type(element).__name__}")
        return collection

    @staticmethod
    def _build_template(template: Dict[str, Any]) -> CertificateTemplate:
        """Construct a certificate template with validation."""

        required_fields = [
            "name",
            "eku",
            "enrollment_rights",
            "manager_approval_required",
            "subject_name_editable",
            "superseded_templates",
            "validity_days",
            "owner",
        ]
        LabConfiguration._ensure_required(template, required_fields, "certificate template")
        return CertificateTemplate(
            name=str(template["name"]),
            eku=LabConfiguration._ensure_list_of_strings(template["eku"], "eku"),
            enrollment_rights=LabConfiguration._ensure_list_of_strings(
                template["enrollment_rights"], "enrollment_rights"
            ),
            manager_approval_required=bool(template["manager_approval_required"]),
            subject_name_editable=bool(template["subject_name_editable"]),
            superseded_templates=LabConfiguration._ensure_list_of_strings(
                template.get("superseded_templates", []), "superseded_templates"
            ),
            validity_days=int(template["validity_days"]),
            owner=str(template["owner"]),
        )

    @staticmethod
    def _build_ca(ca: Dict[str, Any]) -> CertificateAuthority:
        """Construct a certificate authority with validation."""

        required_fields = ["name", "role", "location", "nt_auth_published", "eku"]
        LabConfiguration._ensure_required(ca, required_fields, "certificate authority")
        return CertificateAuthority(
            name=str(ca["name"]),
            role=str(ca["role"]),
            location=str(ca["location"]),
            nt_auth_published=bool(ca["nt_auth_published"]),
            eku=LabConfiguration._ensure_list_of_strings(ca["eku"], "eku"),
            parent=str(ca.get("parent")) if ca.get("parent") else None,
        )

    @staticmethod
    def _build_principal(principal: Dict[str, Any]) -> SecurityPrincipal:
        """Construct a security principal with validation."""

        required_fields = ["name", "groups", "can_edit_subject"]
        LabConfiguration._ensure_required(principal, required_fields, "security principal")
        return SecurityPrincipal(
            name=str(principal["name"]),
            groups=LabConfiguration._ensure_list_of_strings(principal["groups"], "groups"),
            can_edit_subject=bool(principal["can_edit_subject"]),
        )

    @staticmethod
    def _ensure_required(data: Dict[str, Any], keys: List[str], label: str) -> None:
        """Ensure all required keys exist in a dictionary."""

        missing = [key for key in keys if key not in data]
        if missing:
            raise ValueError(f"Missing keys in {label}: {', '.join(missing)}")

    @staticmethod
    def _ensure_list_of_strings(value: Any, field: str) -> List[str]:
        """Ensure a field is a list of strings."""

        if not isinstance(value, list):
            raise ValueError(f"Field '{field}' must be a list of strings")
        converted = [str(item) for item in value]
        return converted

    @staticmethod
    def _ensure_unique_names(items: List[Any], label: str) -> None:
        """Ensure that dataclass-like objects have unique case-insensitive names.

        Unique naming prevents ambiguous lookups and reporting in simulation output.
        """

        seen: set[str] = set()
        for item in items:
            name = getattr(item, "name", "").lower()
            if not name:
                raise ValueError(f"{label.title()} name cannot be empty")
            if name in seen:
                raise ValueError(f"Duplicate {label} name detected: {getattr(item, 'name', '')}")
            seen.add(name)

    def _validate_ca_relationships(self) -> None:
        """Validate that certificate authority parent references are consistent."""

        ca_names = {ca.name for ca in self.certificate_authorities}
        for ca in self.certificate_authorities:
            if ca.parent:
                if ca.parent not in ca_names:
                    raise ValueError(f"Certificate authority '{ca.name}' references missing parent '{ca.parent}'")
                if ca.parent == ca.name:
                    raise ValueError("Certificate authority cannot be its own parent")
