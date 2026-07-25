"""
Theme system for Forensic Workstation Builder
Apple-inspired silver/white/black design
"""

from PySide6.QtCore import QSettings

def get_theme():
    """Get current theme from settings"""
    settings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")
    return settings.value("theme", "dark")

def set_theme(theme_name: str):
    """Set theme in settings"""
    settings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")
    settings.setValue("theme", theme_name)

def build_stylesheet(theme_name: str = "dark") -> str:
    """Build the complete stylesheet for the application"""
    
    if theme_name == "light":
        return build_light_theme()
    else:
        return build_dark_theme()

def build_dark_theme() -> str:
    """Apple-inspired dark theme - silver/black"""
    return """
    /* ============================================
       APPLE-INSPIRED DARK THEME
       Silver / Black / White
       ============================================ */
    
    /* -------- Global -------- */
    QMainWindow {
        background-color: #000000;
    }
    
    QWidget {
        background-color: transparent;
        color: #ffffff;
        font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
    }
    
    /* -------- Sidebar -------- */
    #Sidebar {
        background-color: #1a1a1a;
        border-right: 1px solid #2a2a2a;
    }
    
    #SidebarBrand {
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        padding: 24px 20px 8px 20px;
        letter-spacing: -0.5px;
    }
    
    #SidebarSubtitle {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
        padding: 0 20px 24px 20px;
        letter-spacing: 0.3px;
    }
    
    #NavButton {
        background-color: transparent;
        color: #8e8e93;
        border: none;
        padding: 10px 20px;
        margin: 2px 10px;
        text-align: left;
        font-size: 14px;
        font-weight: 400;
        border-radius: 8px;
        letter-spacing: -0.2px;
    }
    
    #NavButton:hover {
        background-color: #2a2a2a;
        color: #ffffff;
    }
    
    #NavButton:checked {
        background-color: #2a2a2a;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* -------- Header -------- */
    #Header {
        background-color: #000000;
        border-bottom: 1px solid #1a1a1a;
    }
    
    #HeaderTitle {
        color: #ffffff;
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    #HeaderSubtitle {
        color: #8e8e93;
        font-size: 13px;
        font-weight: 400;
        letter-spacing: 0px;
    }
    
    #StatusPill {
        color: #8e8e93;
        font-size: 12px;
        font-weight: 400;
        background-color: #1a1a1a;
        padding: 6px 14px;
        border-radius: 20px;
    }
    
    /* -------- Content Area -------- */
    #ContentArea {
        background-color: #0a0a0a;
    }
    
    /* -------- Cards -------- */
    #stat-card {
        background-color: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px;
    }
    
    #stat-card:hover {
        border-color: #3a3a3a;
    }
    
    #stat-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: 600;
        letter-spacing: -1px;
    }
    
    #stat-label {
        color: #8e8e93;
        font-size: 13px;
        font-weight: 400;
    }
    
    /* -------- Tool Cards -------- */
    #tool-card {
        background-color: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 16px;
    }
    
    #tool-card:hover {
        border-color: #3a3a3a;
    }
    
    #tool-name {
        color: #ffffff;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    #tool-category {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
        background-color: #1a1a1a;
        padding: 2px 10px;
        border-radius: 12px;
    }
    
    #tool-status {
        color: #8e8e93;
        font-size: 12px;
        font-weight: 400;
    }
    
    /* -------- Buttons -------- */
    QPushButton {
        background-color: #2a2a2a;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0px;
    }
    
    QPushButton:hover {
        background-color: #3a3a3a;
    }
    
    QPushButton:pressed {
        background-color: #1a1a1a;
    }
    
    #install-button {
        background-color: #2a2a2a;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
    }
    
    #install-button:hover {
        background-color: #3a3a3a;
    }
    
    /* -------- Search & Inputs -------- */
    QLineEdit, QComboBox, QSpinBox {
        background-color: #141414;
        color: #ffffff;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border-color: #4a4a4a;
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
    
    /* -------- Scroll Bars -------- */
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    
    QScrollBar:vertical {
        background-color: transparent;
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #2a2a2a;
        border-radius: 3px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #3a3a3a;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* -------- Dialogs -------- */
    QDialog {
        background-color: #0a0a0a;
    }
    
    QDialog QLabel {
        color: #ffffff;
    }
    
    /* -------- Activity Frame -------- */
    #activity-frame {
        background-color: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 15px;
        min-height: 200px;
    }
    
    /* -------- Section Title -------- */
    #section-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.3px;
        margin-top: 10px;
    }
    
    /* -------- Welcome Text -------- */
    #welcome-text {
        color: #ffffff;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: -1px;
        padding: 20px 0;
    }
    
    /* -------- Tool Detail Dialog -------- */
    QDialog#tool-detail {
        background-color: #0a0a0a;
        border-radius: 16px;
    }
    
    /* -------- Progress Dialog -------- */
    QProgressBar {
        background-color: #1a1a1a;
        border: none;
        border-radius: 4px;
        height: 6px;
    }
    
    QProgressBar::chunk {
        background-color: #8e8e93;
        border-radius: 4px;
    }
    
    /* -------- Status Labels -------- */
    QLabel[status="success"] {
        color: #30d158;
    }
    
    QLabel[status="error"] {
        color: #ff453a;
    }
    
    QLabel[status="warning"] {
        color: #ffd60a;
    }
    """

