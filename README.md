markdown
# 🔬 Forensic Workstation Builder

> A professional, secure platform for discovering, installing, and reproducing digital forensics and cybersecurity tool environments — with one click.

---

## 🎯 What It Does

Digital forensics investigators need 10+ specialized tools to analyze systems. Installing them manually takes hours and is error-prone.

**Forensic Workstation Builder** solves this by providing a beautiful GUI and CLI to:

- **Browse** 18+ forensic tools
- **Install** tools with one click
- **Resolve dependencies** automatically
- **Create profiles** for common workflows (Windows Forensics, Malware Analysis, Network Forensics)
- **Snapshot & reproduce** environments
- **Audit** every action

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **GUI & CLI** | Full graphical interface + command-line support |
| 📦 **18+ Tools** | Autopsy, Wireshark, Ghidra, YARA, Volatility, and more |
| 📋 **4 Profiles** | Windows Forensics, Malware Analysis, Network Forensics, Custom |
| 🔒 **Secure Install** | SHA-256 verification, signed manifests |
| 📊 **Audit Logging** | Complete audit trail of all actions |
| 📸 **Snapshots** | Save and reproduce exact environments |
| 🔄 **Version Pinning** | Track exact tool versions |
| 🌓 **Dark/Light Theme** | Built-in theme toggle |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/harnishraval09-arch/forensic-workstation-builder.git
cd forensic-workstation-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
🖥️ Usage
GUI
bash
python main.py
CLI
bash
python cli.py list                           # List all tools
python cli.py install wireshark              # Install a tool
python cli.py list-profiles                  # List profiles
python cli.py install-profile "Windows Forensics"  # Install a profile
python cli.py create-snapshot "My Lab"       # Create a snapshot
python cli.py compare snapshot_1 snapshot_2  # Compare snapshots
📸 Screenshots
Dashboard	Tool Catalogue
(Add screenshot here)	(Add screenshot here)
🛠️ Architecture
text
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│                   (PySide6 GUI + CLI)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                    │
│              (Orchestration & Logic)                    │
│  - ToolManager  - ProfileManager  - JobEngine          │
│  - DependencyResolver  - SnapshotManager                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                         │
│                 (Data Models)                           │
│  - Tool  - Profile  - Job  - Snapshot                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   ADAPTER LAYER                         │
│              (Platform-specific)                        │
│  - WindowsAdapter  - LinuxAdapter  - WSLAdapter        │
└─────────────────────────────────────────────────────────┘
🧪 Supported Tools
Tool	Category	Type
Autopsy	Digital Forensics	Installer
CyberChef	General	Archive
Wireshark	Network Forensics	Installer
Ghidra	Malware Analysis	Archive
YARA	Malware Analysis	Portable
Volatility3	Malware Analysis	Python Package
FTK Imager	Digital Forensics	Installer
Registry Explorer	Digital Forensics	Portable
PEStudio	Malware Analysis	Portable
NetworkMiner	Network Forensics	Installer
Zeek	Network Forensics	Archive
KAPE	Digital Forensics	Archive
EvtxECmd	Digital Forensics	Portable
IDA Free	Malware Analysis	Installer
Python3	Runtime	Installer
Java	Runtime	Installer
📊 Tech Stack
Technology	Purpose
Python 3.10+	Core language
PySide6	GUI framework
requests	HTTP downloads
hashlib	SHA-256 verification
git	Version control
📝 Audit Logging
All actions are logged to data/logs/audit.log:

json
{"action": "install_started", "tool_id": "wireshark", "status": "info", "timestamp": "..."}
{"action": "download", "tool_id": "wireshark", "status": "success", "details": {...}}
{"action": "install_completed", "tool_id": "wireshark", "status": "success"}
🔐 Security Features
✅ SHA-256 hash verification for downloads

✅ Signed manifests to prevent tampering

✅ Audit logging for all actions

✅ Version pinning for reproducibility

✅ Admin permission detection

📁 Project Structure
text
forensic-workstation-builder/
├── data/                    # Tool manifests, profiles, snapshots
│   ├── tools/              # 18 tool manifests (.json)
│   ├── profiles/           # 4 environment profiles
│   ├── snapshots/          # Saved environment snapshots
│   └── logs/               # Audit and application logs
├── fwb/                    # Main package
│   ├── core/               # Backend logic (ToolManager, Installer)
│   ├── gui/                # GUI components (pages, dialogs)
│   ├── models/             # Data models (Tool, Profile)
│   └── utils/              # Utilities (security, downloader, logger)
├── cli.py                  # Command-line interface
├── main.py                 # GUI entry point
├── sign_manifests.py       # Tool manifest signing script
├── compare_snapshots.py    # Snapshot comparison script
└── requirements.txt        # Python dependencies
👨‍💻 Author
Harnish Raval
BTech CSE (Cybersecurity) — Final Year Project

📝 License
MIT License

🙏 Acknowledgments
Original FAST project for inspiration

All the open-source forensic tools included in the catalogue

Claude AI for GUI design assistance

text

---

## ✅ Your Final Checklist

| Task | Status |
|------|--------|
| Push to GitHub | ⬜ |
| Update README.md | ⬜ |
| Add screenshots | ⬜ |
| Add license | ⬜ |
| Share with seniors | ⬜ |

---

## 🎯 Final Commands

```bash
# Push your code
git remote add origin https://github.com/harnishraval09-arch/forensic-workstation-builder.git
git branch -M main
git push -u origin main

# Update README with the content above
# Then commit and push:
git add README.md
git commit -m "docs: Update README with professional project description"
git push
