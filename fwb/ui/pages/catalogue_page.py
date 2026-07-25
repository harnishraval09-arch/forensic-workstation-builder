"""
Tool catalogue page with category icons
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal

class CataloguePage(QWidget):
    """Tool catalogue for browsing and installing tools"""
    
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setup_ui()
        
        # Connect search and filter
        self.search_input.textChanged.connect(self.filter_tools)
        self.category_filter.currentTextChanged.connect(self.filter_tools)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tools by name or description...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3a3a3a;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All categories",
            "Digital Forensics",
            "Malware Analysis", 
            "Network Forensics",
            "General",
            "Runtime"
        ])
        self.category_filter.setStyleSheet("""
            QComboBox {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8e8e93;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                selection-background-color: #2a2a2a;
            }
        """)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Tool count
        self.count_label = QLabel("0 tool(s)")
        self.count_label.setStyleSheet("""
            color: #8e8e93;
            font-size: 13px;
            font-weight: 400;
            padding: 0 4px;
        """)
        layout.addWidget(self.count_label)
        
        # Tool grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.tool_container = QWidget()
        self.tool_grid = QGridLayout(self.tool_container)
        self.tool_grid.setSpacing(16)
        self.tool_grid.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.tool_container)
        
        layout.addWidget(scroll)
        
        # Load tools
        self.refresh()
    
    def refresh(self):
        """Refresh the tool list"""
        self.load_tools()
    
    def load_tools(self):
        """Load tools from the backend"""
        # Clear existing tools
        for i in reversed(range(self.tool_grid.count())):
            widget = self.tool_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get tools from app_state
        tools = []
        if hasattr(self.app_state, 'get_tools'):
            tools = self.app_state.get_tools()
        
        # Also check tool_manager directly
        if not tools and hasattr(self.app_state, 'tool_manager'):
            tools = list(self.app_state.tool_manager.tools.values())
        
        self.all_tools = tools
        self.filter_tools()
    
    def filter_tools(self):
        """Filter tools based on search and category"""
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        filtered = []
        for tool in self.all_tools:
            # Search filter
            if search_text and search_text not in tool.name.lower() and search_text not in tool.description.lower():
                continue
            
            # Category filter
            if category != "All categories" and tool.category != category:
                continue
            
            filtered.append(tool)
        
        # Update count
        self.count_label.setText(f"{len(filtered)} tool(s)")
        
        # Display filtered tools
        self.display_tools(filtered)
    
    def display_tools(self, tools):
        """Display tools in grid"""
        # Clear grid
        for i in reversed(range(self.tool_grid.count())):
            widget = self.tool_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Category icons
        category_icons = {
            "Digital Forensics": "🔍",
            "Malware Analysis": "🦠",
            "Network Forensics": "🌐",
            "General": "🧰",
            "Runtime": "⚙️",
            "Default": "🔧"
        }
        
        # Add tools to grid
        for i, tool in enumerate(tools):
            card = self.create_tool_card(tool, category_icons)
            row = i // 3
            col = i % 3
            self.tool_grid.addWidget(card, row, col)
    
    def create_tool_card(self, tool, category_icons):
        """Create a tool card widget"""
        card = QFrame()
        card.setObjectName("tool-card")
        card.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #3a3a3a;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Tool icon and name
        icon = category_icons.get(tool.category, category_icons["Default"])
        name = QLabel(f"{icon} {tool.name}")
        name.setObjectName("tool-name")
        name.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.3px;
        """)
        layout.addWidget(name)
        
        # Category and version
        info = QLabel(f"{tool.category} · v{tool.version}")
        info.setObjectName("tool-category")
        info.setStyleSheet("""
            color: #8e8e93;
            font-size: 11px;
            font-weight: 400;
            background-color: #1a1a1a;
            padding: 2px 10px;
            border-radius: 12px;
        """)
        layout.addWidget(info)
        
        # Description
        desc = QLabel(tool.description[:100] + ("..." if len(tool.description) > 100 else ""))
        desc.setObjectName("tool-description")
        desc.setStyleSheet("""
            color: #8e8e93;
            font-size: 12px;
            font-weight: 400;
            word-wrap: true;
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Status
        status_text = "INSTALLED" if tool.installed else "NOT INSTALLED"
        admin_text = " ADMIN" if tool.requires_admin else ""
        status = QLabel(f"{status_text}{admin_text}")
        status.setObjectName("tool-status")
        status.setStyleSheet(f"""
            color: {"#34C759" if tool.installed else "#8e8e93"};
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.3px;
            background-color: {"#1a3a1a" if tool.installed else "#1a1a1a"};
            padding: 3px 10px;
            border-radius: 10px;
        """)
        layout.addWidget(status)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        if tool.installed:
            install_btn = QPushButton("Reinstall")
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            """)
        else:
            install_btn = QPushButton("Install")
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: #ffffff;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0066CC;
                }
            """)
        
        install_btn.clicked.connect(lambda checked, t=tool: self.install_tool(t))
        btn_layout.addWidget(install_btn)
        
        details_btn = QPushButton("Details")
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8e8e93;
                border: 1px solid #2a2a2a;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 400;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                color: #ffffff;
            }
        """)
        details_btn.clicked.connect(lambda checked, t=tool: self.show_details(t))
        btn_layout.addWidget(details_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return card
    
    def install_tool(self, tool):
        """Install a tool"""
        from fwb.ui.components.progress_dialog import ProgressDialog
        from fwb.ui.workers import InstallWorker
        
        dialog = ProgressDialog(tool.name, self)
        
        def on_progress(msg, progress):
            dialog.update_progress(msg, progress)
        
        def on_finished(success, result):
            dialog.close()
            if success:
                self.refresh()
                if hasattr(self.app_state, 'data_changed'):
                    self.app_state.data_changed.emit()
        
        worker = InstallWorker(self.app_state, tool.id, on_progress)
        worker.finished.connect(on_finished)
        worker.start()
        
        dialog.exec()
    
    def show_details(self, tool):
        """Show tool details dialog"""
        from fwb.ui.components.tool_detail_dialog import ToolDetailDialog
        dialog = ToolDetailDialog(tool, self.app_state, self)
        dialog.exec()
        self.refresh()