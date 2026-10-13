"""
Gift Picker Dialog — chia tab theo khoảng giá coin.
Không search — chỉ click tab + chọn.
"""
import json
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTabWidget, QWidget, QFrame
)
import gifts as gift_data


COLORS = {
    "bg": "#0f0f18",
    "card": "#1a1a2e",
    "card_hover": "#252545",
    "border": "#2d2d44",
    "border_hi": "#3d3d5c",
    "text": "#e8e8f0",
    "text_dim": "#8888a0",
    "primary": "#7c5cff",
    "primary_hi": "#9d7fff",
    "success": "#00d68f",
    "gold": "#ffd700",
    "danger": "#ff3d5a",
    "warning": "#ffaa00",
}


# ═══════════════════════════════════════════════════════════
# ĐƯỜNG DẪN
# ═══════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent
ICONS_DIR = BASE_DIR / "assets" / "gift-icons"
RECENT_FILE = BASE_DIR / "assets" / "recent_gifts.json"


# ═══════════════════════════════════════════════════════════
# COIN TABS
# ═══════════════════════════════════════════════════════════
COIN_TABS = [
    ("Tất cả",        0,           999_999_999),
    ("1-10",          1,           10),
    ("11-50",         11,          50),
    ("51-100",        51,          100),
    ("101-500",       101,         500),
    ("501-1K",        501,         1000),
    ("1K-5K",         1001,        5000),
    ("5K-10K",        5001,        10_000),
    ("10K-30K",       10_001,      30_000),
    ("30K-50K",       30_001,      50_000),
    ("> 50K",         50_001,      999_999_999),
]
# ═══════════════════════════════════════════════════════════
# PINNED GIFTS — Gift hay dùng, ghim lên đầu
# ═══════════════════════════════════════════════════════════
PINNED_GIFTS = [
    "rose",
    "tiktok",
    "gg",
    "lucky_pig",
    "rosa",
    "little_kisses",
    "perfume",
    "doughnut",
    "paper_crane",       # Hạc giấy
    "game_controller",
    "super_gg",
    "galaxy",
    "swan",
    "corgi",
    "money_gun",
]

# ═══════════════════════════════════════════════════════════
# LOAD ICONS
# ═══════════════════════════════════════════════════════════
def load_icon_files():
    icons = {}
    if not ICONS_DIR.exists():
        return icons
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
    for f in ICONS_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in exts:
            stem = f.stem.lower()
            if stem not in icons:
                icons[stem] = f
    return icons


def find_icon(folder, icon_files):
    return icon_files.get(folder.lower())


# ═══════════════════════════════════════════════════════════
# RECENT
# ═══════════════════════════════════════════════════════════
def load_recent_gifts():
    if not RECENT_FILE.exists():
        return []
    try:
        data = json.loads(RECENT_FILE.read_text(encoding="utf-8"))
        return data.get("recent", [])
    except Exception:
        return []


