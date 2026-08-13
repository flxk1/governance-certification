# SPDX-License-Identifier: MIT
"""Self-contained tests for the GovernanceCertification reference verifier.

Generates a throwaway Ed25519 key in-test, builds a minimal valid DSSE envelope,
and exercises the three load-bearing outcomes: a valid certificate verifies; a
certificate whose ``enforced.blocked_unless_permitted`` is false is rejected as
``not-enforcement-bound``; a corrupted signature is rejected.
"""
import base64
import json
import os
import sys

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import verify as gv  # noqa: E402


def _keypair():
    """A fresh Ed25519 keypair as (sign, verify_sig) closures."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    def sign(message: bytes) -> bytes:
        return private_key.sign(message)

    def verify_sig(message: bytes, sig: bytes) -> bool:
        try:
            public_key.verify(sig, message)
            return True
        except InvalidSignature:
            return False

    return sign, verify_sig


def _predicate(*, blocked: bool = True) -> dict:
    """A minimal, schema-valid five-pillar predicate."""
    return {
        "verdict": "permit",
        "action_class": "shell.exec",
        "issued_at": "2026-08-13T00:00:00Z",
        "enforced": {
            "mechanism": "claude-code:PreToolUse",
            "blocked_unless_permitted": blocked,
            "decision_ref": "audit-0001",
        },
        "overseen": {"required": False},
        "grounded": {
            "scheme": "https://loomground.org/grounding/5d+nd/v1",
            "ref": "span:cmd[0:12]",
            "digest": {"sha256": "0" * 64},
        },
        "intact": {
            "type": "native-chain",
            "log_id": "folder-demo",
            "entry_ref": "audit-0001",
        },
        "legitimate": {"policy_fingerprint": "deadbeefcafef00d"},
    }


def _envelope(sign, *, blocked: bool = True) -> dict:
    """Build and DSSE-sign an in-toto Statement carrying the predicate."""
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "shell.exec", "digest": {"sha256": "1" * 64}}],
        "predicateType": gv.PREDICATE_TYPE,
        "predicate": _predicate(blocked=blocked),
    }
    body = json.dumps(statement, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = sign(gv._pae(gv._DSSE_PAYLOAD_TYPE, body))
    return {
        "payloadType": gv._DSSE_PAYLOAD_TYPE,
        "payload": base64.b64encode(body).decode("ascii"),
        "signatures": [
            {"keyid": "test-key", "sig": base64.b64encode(sig).decode("ascii")},
        ],
    }


def test_valid_certificate_verifies():
    sign, verify_sig = _keypair()
    report = gv.verify(_envelope(sign, blocked=True), verify_sig=verify_sig)
    assert report["ok"] is True, report["findings"]
    assert report["findings"] == []
    assert report["statement"]["predicateType"] == gv.PREDICATE_TYPE


def test_not_enforcement_bound_is_rejected():
    sign, verify_sig = _keypair()
    report = gv.verify(_envelope(sign, blocked=False), verify_sig=verify_sig)
    assert report["ok"] is False
    codes = {f["code"] for f in report["findings"]}
    assert "not-enforcement-bound" in codes


def test_corrupted_signature_is_rejected():
    sign, verify_sig = _keypair()
    envelope = _envelope(sign, blocked=True)
    raw = bytearray(base64.b64decode(envelope["signatures"][0]["sig"]))
    raw[-1] ^= 0xFF  # flip the final byte of the signature
    envelope["signatures"][0]["sig"] = base64.b64encode(bytes(raw)).decode("ascii")
    report = gv.verify(envelope, verify_sig=verify_sig)
    assert report["ok"] is False
    codes = {f["code"] for f in report["findings"]}
    assert "bad-signature" in codes
