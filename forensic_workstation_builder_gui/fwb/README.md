# Forensic Workstation Builder — GUI

A PySide6 desktop GUI wired directly into the existing backend
(`ToolManager`, `ProfileManager`, `DependencyResolver`, `Installer`).

## Run it

```bash
pip install -r requirements.txt
python main.py
```

The app loads every `*.json` tool manifest in `data/tools/` and every
`*.json` profile in `data/profiles/` on startup. Sample manifests for
14 tools and 3 profiles (Windows Forensics, Malware Analysis, Network
Forensics) are included so the catalogue isn't empty on first run —
replace/add to these freely, the loader picks up anything dropped in
those folders.

## Layout

```
main.py                     entry point — bootstraps backend, launches GUI
src/
  models/                   Tool, Profile dataclasses (as provided)
  core/                     ToolManager, ProfileManager, DependencyResolver,
                             Installer (as provided)
  utils/                    Downloader, security helpers (as provided)
  gui/
    app_state.py            wires backend managers + GUI-only state together
    state.py                ActivityLog, JobStore, SnapshotStore
    workers.py               QThread workers so installs don't block the UI
    theme.py                 dark/light QSS palettes
    main_window.py           sidebar + header + page stack
    pages/                   Dashboard, Catalogue, Profiles, Jobs,
                              Snapshots, Settings
    components/               StatCard, ToolCard, ProfileCard,
                              ProgressDialog, ToolDetailDialog,
                              InstallationPlanDialog, CreateProfileDialog
data/
  tools/*.json               tool manifests loaded by ToolManager
  profiles/*.json             profile bundles loaded by ProfileManager
  snapshots/                  GUI-managed snapshot JSON files (created at runtime)
  logs/app.log                 rotating log output
```

## Notes on backend integration

- **Install progress**: `ToolManager.install_tool()` is synchronous and
  doesn't report granular progress, so installs run on a background
  `QThread` (`InstallWorker` / `BatchInstallWorker`) and the UI shows
  an indeterminate progress bar rather than a fake percentage.
- **Dependency plan preview**: Before installing a profile, the GUI
  calls `DependencyResolver.set_tools()` + `get_install_plan()` and
  shows the resulting batches in `InstallationPlanDialog` for
  confirmation. `ToolManager.install_tool()` also resolves a single
  tool's own dependency chain recursively, so both single-tool and
  profile installs stay consistent.
- **Update detection**: `Tool.installed_version` is never populated by
  the current backend, so "Updates Available" reports 0 until that's
  wired up — the Settings page's Update Policy control only stores a
  preference for now.
- **Snapshots**: there's no `SnapshotManager` in the backend yet, so
  `SnapshotStore` (GUI-side) persists snapshots as JSON files
  (`{name, created_at, tool_ids}`) under `data/snapshots/`. Swap this
  out for a real backend manager whenever one exists — the page only
  talks to `SnapshotStore`, not the JSON format directly.
- **Directories**: The Settings page lets you browse for download/
  install directories, but `ToolManager` takes `tools_dir` at
  construction time, so changing them currently requires a restart —
  noted in the UI when you save.

## Known limitations to flag to the team

- `Installer._install_archive` in the provided `tool_manager.py` is a
  placeholder (`"Archive installation not yet implemented"|`), so
  installing archive-based tools (CyberChef, Ghidra, NetworkMiner)
  will report a clean failure until that's implemented — the GUI
  surfaces the returned message as-is rather than masking it.
- `Uninstall` in the GUI calls `Installer.uninstall_tool()`, which
  requires `tool.install_path` to be set; portable/archive installs
  set this today, but installer-based (.exe/.msi) installs don't, so
  uninstall for those will report "No installation found" until the
  backend tracks install paths for that method too.
