# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-31

### Added

#### Core Features
- **18+ Forensic Tools** — Autopsy, Wireshark, Ghidra, YARA, Volatility, FTK Imager, Registry Explorer, PEStudio, NetworkMiner, Zeek, KAPE, EvtxECmd, IDA Free, CyberChef, Python3, Java, and more
- **4 Pre-configured Profiles** — Windows Forensics, Malware Analysis, Network Forensics, Custom
- **Dependency Resolution** — Auto-installs prerequisites (Java for Autopsy, Python for Volatility)

#### GUI
- **7 Pages** — Dashboard, Tool Catalogue, Profiles, Jobs, Snapshots, Audit Log, Settings
- **Dark/Light Theme Toggle** — Built-in theme switcher
- **Real-time Progress Tracking** — Installation progress in Jobs page

#### CLI
- **6 Commands** — `list`, `install`, `install-profile`, `list-profiles`, `create-snapshot`, `compare`

#### Security
- SHA-256 Verification — Downloads verified before installation
- Signed Manifests — Tamper-proof tool definitions
- Audit Logging — Complete audit trail in `data/logs/audit.log`
- Admin Permission Detection — Warns before requiring admin rights

#### Reproducibility
- Environment Snapshots — Save and restore exact environments
- Version Pinning — Track exact tool versions
- Environment Comparison — Compare two snapshots

---

### Known Issues
- Archive extraction for CyberChef and Ghidra needs further testing
- Some download URLs may require periodic updates

---

## [Unreleased]

### Planned Features
- Docker support for isolated environments
- Cloud sync for snapshots
- Plugin system for community-contributed tools
- Educational mode with tool explanations