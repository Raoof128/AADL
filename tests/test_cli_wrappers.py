import pytest

from attacks.esc1_simulation import main as esc1_main
from defence.eku_lockdown import main as harden_main
from detection.template_scanner import main as scanner_main


@pytest.mark.parametrize(
    "argv,expected",
    [
        ([], 0),
        (["--requester", "unknown"], 1),
    ],
)
def test_esc1_wrapper_exit_codes(argv, expected):
    assert esc1_main(argv) == expected


def test_template_scanner_wrapper_success():
    assert scanner_main([]) == 0


def test_template_scanner_wrapper_missing_config(tmp_path):
    missing = tmp_path / "missing.yaml"
    assert scanner_main(["--config", str(missing)]) == 3


def test_eku_lockdown_wrapper_success():
    assert harden_main([]) == 0


def test_eku_lockdown_wrapper_missing_config(tmp_path):
    missing = tmp_path / "missing.yaml"
    assert harden_main(["--config", str(missing)]) == 3
