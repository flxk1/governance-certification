# What this repo owns vs. composes

## What this repo owns vs. composes

This repo owns **only** the predicate schema and the thin pillar-checks in the
reference verifier — the *shape* of the five pillars and the one check that
makes the artifact enforcement-bound. Everything mechanical is composed:

- **DSSE + in-toto + Sigstore cosign** — the signed envelope, the attestation
  header, and the verify path.
- **Ed25519 (RFC 8032) + RFC 8785 (JCS)** — signing and canonicalisation.
- **PROV-O / RDF-Data-Cube** — the grounding scheme (pluggable; see below).
- **Rekor / RFC 6962** — the `intact` pillar's inclusion proof.
- **A portable oversight attestation** — the `overseen` pillar (DSSE-signed, so
  it embeds as an in-toto-compatible sub-attestation).

Out of scope here (they compose on their own standards, not on this schema):
agent identity / transport (**Web Bot Auth**, RFC 9421), human-delegation
(**HDP**), and any handshake or registry. This repo adds none of those.

## Grounding schemes are pluggable

The `grounded.scheme` field is a URI. `prov-o`, `uri-span`, and `7d+nd` are
interchangeable *values* of that field — none is privileged by the schema. A
verifier resolves whichever it understands; `grounded.digest` lets any verifier
re-check the cited span without understanding the scheme at all. There is no
bespoke scheme registry.
