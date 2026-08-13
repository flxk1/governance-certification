# GovernanceCertification

**The invention: enforcement-bound oversight proof.** A portable attestation
that can *only* be minted as the byproduct of an action being
**blocked-unless-permitted at runtime** by a human-overseen, source-grounded
gate. Holding a valid one is *evidence the governance happened* — not a claim
that it did.

Every ingredient is standard FOSS. What is new is the **coupling**: the runtime
gate is the only thing that can mint the certificate, and it mints one only when
it actually gated. Enforcement produces the proof; the proof is unforgeable
evidence of enforcement. That binding is the whole invention.

The load-bearing pillar is `enforced.blocked_unless_permitted` — it **must** be
`true`. A verifier **must reject** any certificate where it isn't; such an
artifact certifies nothing the invention requires.

## What it is

A GovernanceCertification is an **in-toto predicate**:

- **predicateType** `https://loomground.org/attestations/GovernanceCertification/v1`
- carried in an **in-toto Statement** whose `subject` is the governed action
  (its name + a `sha256` digest of the action envelope, so the certificate is
  bound to a specific action),
- wrapped in a **DSSE envelope**, Ed25519-signed,
- **cosign-verifiable** — Sigstore cosign already signs and verifies
  in-toto/DSSE attestations, so a GovernanceCertification rides tooling that
  exists.

The predicate asserts that, at the moment it acted, an AI action was
simultaneously **grounded ∧ overseen ∧ enforced ∧ intact ∧ legitimate**.

## The five pillars

| Pillar | Attests | Reuses (FOSS) | Owns |
|---|---|---|---|
| **enforced** | blocked-unless-permitted at runtime | Claude Code PreToolUse/PostToolUse hooks; OPA/Cedar for eval (pluggable) | **the binding** — the certificate is minted only if the gate gated |
| **overseen** | a qualified human exercised oversight | DSSE + Ed25519 (RFC 8032) + RFC 8785 (JCS) | oversight-certificate disposition semantic (its own repo) |
| **grounded** | verdict rests on a cited span | PROV-O / RDF-Data-Cube / BFO; RFC 8785 digest | nothing — `scheme` is a URI; 5d+nd is one reference resolver |
| **intact** | recorded tamper-evidently | Sigstore Rekor / RFC 6962 / RFC 9162 (Trillian) | nothing — reuse an inclusion proof; native chain only as fallback |
| **legitimate** | policy anchors to real sources | Cedar/OPA/XACML (policy-as-code); ELI/ECLI, Akoma Ntoso, eyecite/EUR-Lex (legal anchors) | nothing — anchors are standard citations |

The `verdict` that produces a certificate is `permit` or `hold-approved`; a
`deny` produces none (there is nothing to certify but a refusal). For
`hold-approved` the `overseen` pillar must carry a human step; for `permit` a
human step may be absent (the grade permitted it).

## What this repo owns vs. composes

This repo owns **only** the predicate schema and the thin pillar-checks in the
reference verifier — the *shape* of the five pillars and the one check that
makes the artifact enforcement-bound. Everything mechanical is composed:

- **DSSE + in-toto + Sigstore cosign** — the signed envelope, the attestation
  header, and the verify path.
- **Ed25519 (RFC 8032) + RFC 8785 (JCS)** — signing and canonicalisation.
- **PROV-O / 5d+nd** — the grounding scheme (pluggable; see below).
- **Rekor / RFC 6962** — the `intact` pillar's inclusion proof.
- **oversight-certificate** — the `overseen` pillar (its own repo, already DSSE,
  so it embeds as an in-toto-compatible sub-attestation).

Out of scope here (they compose on their own standards, not on this schema):
agent identity / transport (**Web Bot Auth**, RFC 9421), human-delegation
(**HDP**), and any handshake or registry. This repo adds none of those.

## Verify

Offline reference check (stdlib + `cryptography`), given a DSSE envelope and the
signer's Ed25519 public key in PEM form:

```bash
python verify.py certificate.dsse.json --pubkey signer.ed25519.pem
# or, once installed:
govcert-verify certificate.dsse.json --pubkey signer.ed25519.pem
```

As a library:

```python
from verify import verify

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
is what cosign emits and checks. `verify.py` is the minimal offline reference,
not a replacement for it.

## Grounding schemes are pluggable

The `grounded.scheme` field is a URI. `5d+nd`, `7d+nd`, and `prov-o` are
interchangeable *values* of that field — none is privileged by the schema. A
verifier resolves whichever it understands; `grounded.digest` lets any verifier
re-check the cited span without understanding the scheme at all. There is no
bespoke scheme registry.

## Status

Draft spec v1.

## License

MIT — see [LICENSE](LICENSE).
