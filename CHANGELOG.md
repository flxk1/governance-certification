# Changelog

## [0.2.0](https://github.com/flxk1/governance-certification/compare/v0.1.0...v0.2.0) (2026-09-11)


### Features

* GovernanceCertification v1 — schema + reference verifier ([1273e64](https://github.com/flxk1/governance-certification/commit/1273e648fb2eadb8ffdc1464ca5e0c2fa9459476))


### Bug Fixes

* **release:** extra-files + version marker, not version-file ([2a95eaf](https://github.com/flxk1/governance-certification/commit/2a95eaf3bdda4a43ea4d7eef7e680a498eb46114))


### Documentation

* add intact pillar to the family index ([b59ba7d](https://github.com/flxk1/governance-certification/commit/b59ba7d1f21197a3154c6cb6dc63aa9959a9ae74))
* decouple README from sibling repos ([5a0bb2b](https://github.com/flxk1/governance-certification/commit/5a0bb2bdcd83de49259f01252d910c55cba6ac22))
* llms.txt generated from README ([0f9ce85](https://github.com/flxk1/governance-certification/commit/0f9ce857880f3ffa01b8bba33b5a12da7bcead17))
* README Problem + executed Example (201 words) ([acc7741](https://github.com/flxk1/governance-certification/commit/acc7741af98d75bf53d3b16e5babe04d64faa3c8))
* README to canon (144 words), description, Family ([6cbf003](https://github.com/flxk1/governance-certification/commit/6cbf00394b2570c35819a3f38e67f5a65159ce48))

## Changelog

## Unreleased

- Repository laid out on the measure skeleton: root `verify.py` → `src/governance_certification/verify.py` (import path `governance_certification.verify`, console script `govcert-verify` unchanged); `schema/` stays at root and ships in the wheel as package data; `LICENSE` → `LICENSES/MIT.txt` + `NOTICE` + `REUSE.toml`; version single-sourced from `src/governance_certification/_version.py`.
