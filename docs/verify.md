# Verifying a certificate

## Verify

Offline reference check (stdlib + `cryptography`), given a DSSE envelope and the
signer's Ed25519 public key in PEM form:

```bash
python -m governance_certification.verify certificate.dsse.json --pubkey signer.ed25519.pem
# or, once installed:
govcert-verify certificate.dsse.json --pubkey signer.ed25519.pem
```

As a library:

```python
from governance_certification.verify import verify

report = verify(envelope_dict, verify_sig=my_ed25519_verify)
# report -> {"ok": bool, "findings": [{"code", "detail"}, ...], "statement": {...}}
# ok is True only if the signature verifies AND enforced.blocked_unless_permitted is true
# AND the predicateType matches. `not-enforcement-bound` is the invention's hard reject.
```

`verify_sig(message: bytes, sig: bytes) -> bool` verifies one Ed25519 signature
over the DSSE Pre-Authentication Encoding (`DSSEv1 <len> <type> <len> <body>`).
If `jsonschema` is importable, the predicate is additionally validated against
`schema/GovernanceCertification-v1.schema.json`; the check is skipped cleanly
when it is not.

**In production, verify with Sigstore cosign** — the same DSSE/in-toto envelope
is what cosign emits and checks. `src/governance_certification/verify.py` is the minimal offline reference,
not a replacement for it.

## Status

Draft spec v1.
