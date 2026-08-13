# SPDX-License-Identifier: MIT
# Copyright 2026 flxk1
"""GovernanceCertification v1 — minimal offline reference verifier.

A GovernanceCertification is an in-toto predicate
(predicateType ``https://loomground.org/attestations/GovernanceCertification/v1``)
riding a DSSE-signed in-toto Statement whose ``subject`` is the governed action.
It asserts that, at the moment it acted, an AI action was simultaneously
grounded, overseen, enforced, intact and legitimate.

The load-bearing property is ``enforced.blocked_unless_permitted``: the
certificate is only issuable because the action passed through a runtime gate
that would OTHERWISE have blocked it. A verifier MUST reject any instance where
that flag is not ``True`` — such an artifact certifies nothing the invention
requires.

**In production, verify with Sigstore cosign** — it already carries and checks
in-toto/DSSE attestations, so a GovernanceCertification rides tooling that
exists. This module is the minimal, dependency-light OFFLINE reference: it
reimplements only the DSSE Pre-Authentication-Encoding check and the five-pillar
predicate checks, using the Python stdlib plus ``cryptography`` for Ed25519.
It mirrors the reference implementation's verifier.

Optional soft dependency: if ``jsonschema`` is importable, the predicate is also
validated against ``schema/GovernanceCertification-v1.schema.json``; if it is
absent the check is skipped cleanly.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from typing import Callable, Optional

PREDICATE_TYPE = "https://loomground.org/attestations/GovernanceCertification/v1"
_DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "schema", "GovernanceCertification-v1.schema.json",
)


def _pae(payload_type: str, body: bytes) -> bytes:
    """DSSE Pre-Authentication Encoding — the exact bytes that were signed.

    Spec-exact: ``DSSEv1 <len(type)> <type> <len(body)> <body>``.
    """
    t = payload_type.encode("utf-8")
    return (b"DSSEv1 " + str(len(t)).encode() + b" " + t + b" "
            + str(len(body)).encode() + b" " + body)


def _schema_findings(predicate: dict) -> list:
    """Optionally validate the predicate against the JSON Schema.

    Soft dependency: returns no findings (and does not fail) when ``jsonschema``
    or the schema file is unavailable.
    """
    try:
        import jsonschema  # type: ignore
    except Exception:
        return []
    try:
        with open(_SCHEMA_PATH, "r", encoding="utf-8") as fh:
            schema = json.load(fh)
    except Exception:
        return []
    validator = jsonschema.Draft202012Validator(schema)
    return [
        {"code": "schema-invalid",
         "detail": f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"}
        for err in sorted(validator.iter_errors(predicate), key=lambda e: list(e.path))
    ]


def verify(envelope: dict, *, verify_sig: Callable[[bytes, bytes], bool]) -> dict:
    """Offline re-check of a GovernanceCertification DSSE envelope.

    ``verify_sig(message: bytes, sig: bytes) -> bool`` verifies one Ed25519
    signature over the DSSE PAE. Returns ``{ok, findings, statement}``:

    * ``ok`` — True only when the signature verifies AND no findings were raised.
    * ``findings`` — a list of ``{code, detail}`` problems (empty when clean).
    * ``statement`` — the decoded in-toto Statement (or ``None`` on decode error).

    Checks, mirroring the reference minter/verifier:
      (a) base64-decode the payload, recompute the DSSE PAE, verify the signature;
      (b) ``predicateType`` matches the owned type URI;
      (c) REJECT with ``not-enforcement-bound`` unless
          ``predicate.enforced.blocked_unless_permitted`` is ``True`` — the
          load-bearing pillar (the invention);
      (d) if ``jsonschema`` is importable, validate the predicate against the
          schema (soft; skipped cleanly when absent).
    """
    try:
        payload = base64.b64decode(envelope["payload"])
        pae = _pae(str(envelope.get("payloadType", _DSSE_PAYLOAD_TYPE)), payload)
        sig_ok = any(
            verify_sig(pae, base64.b64decode(s["sig"]))
            for s in (envelope.get("signatures") or [])
        )
        statement = json.loads(payload)
        predicate = statement.get("predicate") or {}

        findings: list = []
        if statement.get("predicateType") != PREDICATE_TYPE:
            findings.append({"code": "wrong-predicate-type",
                             "detail": str(statement.get("predicateType"))})
        # (c) THE load-bearing pillar. Without this true, it is a claim, not proof.
        if (predicate.get("enforced") or {}).get("blocked_unless_permitted") is not True:
            findings.append({
                "code": "not-enforcement-bound",
                "detail": "enforced.blocked_unless_permitted is not true — "
                          "this certifies nothing the invention requires",
            })
        findings.extend(_schema_findings(predicate))
        if not sig_ok:
            findings.append({"code": "bad-signature",
                             "detail": "DSSE signature did not verify"})
        return {"ok": sig_ok and not findings, "findings": findings,
                "statement": statement}
    except Exception as exc:  # never raise out of a verifier
        return {"ok": False, "statement": None,
                "findings": [{"code": "verify-error",
                              "detail": f"{type(exc).__name__}: {exc}"}]}


def ed25519_verifier_from_pem(pem_bytes: bytes) -> Callable[[bytes, bytes], bool]:
    """Build a ``verify_sig`` closure from an Ed25519 public key in PEM form."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    public_key = load_pem_public_key(pem_bytes)

    def verify_sig(message: bytes, sig: bytes) -> bool:
        try:
            public_key.verify(sig, message)  # Ed25519: verify(signature, data)
            return True
        except InvalidSignature:
            return False

    return verify_sig


def main(argv: Optional[list] = None) -> int:
    """CLI: ``govcert-verify <envelope.json> --pubkey <ed25519.pem>``."""
    ap = argparse.ArgumentParser(
        prog="govcert-verify",
        description="Offline reference verifier for a GovernanceCertification "
                    "DSSE envelope (in production, use Sigstore cosign).",
    )
    ap.add_argument("envelope", help="path to a DSSE envelope JSON file")
    ap.add_argument("--pubkey", required=True,
                    help="path to the signer's Ed25519 public key (PEM)")
    args = ap.parse_args(argv)

    with open(args.envelope, "rb") as fh:
        envelope = json.load(fh)
    with open(args.pubkey, "rb") as fh:
        verify_sig = ed25519_verifier_from_pem(fh.read())

    report = verify(envelope, verify_sig=verify_sig)
    print("OK" if report["ok"] else "REJECTED")
    for finding in report["findings"]:
        print(f"  - {finding['code']}: {finding['detail']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
