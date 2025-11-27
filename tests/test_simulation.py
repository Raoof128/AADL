import json

import pytest

from adcs_lab import Esc1Simulation, LabConfiguration, TemplateAnalyzer, EkuHardener
from adcs_lab.cli import main as cli_main


def load_config():
    config = LabConfiguration("data/sample_templates.yaml")
    config.load()
    return config


def test_esc1_simulation_finds_vulnerable_template():
    config = load_config()
    requester = next(p for p in config.security_principals if p.name == "alice")
    result = Esc1Simulation(config).run(requester)
    assert result.success is True
    assert "ESC1-Template" in result.impacted_templates


def test_template_analyzer_flags_subject_editing():
    config = load_config()
    findings = TemplateAnalyzer(config).run()
    assert any(f.template == "ESC1-Template" for f in findings)


def test_template_analyzer_flags_permissive_enrollment():
    config = load_config()
    findings = TemplateAnalyzer(config).run()
    assert any("Enrollment rights" in f.description for f in findings)


def test_hardener_disables_subject_editing():
    config = load_config()
    actions = EkuHardener(config.certificate_templates).apply()
    hardened = {action.template: action.changes for action in actions}
    assert "ESC1-Template" in hardened
    assert any("Disabled subject name editing" in change for change in hardened["ESC1-Template"])


def test_invalid_configuration_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(
        """
certificate_templates:
  - name: MissingFields
certificate_authorities: []
security_principals: []
        """,
        encoding="utf-8",
    )
    config = LabConfiguration(bad_file)
    with pytest.raises(ValueError) as exc:
        config.load()
    assert "Missing keys" in str(exc.value) or "missing required sections" in str(exc.value).lower()


def test_duplicate_names_raise(tmp_path):
    bad_file = tmp_path / "dup.yaml"
    bad_file.write_text(
        """
certificate_templates:
  - name: dup
    eku: ["Client Authentication"]
    enrollment_rights: ["Domain Users"]
    manager_approval_required: false
    subject_name_editable: true
    superseded_templates: []
    validity_days: 180
    owner: "PKI Admins"
  - name: DUP
    eku: ["Client Authentication"]
    enrollment_rights: ["Domain Users"]
    manager_approval_required: false
    subject_name_editable: true
    superseded_templates: []
    validity_days: 180
    owner: "PKI Admins"
certificate_authorities: []
security_principals: []
        """,
        encoding="utf-8",
    )
    config = LabConfiguration(bad_file)
    with pytest.raises(ValueError) as exc:
        config.load()
    assert "Duplicate certificate template" in str(exc.value)


def test_invalid_yaml_file_raises_value_error(tmp_path):
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("::notyaml::", encoding="utf-8")
    config = LabConfiguration(invalid_file)
    with pytest.raises(ValueError):
        config.load()


def test_invalid_parent_reference_raises(tmp_path):
    bad_file = tmp_path / "bad_ca.yaml"
    bad_file.write_text(
        """
certificate_authorities:
  - name: child
    role: subordinate
    parent: missing
    location: lab
    nt_auth_published: true
    eku: ["Client Authentication"]
certificate_templates: []
security_principals: []
        """,
        encoding="utf-8",
    )
    config = LabConfiguration(bad_file)
    try:
        config.load()
    except ValueError as exc:
        assert "references missing parent" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid CA parent")


def test_cli_detect_outputs_json(capsys):
    exit_code = cli_main(["--config", "data/sample_templates.yaml", "detect", "--output-json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert isinstance(parsed, list)


def test_cli_missing_config_returns_error(tmp_path):
    missing_file = tmp_path / "missing.yaml"
    exit_code = cli_main(["--config", str(missing_file), "detect"])
    assert exit_code == 3