def build_light_theme() -> str:
    """Apple-inspired light theme - white/silver"""
    return """
    /* ============================================
       APPLE-INSPIRED LIGHT THEME
       White / Silver / Black
       ============================================ */
    
    QMainWindow {
        background-color: #f5f5f7;
    }
    
    QWidget {
        background-color: transparent;
        color: #1d1d1f;
        font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
    }
    
    #Sidebar {
        background-color: #ffffff;
        border-right: 1px solid #e5e5ea;
    }
    
    #SidebarBrand {
        color: #1d1d1f;
        font-size: 24px;
        font-weight: 600;
        padding: 24px 20px 8px 20px;
        letter-spacing: -0.5px;
    }
    
    #SidebarSubtitle {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
        padding: 0 20px 24px 20px;
        letter-spacing: 0.3px;
    }
    
    #NavButton {
        background-color: transparent;
        color: #8e8e93;
        border: none;
        padding: 10px 20px;
        margin: 2px 10px;
        text-align: left;
        font-size: 14px;
        font-weight: 400;
        border-radius: 8px;
        letter-spacing: -0.2px;
    }
    
    #NavButton:hover {
        background-color: #f5f5f7;
        color: #1d1d1f;
    }
    
    #NavButton:checked {
        background-color: #f5f5f7;
        color: #1d1d1f;
        font-weight: 500;
    }
    
    #Header {
        background-color: #ffffff;
        border-bottom: 1px solid #e5e5ea;
    }
    
    #HeaderTitle {
        color: #1d1d1f;
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    #HeaderSubtitle {
        color: #8e8e93;
        font-size: 13px;
        font-weight: 400;
    }
    
    #StatusPill {
        color: #8e8e93;
        font-size: 12px;
        font-weight: 400;
        background-color: #f5f5f7;
        padding: 6px 14px;
        border-radius: 20px;
    }
    
    #stat-card {
        background-color: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 20px;
    }
    
    #stat-card:hover {
        border-color: #d1d1d6;
    }
    
    #stat-value {
        color: #1d1d1f;
        font-size: 32px;
        font-weight: 600;
        letter-spacing: -1px;
    }
    
    #stat-label {
        color: #8e8e93;
        font-size: 13px;
        font-weight: 400;
    }
    
    #tool-card {
        background-color: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 16px;
    }
    
    #tool-card:hover {
        border-color: #d1d1d6;
    }
    
    #tool-name {
        color: #1d1d1f;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    #tool-category {
        color: #8e8e93;
        font-size: 11px;
        font-weight: 400;
        background-color: #f5f5f7;
        padding: 2px 10px;
        border-radius: 12px;
    }
    
    QPushButton {
        background-color: #e5e5ea;
        color: #1d1d1f;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #d1d1d6;
    }
    
    QPushButton:pressed {
        background-color: #c7c7cc;
    }
    
    #install-button {
        background-color: #e5e5ea;
        color: #1d1d1f;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
    }
    
    #install-button:hover {
        background-color: #d1d1d6;
    }
    
    QLineEdit, QComboBox, QSpinBox {
        background-color: #ffffff;
        color: #1d1d1f;
        border: 1px solid #e5e5ea;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border-color: #d1d1d6;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #8e8e93;
        margin-right: 8px;
    }
    
    QScrollBar:vertical {
        background-color: transparent;
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #d1d1d6;
        border-radius: 3px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #c7c7cc;
    }
    
    QDialog {
        background-color: #ffffff;
    }
    
    QDialog QLabel {
        color: #1d1d1f;
    }
    
    #activity-frame {
        background-color: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 15px;
        min-height: 200px;
    }
    
    #section-title {
        color: #1d1d1f;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.3px;
        margin-top: 10px;
    }
    
    #welcome-text {
        color: #1d1d1f;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: -1px;
        padding: 20px 0;
    }
    
    QProgressBar {
        background-color: #e5e5ea;
        border: none;
        border-radius: 4px;
        height: 6px;
    }
    
    QProgressBar::chunk {
        background-color: #8e8e93;
        border-radius: 4px;
    }
    """