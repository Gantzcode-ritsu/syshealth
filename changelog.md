# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/) dan versi mengikuti [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-28

### Added
- Dashboard live: CPU (total dan per core), RAM, Swap, Disk, Network I/O, Top-N proses.
- Progress bar dengan warna dinamis (Normal < 70%, Warning 70-85%, Critical > 85%).
- Opsi CLI `--interval`, `--top`, `--sort`, `--export json|md`, `--output`, `--version`.
- Ekspor snapshot ke JSON dan Markdown.
- Test suite pytest untuk collector, utils, formatter, dan CLI.
- CI GitHub Actions (Linux, macOS, Windows) dan workflow rilis ke PyPI.