def save_recent_gifts(recent_folders):
    try:
        RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        RECENT_FILE.write_text(
            json.dumps({"recent": recent_folders}, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[recent] Save error: {e}")


def add_recent_gift(folder, max_recent=5):
    recent = load_recent_gifts()
    if folder in recent:
        recent.remove(folder)
    recent.insert(0, folder)
    recent = recent[:max_recent]
    save_recent_gifts(recent)
    return recent


# ═══════════════════════════════════════════════════════════
# GIFT PICKER DIALOG
# ═══════════════════════════════════════════════════════════
class GiftPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎁 Chọn Gift")
        self.setMinimumSize(700, 750)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg']}; }}")

        # Load icons — cache
        self.icon_files = load_icon_files()
        print(f"[gift-picker] Loaded {len(self.icon_files)} icon files")

        self.icon_cache = {}
        self._preload_icons()

        # Sắp xếp theo coins
        self.gift_data = sorted(
            gift_data.GIFTS,
            key=lambda g: (g[2], g[0].lower())
        )

        self.selected_gift = None

        self._build_ui()

    def _preload_icons(self):
        """Preload tất cả icon 1 lần."""
        for folder, path in self.icon_files.items():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.icon_cache[folder] = QIcon(pixmap)
        print(f"[gift-picker] Cached {len(self.icon_cache)} icons")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # HEADER
        header = QLabel(f"🎁 CHỌN GIFT  —  Tổng: {len(self.gift_data):,}")
        header.setStyleSheet(f"""
            color: {COLORS['primary_hi']};
            font-size: 16px;
            font-weight: 900;
            padding: 8px;
            letter-spacing: 1px;
        """)
        root.addWidget(header)

        # ★ TABS theo giá coin
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background: {COLORS['bg']};
            }}
            QTabBar::tab {{
                background: {COLORS['card']};
                color: {COLORS['text_dim']};
                padding: 10px 16px;
                border-radius: 8px 8px 0 0;
                font-weight: 700;
                font-size: 12px;
                margin-right: 2px;
                min-width: 60px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {COLORS['card_hover']};
            }}
        """)

        # Tạo từng tab
        for tab_name, min_c, max_c in COIN_TABS:
            gifts_in_range = [
                g for g in self.gift_data
                if min_c <= g[2] <= max_c
            ]
            tab_widget = self._create_tab(gifts_in_range, tab_name)
            self.tabs.addTab(tab_widget, f"{tab_name} ({len(gifts_in_range)})")

        root.addWidget(self.tabs, 1)

        # FOOTER
        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.status_label = QLabel("Chưa chọn gift")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            font-size: 12px;
            font-weight: 700;
        """)
        footer.addWidget(self.status_label)
        footer.addStretch()

        btn_cancel = QPushButton("❌ Hủy")
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['card']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 700;
                min-width: 100px;
            }}
            QPushButton:hover {{ background: {COLORS['border']}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        self.btn_select = QPushButton("✅ Chọn gift")
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 700;
                min-width: 160px;
            }}
            QPushButton:hover {{ background: {COLORS['primary_hi']}; }}
            QPushButton:disabled {{
                background: {COLORS['border']};
                color: {COLORS['text_dim']};
            }}
        """)
        self.btn_select.setEnabled(False)
        self.btn_select.clicked.connect(self.accept)
        footer.addWidget(self.btn_select)

        root.addLayout(footer)

    def _create_tab(self, gifts, tab_name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lst = QListWidget()
        lst.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: none;
                padding: 6px;
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 6px;
                min-height: 40px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['card_hover']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        lst.setIconSize(QSize(32, 32))
        lst.setUniformItemSizes(True)

        # ═══════════════════════════════════════════════════
        # ★ PHẦN 1: PINNED GIFTS
        # ═══════════════════════════════════════════════════
        # Lấy danh sách pinned gift từ gift_data
        pinned_set = set(f.lower() for f in PINNED_GIFTS)
        pinned_items = [
            g for g in self.gift_data
            if g[4].lower() in pinned_set
        ]
        # Sắp xếp theo thứ tự trong PINNED_GIFTS
        pinned_order = {f.lower(): i for i, f in enumerate(PINNED_GIFTS)}
        pinned_items.sort(key=lambda g: pinned_order.get(g[4].lower(), 999))

        if pinned_items:
            # Header "PINNED"
            header_item = QListWidgetItem("⭐  PINNED — Gift hay dùng")
            header_item.setFlags(Qt.NoItemFlags)  # Không click được
            header_item.setForeground(Qt.gray)
            header_item.setData(Qt.UserRole, None)
            # Font đậm + màu vàng
            font = header_item.font()
            font.setBold(True)
            font.setPointSize(11)
            header_item.setFont(font)
            header_item.setBackground(Qt.transparent)
            lst.addItem(header_item)

            # Các pinned gift
            for g in pinned_items:
                name, icon, points, effect, folder = g
                icon_obj = self.icon_cache.get(folder.lower(), QIcon())
                prefix = "🎆 " if effect == "fx" else ""
                display = f"  {prefix}{name}  —  {points:,} coins"

                item = QListWidgetItem(icon_obj, display)
                item.setData(Qt.UserRole, g)
                # Highlight nhẹ
                item.setBackground(Qt.transparent)
                lst.addItem(item)

            # Separator
            sep_item = QListWidgetItem("─" * 80)
            sep_item.setFlags(Qt.NoItemFlags)
            sep_item.setForeground(Qt.gray)
            sep_item.setData(Qt.UserRole, None)
            lst.addItem(sep_item)

        # ═══════════════════════════════════════════════════
        # ★ PHẦN 2: ALL GIFTS (loại trừ pinned khỏi phần này)
        # ═══════════════════════════════════════════════════
        # Header "ALL GIFTS"
        all_header = QListWidgetItem(f"📦  ALL GIFTS ({len(gifts):,})")
        all_header.setFlags(Qt.NoItemFlags)
        all_header.setForeground(Qt.gray)
        all_header.setData(Qt.UserRole, None)
        font = all_header.font()
        font.setBold(True)
        font.setPointSize(11)
        all_header.setFont(font)
        lst.addItem(all_header)

        # Các gift còn lại (bỏ pinned)
        for g in gifts:
            # Bỏ qua pinned (đã hiện ở trên)
            if g[4].lower() in pinned_set:
                continue

            name, icon, points, effect, folder = g
            icon_obj = self.icon_cache.get(folder.lower(), QIcon())
            prefix = "🎆 " if effect == "fx" else ""
            display = f"  {prefix}{name}  —  {points:,} coins"

            item = QListWidgetItem(icon_obj, display)
            item.setData(Qt.UserRole, g)
            lst.addItem(item)

        # Signal
        lst.currentItemChanged.connect(
            lambda current, previous: self._on_item_changed(current, previous)
        )
        lst.itemDoubleClicked.connect(self._on_item_double)

        layout.addWidget(lst)
        return widget

    def _on_item_changed(self, current, previous, lst):
        """★ Khi selection thay đổi."""
        if current is None:
            return
        gift = current.data(Qt.UserRole)
        if gift:
            self.selected_gift = gift
            name = gift[0]
            self.btn_select.setEnabled(True)
            self.btn_select.setText(f"✅ Chọn: {name}")
            self.status_label.setText(f"Đã chọn: {name} — {gift[2]:,} coins")

    def _on_item_double(self, item):
        """Double click → chọn luôn."""
        gift = item.data(Qt.UserRole)
        if gift:
            self.selected_gift = gift
            self.accept()

    def accept(self):
        if self.selected_gift:
            folder = self.selected_gift[4]
            add_recent_gift(folder)
        super().accept()