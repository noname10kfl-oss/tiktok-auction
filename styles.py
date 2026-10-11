"""Colors and stylesheet for the GUI - commercial dark theme."""

COLORS = {
    "bg":          "#0b0d17",
    "bg_alt":      "#131625",
    "card":        "#1a1e30",
    "card_hover":  "#222842",
    "border":      "#252b45",
    "border_hi":   "#3a4270",
    "text":        "#e8ecf5",
    "text_dim":    "#8891ab",
    "text_muted":  "#5a6280",
    "primary":     "#7c5cff",
    "primary_hi":  "#977dff",
    "success":     "#00d68f",
    "success_hi":  "#00e89c",
    "warning":     "#ffaa00",
    "warning_hi":  "#ffc233",
    "danger":      "#ff3d5a",
    "danger_hi":   "#ff5d75",
    "gold":        "#ffd700",
    "silver":      "#c0c0c0",
    "bronze":      "#cd7f32",
}


def main_stylesheet():
    c = COLORS
    return f"""
    QMainWindow, QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }}
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        border-radius: 12px;
        background: {c['bg_alt']};
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {c['text_dim']};
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 600;
        font-size: 13px;
    }}
    QTabBar::tab:selected {{
        background: {c['bg_alt']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-bottom-color: {c['bg_alt']};
    }}
    QTabBar::tab:hover:!selected {{
        color: {c['text']};
        background: {c['card']};
    }}
    QGroupBox {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        margin-top: 14px;
        padding: 18px 14px 14px 14px;
        font-weight: 600;
        color: {c['text']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 16px;
        padding: 4px 10px;
        background: {c['card']};
        color: {c['primary_hi']};
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    QPushButton {{
        background: {c['card_hover']};
        color: {c['text']};
        border: 1px solid {c['border_hi']};
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: {c['border_hi']};
        border-color: {c['primary']};
    }}
    QPushButton:disabled {{
        background: {c['bg_alt']};
        color: {c['text_muted']};
        border-color: {c['border']};
    }}
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background: {c['bg']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
        selection-background-color: {c['primary']};
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border-color: {c['primary']};
        background: {c['card']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {c['card']};
        color: {c['text']};
        selection-background-color: {c['primary']};
        border: 1px solid {c['border']};
        outline: none;
        padding: 4px;
    }}
    QListWidget {{
        background: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 6px;
        outline: 0;
    }}
    QListWidget::item {{
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        color: {c['text']};
    }}
    QListWidget::item:hover {{ background: {c['card_hover']}; }}
    QListWidget::item:selected {{
        background: {c['primary']};
        color: white;
    }}
    QTextEdit {{
        background: {c['bg']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 10px;
        font-family: 'Consolas', monospace;
        font-size: 12px;
        selection-background-color: {c['primary']};
    }}
    QScrollBar:vertical {{
        background: {c['bg']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border_hi']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['primary']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    QStatusBar {{
        background: {c['bg_alt']};
        color: {c['text_dim']};
        border-top: 1px solid {c['border']};
        padding: 4px 8px;
    }}
    QStatusBar::item {{ border: none; }}
    QToolTip {{
        background: {c['card']};
        color: {c['text']};
        border: 1px solid {c['primary']};
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 12px;
    }}
    QMessageBox {{ background: {c['bg_alt']}; }}
    QMessageBox QLabel {{ color: {c['text']}; }}
    QMessageBox QPushButton {{
        background: {c['primary']};
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-weight: 600;
    }}
    QMessageBox QPushButton:hover {{ background: {c['primary_hi']}; }}
    """


def btn_style(kind="default", size="md"):
    c = COLORS
    palette = {
        "primary": (c["primary"], c["primary_hi"]),
        "success": (c["success"], c["success_hi"]),
        "warning": (c["warning"], c["warning_hi"]),
        "danger":  (c["danger"], c["danger_hi"]),
        "default": (c["card_hover"], c["border_hi"]),
    }
    base, hover = palette.get(kind, palette["default"])
    sizes = {
        "sm": "padding: 8px 14px; font-size: 12px;",
        "md": "padding: 10px 20px; font-size: 13px;",
        "lg": "padding: 14px 28px; font-size: 15px; font-weight: 700;",
    }
    fg = "#0b0d17" if kind in ("success", "warning") else "white"
    if kind == "default":
        fg = c["text"]
    return f"""
    QPushButton {{
        background: {base};
        color: {fg};
        border: 1px solid {base};
        border-radius: 8px;
        {sizes.get(size, sizes['md'])}
        font-weight: 600;
    }}
    QPushButton:hover {{ background: {hover}; border-color: {hover}; }}
    QPushButton:disabled {{
        background: {c['bg_alt']};
        color: {c['text_muted']};
        border-color: {c['border']};
    }}
    """