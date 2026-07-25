from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGridLayout, QPushButton
)

from ..components.profile_card import ProfileCard
from ..components.installation_plan_dialog import InstallationPlanDialog
from ..components.create_profile_dialog import CreateProfileDialog
from ..components.progress_dialog import ProgressDialog
from ..workers import BatchInstallWorker
from ...models.profile import Profile

COLUMNS = 2


class ProfilesPage(QWidget):
    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        self._batch_worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Profiles")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        create_btn = QPushButton("+ Create Profile")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create_profile)
        header.addWidget(create_btn)
        root.addLayout(header)

        sub = QLabel("Install a curated bundle of tools for a specific forensic workflow.")
        sub.setObjectName("Muted")
        root.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_container = QWidget()
        self.grid = QGridLayout(grid_container)
        self.grid.setSpacing(16)
        scroll.setWidget(grid_container)
        root.addWidget(scroll, 1)

        self.refresh()

    def refresh(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        profiles = self.app_state.profile_manager.list_profiles()
        for index, profile in enumerate(sorted(profiles, key=lambda p: p.name.lower())):
            installed_count = sum(
                1 for tid in profile.tools
                if (t := self.app_state.tool_manager.get_tool(tid)) and t.installed
            )
            card = ProfileCard(profile, len(profile.tools), installed_count)
            card.install_requested.connect(self._install_profile)
            row, col = divmod(index, COLUMNS)
            self.grid.addWidget(card, row, col)

    def _create_profile(self):
        all_tools = self.app_state.tool_manager.list_tools()
        existing_ids = {p.id for p in self.app_state.profile_manager.list_profiles()}
        dialog = CreateProfileDialog(all_tools, existing_ids, self)
        if dialog.exec():
            data = dialog.result_data
            profile = Profile(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                tools=data["tools"],
                category=data["category"],
            )
            success = self.app_state.profile_manager.create_profile(profile)
            if success:
                self.app_state.activity_log.add(f"Created profile '{profile.name}'", "success")
            else:
                self.app_state.activity_log.add(f"Failed to create profile '{profile.name}'", "error")
            self.refresh()
            self.app_state.on_data_changed()

    def _install_profile(self, profile_id: str):
        profile = self.app_state.profile_manager.get_profile(profile_id)
        if not profile:
            return

        tm = self.app_state.tool_manager
        resolver = self.app_state.dependency_resolver
        resolver.set_tools(tm.tools, set(tm.installed_tools.keys()))
        plan = resolver.get_install_plan(profile.tools)

        plan_dialog = InstallationPlanDialog(plan, tm.tools, f"Install '{profile.name}'", self)
        if plan_dialog.exec() != InstallationPlanDialog.Accepted:
            return

        ordered_ids = [tid for batch in plan["batches"] for tid in batch]
        if not ordered_ids:
            self.app_state.activity_log.add(f"'{profile.name}' is already fully installed", "info")
            return

        self.app_state.activity_log.add(f"Started installing profile '{profile.name}'", "info")
        progress = ProgressDialog(f"Installing profile: {profile.name}", self)
        progress.set_status(f"Installing {len(ordered_ids)} tool(s)…")

        worker = BatchInstallWorker(tm, ordered_ids)
        self._batch_worker = worker

        def on_tool_finished(tool_id, success, message):
            tool = tm.get_tool(tool_id)
            name = tool.name if tool else tool_id
            job = self.app_state.job_store.start_job(tool_id, name)
            self.app_state.job_store.complete_job(job.job_id, success, message)
            level = "success" if success else "error"
            self.app_state.activity_log.add(f"{name}: {message}", level)
            progress.set_status(f"{name}: {message}")

        def on_batch_finished(succeeded, failed):
            progress.mark_complete(
                failed == 0,
                f"{succeeded} succeeded, {failed} failed installing '{profile.name}'"
            )
            self._batch_worker = None
            self.refresh()
            self.app_state.on_data_changed()

        worker.tool_finished.connect(on_tool_finished)
        worker.batch_finished.connect(on_batch_finished)
        worker.start()
        progress.exec()
