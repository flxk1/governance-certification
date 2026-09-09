# governance-certification

In-toto predicate schema and reference verifier for GovernanceCertification, an attestation a runtime gate mints for one governed action.

## Install

`pip install "governance-certification[schema] @ git+https://github.com/flxk1/governance-certification"`

## Usage

```
govcert-verify certificate.dsse.json --pubkey signer.ed25519.pem
```

## Interface

- predicateType `https://loomground.org/attestations/GovernanceCertification/v1`, carried in a DSSE envelope, Ed25519-signed; subject = action name + sha256 of the action envelope
- required pillars: `enforced` (`blocked_unless_permitted` const `true`) · `overseen` · `grounded` · `intact` · `legitimate`
- verdict: `permit` | `hold-approved`
- verifier: `governance_certification.verify.verify(envelope, verify_sig=…) -> {ok, findings, statement}`; hard reject `not-enforcement-bound`
- schema: `schema/GovernanceCertification-v1.schema.json`

## Family

Family index of the assurance artifacts. Pillars: grounding [5d-nd](https://github.com/flxk1/5d-nd) · oversight [oversight-certificate](https://github.com/flxk1/oversight-certificate) · enforcement state [enforcement-posture](https://github.com/flxk1/enforcement-posture) · observed effects [effect-reconciliation](https://github.com/flxk1/effect-reconciliation) · source validity [norm-freshness](https://github.com/flxk1/norm-freshness) · attached duties [obligation-discharge](https://github.com/flxk1/obligation-discharge). Catalogue: [loomground/CATALOGUE.md](https://github.com/flxk1/loomground/blob/main/CATALOGUE.md). Detail: [docs/](docs/).

## Status

Draft spec v1 · package 0.1.0 · 3 tests · Python ≥ 3.9

## License

MIT — [LICENSES/MIT.txt](LICENSES/MIT.txt)
