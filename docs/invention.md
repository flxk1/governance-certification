# The invention: enforcement-bound oversight proof


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
| **overseen** | a qualified human exercised oversight | DSSE + Ed25519 (RFC 8032) + RFC 8785 (JCS) | a portable, DSSE-signed oversight attestation |
| **grounded** | verdict rests on a cited span | PROV-O / RDF-Data-Cube / BFO; RFC 8785 digest | nothing — `scheme` is a URI; resolvers are external |
| **intact** | recorded tamper-evidently | Sigstore Rekor / RFC 6962 / RFC 9162 (Trillian) | nothing — reuse an inclusion proof; native chain only as fallback |
| **legitimate** | policy anchors to real sources | Cedar/OPA/XACML (policy-as-code); ELI/ECLI, Akoma Ntoso, eyecite/EUR-Lex (legal anchors) | nothing — anchors are standard citations |

The `verdict` that produces a certificate is `permit` or `hold-approved`; a
`deny` produces none (there is nothing to certify but a refusal). For
`hold-approved` the `overseen` pillar must carry a human step; for `permit` a
human step may be absent (the grade permitted it).
