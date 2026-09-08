"""
Theme system - color palettes and QSS stylesheet generation for the
Forensic Workstation Builder GUI.

Visual direction: navy nav + a teal-to-blue gradient banner under it,
clean white/light-gray content panels, pill-shaped outlined buttons -
inspired by a corporate security-vendor site look. Both a Light and a
Dark variant are provided; Dark keeps the same navy/teal/blue accent
family but on dark surfaces so it doesn't feel like a different app.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    # Sidebar (navy, IDE-style nav)
    sidebar_bg: str
    sidebar_bg_hover: str
    sidebar_bg_active: str
    sidebar_text: str
    sidebar_text_muted: str

    # Header banner (teal -> blue gradient, like the reference site's hero strip)
    header_grad_start: str
    header_grad_end: str
    header_text: str
    header_subtext: str
    header_border: str

    # Surfaces
    window_bg: str
    surface: str
    surface_alt: str
    border: str

    text_primary: str
    text_secondary: str
    text_muted: str

    primary: str
    primary_hover: str
    primary_pressed: str

    success: str
    warning: str
    danger: str
    info: str


LIGHT = Palette(
    sidebar_bg="#0d3b66",
    sidebar_bg_hover="#123f6e",
    sidebar_bg_active="#155a94",
    sidebar_text="#f2f6fa",
    sidebar_text_muted="#a9c2d8",

    header_grad_start="#2ec4b6",
    header_grad_end="#2f6fed",
    header_text="#ffffff",
    header_subtext="rgba(255,255,255,0.88)",
    header_border="#dfe4ea",

    window_bg="#f4f6f8",
    surface="#ffffff",
    surface_alt="#f6f8f9",
    border="#e1e6ea",

    text_primary="#1c2530",
    text_secondary="#54626f",
    text_muted="#8a97a3",

    primary="#2f6fed",
    primary_hover="#2a63d4",
    primary_pressed="#2456b8",

    success="#27ae60",
    warning="#e67e22",
    danger="#e74c3c",
    info="#2ec4b6",
)

DARK = Palette(
    sidebar_bg="#0a2540",
    sidebar_bg_hover="#0f3055",
    sidebar_bg_active="#155a94",
    sidebar_text="#f2f6fa",
    sidebar_text_muted="#8fa9c2",

    header_grad_start="#1b7d72",
    header_grad_end="#20408f",
    header_text="#ffffff",
    header_subtext="rgba(255,255,255,0.82)",
    header_border="#152f4a",

    window_bg="#0f1620",
    surface="#182234",
    surface_alt="#1d293d",
    border="#2a3a52",

    text_primary="#eef2f5",
    text_secondary="#b7c2cc",
    text_muted="#7c8a97",

    primary="#4a8bff",
    primary_hover="#659dff",
    primary_pressed="#3a76e6",

    success="#2ecc71",
    warning="#f39c12",
    danger="#e74c3c",
    info="#2ec4b6",
)


def get_palette(theme_name: str) -> Palette:
    return DARK if theme_name.lower() == "dark" else LIGHT


def build_stylesheet(theme_name: str) -> str:
    p = get_palette(theme_name)
    return f"""
    /* ---------- Global ---------- */
    QWidget {{
        background-color: {p.window_bg};
        color: {p.text_primary};
        font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }}
    QMainWindow, #ContentArea {{
        background-color: {p.window_bg};
    }}
    QToolTip {{
        background-color: {p.surface_alt};
        color: {p.text_primary};
        border: 1px solid {p.border};
        padding: 4px 8px;
        border-radius: 4px;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p.text_muted};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}

    /* ---------- Sidebar (navy IDE-style nav) ---------- */
    #Sidebar {{
        background-color: {p.sidebar_bg};
        border-right: none;
    }}
    #SidebarBrand {{
        color: {p.sidebar_text};
        font-size: 17px;
        font-weight: 700;
        padding: 22px 20px 4px 20px;
    }}
    #SidebarSubtitle {{
        color: {p.sidebar_text_muted};
        font-size: 11px;
        padding: 0px 20px 18px 20px;
    }}
    QPushButton#NavButton {{
        background-color: transparent;
        color: {p.sidebar_text_muted};
        text-align: left;
        padding: 11px 20px;
        border: none;
        border-left: 3px solid transparent;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton#NavButton:hover {{
        background-color: {p.sidebar_bg_hover};
        color: {p.sidebar_text};
    }}
    QPushButton#NavButton:checked {{
        background-color: {p.sidebar_bg_active};
        color: #ffffff;
        border-left: 3px solid {p.header_grad_start};
        font-weight: 600;
    }}

    /* ---------- Header banner (teal -> blue gradient) ---------- */
    #Header {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {p.header_grad_start}, stop:1 {p.header_grad_end}
        );
        border-bottom: 1px solid {p.header_border};
    }}
    #HeaderTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {p.header_text};
    }}
    #HeaderSubtitle {{
        font-size: 12px;
        color: {p.header_subtext};
    }}
    #StatusPill {{
        background-color: rgba(255, 255, 255, 0.18);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.35);
        border-radius: 13px;
        padding: 5px 14px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* ---------- Cards / Surfaces ---------- */
    QFrame#Card {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 12px;
    }}
    QFrame#Card:hover {{
        border: 1px solid {p.primary};
    }}
    QFrame#StatCard {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 12px;
    }}
    QLabel#StatValue {{
        font-size: 26px;
        font-weight: 700;
        color: {p.text_primary};
    }}
    QLabel#StatLabel {{
        font-size: 12px;
        color: {p.text_muted};
        font-weight: 600;
    }}
    QLabel#SectionTitle {{
        font-size: 15px;
        font-weight: 700;
        color: {p.text_primary};
    }}
    QLabel#Muted {{
        color: {p.text_muted};
    }}
    QLabel#CardTitle {{
        font-size: 14px;
        font-weight: 700;
        color: {p.text_primary};
    }}
    QLabel#CardMeta {{
        font-size: 11px;
        color: {p.text_muted};
    }}
    QLabel#CardDesc {{
        font-size: 12px;
        color: {p.text_secondary};
    }}

    /* ---------- Badges ---------- */
    QLabel#BadgeInstalled {{
        background-color: rgba(39, 174, 96, 0.15);
        color: {p.success};
        border-radius: 9px;
        padding: 2px 10px;
        font-size: 10px;
        font-weight: 700;
    }}
    QLabel#BadgeNotInstalled {{
        background-color: rgba(138, 151, 163, 0.18);
        color: {p.text_muted};
        border-radius: 9px;
        padding: 2px 10px;
        font-size: 10px;
        font-weight: 700;
    }}
    QLabel#BadgeUpdate {{
        background-color: rgba(230, 126, 34, 0.18);
        color: {p.warning};
        border-radius: 9px;
        padding: 2px 10px;
        font-size: 10px;
        font-weight: 700;
    }}
    QLabel#BadgeAdmin {{
        background-color: rgba(231, 76, 60, 0.15);
        color: {p.danger};
        border-radius: 9px;
        padding: 2px 10px;
        font-size: 10px;
        font-weight: 700;
    }}

    /* ---------- Buttons (pill-shaped, outlined primary like reference site) ---------- */
    QPushButton {{
        background-color: transparent;
        color: {p.text_primary};
        border: 1px solid {p.border};
        border-radius: 16px;
        padding: 7px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        border-color: {p.primary};
        color: {p.primary};
    }}
    QPushButton:pressed {{
        background-color: {p.surface_alt};
    }}
    QPushButton:disabled {{
        color: {p.text_muted};
        border-color: {p.border};
        background-color: transparent;
    }}
    QPushButton#PrimaryButton {{
        background-color: {p.primary};
        color: #ffffff;
        border: 1px solid {p.primary};
        padding: 9px 20px;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {p.primary_hover};
        border-color: {p.primary_hover};
        color: #ffffff;
    }}
    QPushButton#PrimaryButton:pressed {{
        background-color: {p.primary_pressed};
    }}
    QPushButton#PrimaryButton:disabled {{
        background-color: {p.border};
        border-color: {p.border};
        color: {p.text_muted};
    }}
    QPushButton#DangerButton {{
        background-color: transparent;
        color: {p.danger};
        border: 1px solid {p.danger};
    }}
    QPushButton#DangerButton:hover {{
        background-color: rgba(231, 76, 60, 0.10);
    }}
    QPushButton#GhostButton {{
        background-color: transparent;
        border: 1px solid {p.border};
    }}
    QPushButton#IconButton {{
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 4px;
    }}

    /* ---------- Inputs ---------- */
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 7px 10px;
        color: {p.text_primary};
        selection-background-color: {p.primary};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {p.primary};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        selection-background-color: {p.primary};
        selection-color: #ffffff;
        outline: none;
    }}
    QCheckBox {{
        spacing: 8px;
    }}

    /* ---------- Progress ---------- */
    QProgressBar {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 8px;
        text-align: center;
        color: {p.text_primary};
        height: 16px;
    }}
    QProgressBar::chunk {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {p.header_grad_start}, stop:1 {p.header_grad_end}
        );
        border-radius: 7px;
    }}

    /* ---------- Tables / Lists ---------- */
    QTableWidget, QListWidget, QTreeWidget {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 10px;
        gridline-color: {p.border};
        outline: none;
    }}
    QHeaderView::section {{
        background-color: {p.surface_alt};
        color: {p.text_muted};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {p.border};
        font-weight: 700;
        font-size: 11px;
    }}
    QTableWidget::item, QListWidget::item {{
        padding: 6px;
        border-bottom: 1px solid {p.border};
    }}
    QListWidget::item:selected, QTableWidget::item:selected {{
        background-color: rgba(47, 111, 237, 0.14);
        color: {p.text_primary};
    }}

    /* ---------- Tabs ---------- */
    QTabWidget::pane {{
        border: 1px solid {p.border};
        border-radius: 10px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {p.text_muted};
        padding: 8px 16px;
        font-weight: 600;
    }}
    QTabBar::tab:selected {{
        color: {p.primary};
        border-bottom: 2px solid {p.primary};
    }}

    /* ---------- Dialogs ---------- */
    QDialog {{
        background-color: {p.window_bg};
    }}
    QFrame#DialogHeader {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {p.header_grad_start}, stop:1 {p.header_grad_end}
        );
        border-bottom: 1px solid {p.header_border};
    }}
    QFrame#Separator {{
        background-color: {p.border};
        max-height: 1px;
        min-height: 1px;
    }}

    /* ---------- Icon badges (tool/profile card glyphs) ---------- */
    QLabel#IconBadge {{
        border-radius: 12px;
        font-size: 19px;
    }}
    """
