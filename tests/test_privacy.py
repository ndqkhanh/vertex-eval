import pytest

from vertex_eval.privacy import enforce_tenant, redact, redact_dict


def test_redact_email():
    assert redact("contact me at bob@example.com") == "contact me at [EMAIL]"


def test_redact_phone():
    assert "[PHONE]" in redact("tel: +1 (555) 123-4567")


def test_redact_credit_card_and_ssn():
    assert "[CARD]" in redact("card 4111 1111 1111 1111 expires soon")
    assert "[SSN]" in redact("ssn 123-45-6789 on file")


def test_redact_empty_is_noop():
    assert redact("") == ""


def test_enforce_tenant_allows_match():
    enforce_tenant("acme", "acme")


def test_enforce_tenant_rejects_mismatch():
    with pytest.raises(PermissionError):
        enforce_tenant("acme", "other")


def test_redact_dict_walks_nested_strings():
    d = {"top": "bob@example.com", "nested": {"inner": "call 555-123-4567"}}
    out = redact_dict(d)
    assert out["top"] == "[EMAIL]"
    assert "[PHONE]" in out["nested"]["inner"]
