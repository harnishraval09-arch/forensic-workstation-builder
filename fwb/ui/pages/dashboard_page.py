"""
Dashboard page
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class DashboardPage(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(24)
        
        # Welcome
        self.greeting = QLabel("Good afternoon")
        self.greeting.setStyleSheet("font-size: 28px; font-weight: 600; color: #ffffff;")
        layout.addWidget(self.greeting)
        
        subtitle = QLabel("Here's the current state of your forensic workstation environment.")
        subtitle.setStyleSheet("color: #8e8e93; font-size: 15px;")
        layout.addWidget(subtitle)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.stat_cards = {}
        stats_data = [
            ("Available Tools", "#007AFF"),
            ("Installed", "#34C759"),
            ("Updates Available", "#FF9500"),
            ("Profiles", "#AF52DE")
        ]
        
        for label, color in stats_data:
            card = self.create_stat_card(label, "0", color)
            stats_layout.addWidget(card)
            self.stat_cards[label] = card
        
        layout.addLayout(stats_layout)
        
        # Activity section
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("Recent Activity")
        activity_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        activity_layout.addWidget(activity_title)
        
        self.activity_text = QLabel("No activity yet. Install a tool to get started.")
        self.activity_text.setStyleSheet("color: #8e8e93; font-size: 13px; padding: 8px 0;")
        self.activity_text.setWordWrap(True)
        activity_layout.addWidget(self.activity_text)
        
        layout.addWidget(activity_frame)
        layout.addStretch()
    
    def create_stat_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #141414;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
                padding: 16px 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 600;
            color: {color};
        """)
        layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("color: #8e8e93; font-size: 13px;")
        layout.addWidget(label_label)
        
        return card
    
    def refresh(self):
        try:
            # Get data
            tools = []
            installed = []
            profiles = []
            
            if hasattr(self.app_state, 'get_tools'):
                tools = self.app_state.get_tools()
            elif hasattr(self.app_state, 'tool_manager'):
                tools = list(self.app_state.tool_manager.tools.values())
            
            if hasattr(self.app_state, 'get_installed_tools'):
                installed = self.app_state.get_installed_tools()
            elif hasattr(self.app_state, 'tool_manager'):
                installed = list(self.app_state.tool_manager.installed_tools.values())
            
            if hasattr(self.app_state, 'get_profiles'):
                profiles = self.app_state.get_profiles()
            elif hasattr(self.app_state, 'profile_manager'):
                profiles = self.app_state.profile_manager.list_profiles()
            
            # Update stats
            self.update_stat("Available Tools", str(len(tools)))
            self.update_stat("Installed", str(len(installed)))
            self.update_stat("Profiles", str(len(profiles)))
            
            # Update activity
            if hasattr(self.app_state, 'activity_log') and self.app_state.activity_log:
                if isinstance(self.app_state.activity_log, list) and len(self.app_state.activity_log) > 0:
                    latest = self.app_state.activity_log[0]
                    msg = latest.get('message', 'No activity')
                    self.activity_text.setText(f"• {msg}")
                else:
                    self.activity_text.setText("No activity yet. Install a tool to get started.")
            
        except Exception as e:
            print(f"Refresh error: {e}")
    
    def update_stat(self, label, value):
        if label in self.stat_cards:
            for child in self.stat_cards[label].children():
                if isinstance(child, QLabel) and child.styleSheet().startswith("font-size: 32px"):
                    child.setText(value)
                    break