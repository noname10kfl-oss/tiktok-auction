"""
TikTok Auction Tool - Desktop App
Có tích hợp VTuber (nhân vật AI nhép miệng theo mic)
Dev:   uv run python app.py
Build: build.bat
"""
import asyncio
import os
import sys
import threading
import time
import gifts as gift_data
import json as _json
from bot_manager import make_roblox_username
from pathlib import Path

if getattr(sys, "frozen", False):
    os.environ["QT_PLUGIN_PATH"] = sys._MEIPASS

from PySide6.QtCore import Qt, QTimer, QObject, Signal
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineSettings
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("⚠️ PySide6-WebEngine chưa cài. Chạy: uv add PySide6-WebEngine")
from PySide6.QtGui import QFont, QColor, QShortcut, QKeySequence, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QGroupBox, QListWidget, QListWidgetItem, QTextEdit, QMessageBox,
    QTabWidget, QFrame, QComboBox, QCheckBox, QScrollArea
)
# ═══════════════════════════════════════════════════════════
# SPINBOX KHÔNG ĐỔI GIÁ TRỊ KHI CUỘN CHUỘT
# ═══════════════════════════════════════════════════════════
class NoWheelSpinBox(QSpinBox):
    """QSpinBox chặn wheelEvent — cuộn chuột không đổi giá trị."""
    def wheelEvent(self, event):
        event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox chặn wheelEvent — cuộn chuột không đổi giá trị."""
    def wheelEvent(self, event):
        event.ignore()

from engine import AuctionEngine, Phase
from server import OverlayServer, get_lan_ip
from tiktok_client import TikTokLiveRunner
from bot_manager import BotManager
from voice_listener import VoiceListener
from styles import main_stylesheet, btn_style, COLORS
import gifts as gift_data


def resource_path(rel: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / rel
    return Path(__file__).parent / rel


# ============================================================
# ASYNC WORKER
# ============================================================
class AsyncWorker(QObject):
    log_signal = Signal(str)
    status_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        static_dir = resource_path(".")

        vouch_file = static_dir / "assets" / "vouch.json"
        robux_file = static_dir / "assets" / "robux.json"
        self.engine = AuctionEngine(
            vouch_file=vouch_file,
            robux_file=robux_file,
        )

        self.server = OverlayServer(
            self.engine,
            static_dir,
            port=3000,
            license_key="Tunchill",
        )
        self.tiktok = TikTokLiveRunner(
            self.loop,
            on_gift=self._on_gift,
            on_status=self._on_status,
            retry_interval=10,
        )

        base_dir = Path(sys._MEIPASS) if getattr(sys, "frozen", False) \
                   else Path(__file__).parent
        self.bot_manager = BotManager(
            base_dir=base_dir,
            on_gift=self._on_gift,
            on_log=self._on_bot_log,
            on_overlay_event=self._on_overlay_event,
            get_top_user=self._get_top_user,
        )

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.engine.add_listener(self._on_engine_change)

    def _run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.server.start())
        except OSError as e:
            if "10048" in str(e) or "address already in use" in str(e).lower():
                self.status_signal.emit(
                    f"❌ Cổng {self.server.port} đang bị chiếm. "
                    f"Đóng app khác đang dùng cổng này."
                )
            else:
                self.status_signal.emit(f"❌ Lỗi server: {e}")
            return
        except Exception as e:
            self.status_signal.emit(f"❌ Lỗi server: {e}")
            return
        self.loop.run_forever()

    def _on_engine_change(self, snap):
        self.server.broadcast_sync(snap)

    def _on_gift(self, user, points, avatar="", display_name="", gift_name=""):
        """Gift thật TikTok — cộng điểm + gửi event + auto fake gift."""
        self.engine.add_score(
            user, points,
            avatar=avatar,
            display_name=display_name or user.lstrip("@"),
        )
        self.log_signal.emit(f"🎁 {user} +{points} (TikTok)")

        gift = gift_data.find_gift(gift_name)
        if not gift:
            gift = gift_data.gift_from_points(points)
        name, icon, gift_pts, effect, folder = gift

        # Gửi gift_event cho gift thật
        payload = {
            "user": user,
            "display_name": display_name or user.lstrip("@"),
            "avatar": avatar,
            "points": points,
            "gift_name": name,
            "gift_icon": icon,
            "gift_points": gift_pts,
            "gift_count": max(1, points // gift_pts) if gift_pts > 0 else 1,
            "effect": effect,
            "folder": folder,
            "is_bot": False,
            "is_real": True,
        }
        self.server.send_event_sync("gift_event", payload)

        # ★ AUTO FAKE GIFT
        fake = self.engine.pick_fake_gift_by_points(points)
        if fake:
            fake_payload = {
                "user": user,
                "display_name": display_name or user.lstrip("@"),
                "avatar": avatar,
                "points": points,
                "gift_name": fake["name"],
                "gift_icon": fake["icon"],
                "gift_points": points,
                "gift_count": 1,
                "effect": "text",
                "folder": fake["folder"],
                "is_bot": False,
                "is_real": False,
            }
            self.server.send_event_sync("gift_event", fake_payload)
            print(f"🎁 Auto fake gift: {fake['name']} ({points} pts)")

    def _on_status(self, text):
        self.status_signal.emit(text)

    def _on_bot_log(self, text):
        self.log_signal.emit(text)

    def _on_overlay_event(self, event_type: str, payload: dict):
        self.server.send_event_sync(event_type, payload)

    def _get_top_user(self):
        leaders = self.engine.get_leaders()
        if not leaders:
            return ("", 0)
        top_user = leaders[0]
        return (top_user, self.engine.scores.get(top_user, 0))

    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    voice_volume_signal = Signal(float)
    voice_status_signal = Signal(str)

        # ---------- Noise filter methods ----------
            # ---------- Auto-start mic ----------
            
            
    def _open_flash_dialog(self):
        """★ Dialog Flash — chọn user + cộng điểm vượt top 1."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
        from PySide6.QtCore import Qt

        # Lấy top 1 hiện tại
        leaders = self.worker.engine.get_leaders()
        if not leaders:
            QMessageBox.warning(
                self, "Chưa có ai",
                "Chưa có người chơi nào trên bảng.\n"
                "Hãy thêm người chơi trước."
            )
            return

        top_user = leaders[0]
        top_score = self.worker.engine.scores.get(top_user, 0)
        flash_amount = max(1, top_score // 5)

        # ═══ Dialog ═══
        dlg = QDialog(self)
        dlg.setWindowTitle("⚡ Flash")
        dlg.setMinimumWidth(500)
        dlg.setStyleSheet(f"""
            QDialog {{
                background: {COLORS['bg']};
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ─── HEADER ───
        header = QLabel("⚡  FLASH")
        header.setStyleSheet(f"""
            color: {COLORS['warning']};
            font-size: 18px;
            font-weight: 900;
            padding: 8px;
            letter-spacing: 2px;
            background: transparent;
            border: none;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # ─── TOP 1 INFO ───
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 215, 0, 0.08);
                border: 1px solid rgba(255, 215, 0, 0.3);
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        info_l = QVBoxLayout(info_box)
        info_l.setSpacing(4)

        top_info = QLabel(f"🥇 TOP 1: <b>{top_user}</b>")
        top_info.setStyleSheet(f"color: {COLORS['gold']}; font-size: 14px; font-weight: 700;")
        top_info.setTextFormat(Qt.RichText)
        info_l.addWidget(top_info)

        score_info = QLabel(f"📊 Điểm top 1: <b>{top_score:,}</b>")
        score_info.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        score_info.setTextFormat(Qt.RichText)
        info_l.addWidget(score_info)

        flash_info = QLabel(f"⚡ Sẽ cộng: <b>{flash_amount:,}</b> điểm (= 1/5 của {top_score:,})")
        flash_info.setStyleSheet(f"color: {COLORS['warning']}; font-size: 13px; font-weight: 700;")
        flash_info.setTextFormat(Qt.RichText)
        info_l.addWidget(flash_info)

        layout.addWidget(info_box)

        # ─── COMBO USER ───
        user_row = QHBoxLayout()
        user_row.setSpacing(10)

        user_label = QLabel("Người chơi:")
        user_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 13px; font-weight: 700;")
        user_label.setFixedWidth(100)
        user_row.addWidget(user_label)

        user_combo = QComboBox()
        user_combo.setMinimumHeight(42)
        user_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
        """)

        # Thêm tất cả user
        all_users = sorted(
            self.worker.engine.scores.keys(),
            key=lambda u: -self.worker.engine.scores[u]
        )
        bot_users = []
        for bot in self.worker.bot_manager.bots:
            if bot.user not in all_users:
                bot_users.append(bot.user)

        for u in all_users:
            score = self.worker.engine.scores.get(u, 0)
            bot = self.worker.bot_manager.get_by_user(u)
            prefix = "🤖 " if bot else "👤 "
            user_combo.addItem(f"{prefix}{u} — {score} điểm", u)

        for u in bot_users:
            bot = self.worker.bot_manager.get_by_user(u)
            prefix = "🤖 "
            user_combo.addItem(f"{prefix}{u} — 0 điểm", u)

        user_row.addWidget(user_combo, 1)
        layout.addLayout(user_row)

        # ─── BUTTONS ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

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
        btn_cancel.clicked.connect(dlg.reject)
        btn_row.addWidget(btn_cancel)

        btn_flash = QPushButton(f"⚡  FLASH +{flash_amount:,}")
        btn_flash.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['warning']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 800;
                min-width: 160px;
            }}
            QPushButton:hover {{ background: #ffcc33; }}
        """)
        btn_row.addWidget(btn_flash)

        layout.addLayout(btn_row)

        # ─── HANDLE ───
        def do_flash():
            user = user_combo.currentData()
            if not user:
                return

            # Cộng điểm
            display_name = self.worker.engine.display_names.get(user, user.lstrip("@"))
            avatar = self.worker.engine.avatars.get(user, "")

            # Bot avatar
            bot = self.worker.bot_manager.get_by_user(user)
            if bot:
                avatar = self.worker.bot_manager.get_avatar_url(bot)
                display_name = bot.display_name

            self.worker.engine.add_score(
                user, flash_amount,
                source="Flash",
                avatar=avatar,
                display_name=display_name,
            )

            # Gửi gift_event cho overlay
            if self.worker.bot_manager.gift_effects_enabled:
                self.worker.server.send_event_sync("gift_event", {
                    "user": user,
                    "display_name": display_name,
                    "avatar": avatar,
                    "points": flash_amount,
                    "gift_name": "Flash",
                    "gift_icon": "⚡",
                    "gift_points": flash_amount,
                    "gift_count": 1,
                    "effect": "text",
                    "folder": "flash",
                    "is_bot": False,
                    "is_real": False,
                })

            self._append_log(
                f"⚡ Flash: {user} +{flash_amount:,} "
                f"(vượt top 1 {top_user} — {top_score:,})"
            )

            dlg.accept()

        btn_flash.clicked.connect(do_flash)

        # ─── Show ───
        dlg.exec()
            
    def _open_gift_picker(self):
        """★ Mở dialog chọn gift."""
        from gift_picker import GiftPickerDialog

        dlg = GiftPickerDialog(self)
        if dlg.exec():
            gift = dlg.selected_gift
            if gift:
                name, icon, points, effect, folder = gift
                self._current_gift = gift

                # Update label
                self.selected_gift_label.setText(
                    f"{name}  ({points:,} coins)"
                )

                # Update gift_combo ẩn
                self.gift_combo.blockSignals(True)
                self.gift_combo.clear()
                self.gift_combo.addItem(
                    f"{name} ({points} điểm)",
                    (points, effect, name, icon, folder)
                )
                self.gift_combo.setCurrentIndex(0)
                self.gift_combo.blockSignals(False)

                # Update điểm + preview
                if hasattr(self, "_on_gift_changed"):
                    self._on_gift_changed(0)

                self._append_log(f"🎁 Đã chọn gift: {name} ({points:,} coins)")
    
    def _update_boss_preview(self):
        """Hiện preview 15 level, format đẹp."""
        import bosses as boss_data
        try:
            rows = boss_data.preview_all(
                self.hp_base_spin.value(),
                self.hp_mult_spin.value(),
                self.robux_base_spin.value(),
                self.robux_mult_spin.value(),
                self.gift_base_spin.value(),
                self.gift_mult_spin.value(),
                self.gift_max_spin.value(),
                levels=15,
            )

            lines = []
            lines.append("  Lv  Boss Name        HP          Reward        Gifts")
            lines.append("  " + "─" * 62)

            for r in rows:
                # Cảnh báo nếu HP vượt ngưỡng
                warn = ""
                if r["hp"] > 10_000_000_000:
                    warn = " ⚠"

                lines.append(
                    f"  {r['level']:>2}  "
                    f"{r['emoji']} {r['name']:<12s}  "
                    f"{r['hp']:>12,}  →  "
                    f"{r['robux']:>10,} R$  ·  "
                    f"{r['gift']:>8,} gifts{warn}"
                )

            self.boss_preview.setPlainText("\n".join(lines))
        except Exception as e:
            self.boss_preview.setPlainText(f"Preview error: {e}")
            
    def _on_completer_activated(self, text):
        """★ Khi user chọn từ autocomplete → set index đúng."""
        # Tìm index có tên khớp
        for i in range(self.gift_combo.count()):
            item_text = self.gift_combo.itemText(i)
            data = self.gift_combo.itemData(i)
            if data:
                name = data[2]
                if name.lower() == text.lower():
                    self.gift_combo.setCurrentIndex(i)
                    return
        # Nếu không match chính xác → tìm gần đúng
        for i in range(self.gift_combo.count()):
            data = self.gift_combo.itemData(i)
            if data:
                name = data[2]
                if text.lower() in name.lower():
                    self.gift_combo.setCurrentIndex(i)
                    return
            
    def _build_section_bot(self):
        """Section: Bot Test."""
        section = self._make_section("🤖  BOT TEST (Chỉ dùng để TEST)")
        l = section.layout()

        # Warning
        warn = QLabel(
            "⚠️  <b>CHỈ DÙNG ĐỂ TEST TOOL</b> — TUYỆT ĐỐI KHÔNG dùng bot khi live thật.<br>"
            "Dùng bot để lừa người xem tặng quà là <b>hành vi gian lận</b> và vi phạm Điều khoản TikTok."
        )
        warn.setStyleSheet(f"""
            color: {COLORS['danger']};
            background: rgba(255, 61, 90, 0.08);
            border: 1px solid rgba(255, 61, 90, 0.4);
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
        """)
        warn.setWordWrap(True)
        l.addWidget(warn)

        # Cấu hình bot
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(self._label("Số lượng thêm:"))
        self.bot_count_spin = NoWheelSpinBox()
        self.bot_count_spin.setRange(1, 200)
        self.bot_count_spin.setValue(5)
        self.bot_count_spin.setFixedWidth(90)
        self.bot_count_spin.setMinimumHeight(38)
        row1.addWidget(self.bot_count_spin)

        btn_add_bots = QPushButton("➕  Thêm bot")
        btn_add_bots.setStyleSheet(btn_style("primary", "md"))
        btn_add_bots.setMinimumHeight(38)
        btn_add_bots.clicked.connect(self._add_bots)
        row1.addWidget(btn_add_bots)

        btn_clear_bots = QPushButton("🗑  Xóa hết")
        btn_clear_bots.setStyleSheet(btn_style("default", "md"))
        btn_clear_bots.setMinimumHeight(38)
        btn_clear_bots.clicked.connect(self._clear_bots)
        row1.addWidget(btn_clear_bots)
        row1.addStretch()
        l.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(self._label("Tặng mỗi (giây):"))
        self.bot_int_min = NoWheelDoubleSpinBox()
        self.bot_int_min.setRange(0.5, 60)
        self.bot_int_min.setValue(3.0)
        self.bot_int_min.setSingleStep(0.5)
        self.bot_int_min.setFixedWidth(90)
        self.bot_int_min.setMinimumHeight(38)
        row2.addWidget(self.bot_int_min)

        row2.addWidget(QLabel("→"))
        self.bot_int_max = NoWheelDoubleSpinBox()
        self.bot_int_max.setRange(0.5, 120)
        self.bot_int_max.setValue(8.0)
        self.bot_int_max.setSingleStep(0.5)
        self.bot_int_max.setFixedWidth(90)
        self.bot_int_max.setMinimumHeight(38)
        row2.addWidget(self.bot_int_max)

        row2.addSpacing(20)
        row2.addWidget(self._label("Điểm mỗi lần:"))
        self.bot_pts_min = NoWheelSpinBox()
        self.bot_pts_min.setRange(1, 100000)
        self.bot_pts_min.setValue(5)
        self.bot_pts_min.setFixedWidth(90)
        self.bot_pts_min.setMinimumHeight(38)
        row2.addWidget(self.bot_pts_min)

        row2.addWidget(QLabel("→"))
        self.bot_pts_max = NoWheelSpinBox()
        self.bot_pts_max.setRange(1, 100000)
        self.bot_pts_max.setValue(100)
        self.bot_pts_max.setFixedWidth(90)
        self.bot_pts_max.setMinimumHeight(38)
        row2.addWidget(self.bot_pts_max)

        row2.addSpacing(20)
        row2.addWidget(self._label("Điểm tối đa:"))
        self.bot_max_score = NoWheelSpinBox()
        self.bot_max_score.setRange(0, 10_000_000)
        self.bot_max_score.setValue(0)
        self.bot_max_score.setFixedWidth(120)
        self.bot_max_score.setMinimumHeight(38)
        row2.addWidget(self.bot_max_score)

        btn_apply = QPushButton("💾  Áp dụng")
        btn_apply.setStyleSheet(btn_style("default", "md"))
        btn_apply.setMinimumHeight(38)
        btn_apply.clicked.connect(self._apply_bot_config)
        row2.addWidget(btn_apply)
        row2.addStretch()
        l.addLayout(row2)

        # Chase mode
        chase_box = QGroupBox("🎯  CHẾ ĐỘ RƯỢT ĐUỔI")
        chase_l = QHBoxLayout(chase_box)
        chase_l.setContentsMargins(12, 20, 12, 12)
        chase_l.setSpacing(10)

        chase_l.addWidget(self._label("Số bot rượt:"))
        self.chase_count_spin = NoWheelSpinBox()
        self.chase_count_spin.setRange(1, 5)
        self.chase_count_spin.setValue(2)
        self.chase_count_spin.setFixedWidth(70)
        self.chase_count_spin.setMinimumHeight(38)
        chase_l.addWidget(self.chase_count_spin)

        chase_l.addWidget(self._label("Hơn top 1:"))
        self.chase_gap_min = NoWheelSpinBox()
        self.chase_gap_min.setRange(1, 10000)
        self.chase_gap_min.setValue(20)
        self.chase_gap_min.setFixedWidth(90)
        self.chase_gap_min.setMinimumHeight(38)
        chase_l.addWidget(self.chase_gap_min)

        chase_l.addWidget(QLabel("→"))
        self.chase_gap_max = NoWheelSpinBox()
        self.chase_gap_max.setRange(1, 100000)
        self.chase_gap_max.setValue(80)
        self.chase_gap_max.setFixedWidth(90)
        self.chase_gap_max.setMinimumHeight(38)
        chase_l.addWidget(self.chase_gap_max)

        chase_l.addWidget(self._label("Mỗi (giây):"))
        self.chase_interval = NoWheelDoubleSpinBox()
        self.chase_interval.setRange(1.0, 60.0)
        self.chase_interval.setValue(4.0)
        self.chase_interval.setSingleStep(0.5)
        self.chase_interval.setFixedWidth(90)
        self.chase_interval.setMinimumHeight(38)
        chase_l.addWidget(self.chase_interval)

        btn_apply_chase = QPushButton("💾")
        btn_apply_chase.setStyleSheet(btn_style("default", "md"))
        btn_apply_chase.setFixedWidth(50)
        btn_apply_chase.setMinimumHeight(38)
        btn_apply_chase.clicked.connect(self._apply_chase_config)
        chase_l.addWidget(btn_apply_chase)

        btn_create_chasers = QPushButton("🎯  Tạo")
        btn_create_chasers.setStyleSheet(btn_style("warning", "md"))
        btn_create_chasers.setMinimumHeight(38)
        btn_create_chasers.clicked.connect(self._create_chasers)
        chase_l.addWidget(btn_create_chasers)
        chase_l.addStretch()
        l.addWidget(chase_box)

        # Comment Roblox
        cmt_row = QHBoxLayout()
        cmt_row.setSpacing(10)
        self.cmt_enabled_chk = QCheckBox("💬 Bật comment Roblox khi bot thắng")
        self.cmt_enabled_chk.setChecked(True)
        self.cmt_enabled_chk.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        self.cmt_enabled_chk.toggled.connect(self._toggle_roblox_cmt)
        cmt_row.addWidget(self.cmt_enabled_chk)

        cmt_row.addSpacing(15)
        cmt_row.addWidget(self._label("Delay:"))
        self.cmt_delay = NoWheelDoubleSpinBox()
        self.cmt_delay.setRange(0.0, 10.0)
        self.cmt_delay.setValue(1.5)
        self.cmt_delay.setSingleStep(0.5)
        self.cmt_delay.setFixedWidth(80)
        self.cmt_delay.setMinimumHeight(38)
        cmt_row.addWidget(self.cmt_delay)

        btn_apply_cmt = QPushButton("💾")
        btn_apply_cmt.setStyleSheet(btn_style("default", "md"))
        btn_apply_cmt.setFixedWidth(50)
        btn_apply_cmt.setMinimumHeight(38)
        btn_apply_cmt.clicked.connect(self._apply_cmt_config)
        cmt_row.addWidget(btn_apply_cmt)

        btn_test_cmt = QPushButton("🧪  Test cmt")
        btn_test_cmt.setStyleSheet(btn_style("primary", "sm"))
        btn_test_cmt.setMinimumHeight(38)
        btn_test_cmt.clicked.connect(self._test_roblox_cmt)
        cmt_row.addWidget(btn_test_cmt)
        cmt_row.addStretch()
        l.addLayout(cmt_row)

        # Gift effects
        fx_row = QHBoxLayout()
        self.fx_enabled_chk = QCheckBox("🎆 Bật hiệu ứng quà tặng")
        self.fx_enabled_chk.setChecked(True)
        self.fx_enabled_chk.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        self.fx_enabled_chk.toggled.connect(self._toggle_gift_fx)
        fx_row.addWidget(self.fx_enabled_chk)
        fx_row.addStretch()
        l.addLayout(fx_row)

        # Danh sách bot
        list_row = QHBoxLayout()
        list_row.setSpacing(10)

        self.bot_list = QListWidget()
        self.bot_list.setMinimumHeight(200)
        self.bot_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }}
            QListWidget::item {{ padding: 8px; }}
        """)
        list_row.addWidget(self.bot_list, 1)

        list_btns = QVBoxLayout()
        list_btns.setSpacing(6)

        btn_reload_bots = QPushButton("🔄  Tải lại")
        btn_reload_bots.setStyleSheet(btn_style("default", "sm"))
        btn_reload_bots.setMinimumHeight(34)
        btn_reload_bots.clicked.connect(self._refresh_bot_list)
        list_btns.addWidget(btn_reload_bots)

        btn_open_bots = QPushButton("📁  assets/bots")
        btn_open_bots.setStyleSheet(btn_style("default", "sm"))
        btn_open_bots.setMinimumHeight(34)
        btn_open_bots.clicked.connect(self._open_bots_folder)
        list_btns.addWidget(btn_open_bots)

        btn_open_gifts = QPushButton("🎁  assets/gifts")
        btn_open_gifts.setStyleSheet(btn_style("default", "sm"))
        btn_open_gifts.setMinimumHeight(34)
        btn_open_gifts.clicked.connect(self._open_gifts_folder)
        list_btns.addWidget(btn_open_gifts)

        list_btns.addStretch()
        list_row.addLayout(list_btns)
        l.addLayout(list_row)

        # Nút bật/tắt bot
        row_btns = QHBoxLayout()
        row_btns.setSpacing(10)
        self.btn_bot_start = QPushButton("▶   BẬT BOT")
        self.btn_bot_start.setStyleSheet(btn_style("warning", "lg"))
        self.btn_bot_start.setMinimumHeight(48)
        self.btn_bot_start.clicked.connect(self._start_bots)
        row_btns.addWidget(self.btn_bot_start, 1)

        self.btn_bot_stop = QPushButton("⏹   TẮT BOT")
        self.btn_bot_stop.setStyleSheet(btn_style("danger", "lg"))
        self.btn_bot_stop.setMinimumHeight(48)
        self.btn_bot_stop.clicked.connect(self._stop_bots)
        self.btn_bot_stop.setEnabled(False)
        row_btns.addWidget(self.btn_bot_stop, 1)
        l.addLayout(row_btns)

        # Status
        self.bot_status = QLabel("🤖  Bot đã tắt")
        self.bot_status.setStyleSheet(f"""
            padding: 10px 16px;
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        l.addWidget(self.bot_status)

        return section
    
    def _build_section_log(self):
        """Section: Nhật ký."""
        section = self._make_section("📜  NHẬT KÝ SỰ KIỆN")
        l = section.layout()

        header = QHBoxLayout()
        header.addStretch()
        btn_clear = QPushButton("🗑  Xóa nhật ký")
        btn_clear.setStyleSheet(btn_style("default", "sm"))
        btn_clear.setMinimumHeight(34)
        btn_clear.clicked.connect(lambda: self.log_view.clear())
        header.addWidget(btn_clear)
        l.addLayout(header)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(300)
        self.log_view.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg']};
                color: {COLORS['success']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        l.addWidget(self.log_view)
        return section
    

            
    def _build_section_theme(self):
        """Section: Theme — chọn theme cho overlay."""
        section = self._make_section("🎨  THEME")
        l = section.layout()

        # Row chính: list bên trái + preview bên phải
        row = QHBoxLayout()
        row.setSpacing(14)

        # ─── Cột trái: danh sách theme ───
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        self.theme_list = QListWidget()
        self.theme_list.setMinimumWidth(280)
        self.theme_list.setMinimumHeight(400)
        self.theme_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 6px;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 12px 14px;
                border-radius: 8px;
                margin-bottom: 4px;
            }}
            QListWidget::item:hover {{ background: {COLORS['card_hover']}; }}
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        self.theme_list.itemClicked.connect(self._on_theme_selected)
        left_box.addWidget(self.theme_list, 1)

        btn_row = QHBoxLayout()
        btn_apply = QPushButton("🎨  ÁP DỤNG")
        btn_apply.setStyleSheet(btn_style("success", "lg"))
        btn_apply.setMinimumHeight(48)
        btn_apply.clicked.connect(self._apply_selected_theme)
        btn_row.addWidget(btn_apply, 1)

        btn_reload = QPushButton("🔄")
        btn_reload.setStyleSheet(btn_style("default", "md"))
        btn_reload.setMinimumHeight(48)
        btn_reload.setFixedWidth(60)
        btn_reload.setToolTip("Tải lại danh sách theme")
        btn_reload.clicked.connect(self._reload_themes)
        btn_row.addWidget(btn_reload)
        left_box.addLayout(btn_row)

        row.addLayout(left_box, 1)

        # ─── Cột phải: preview ───
        right_box = QVBoxLayout()
        right_box.setSpacing(8)

        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        url_row.addWidget(self._label("URL Preview:"))
        self.preview_url = QLineEdit()
        self.preview_url.setReadOnly(True)
        self.preview_url.setMinimumHeight(38)
        self.preview_url.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg']};
                color: {COLORS['primary_hi']};
                border: 1px solid {COLORS['primary']};
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }}
        """)
        url_row.addWidget(self.preview_url, 1)

        btn_copy_url = QPushButton("📋")
        btn_copy_url.setStyleSheet(btn_style("default", "md"))
        btn_copy_url.setFixedWidth(50)
        btn_copy_url.setMinimumHeight(38)
        btn_copy_url.clicked.connect(
            lambda: self._copy_text(self.preview_url.text(), btn_copy_url)
        )
        url_row.addWidget(btn_copy_url)
        right_box.addLayout(url_row)

        # Web view preview
        if HAS_WEBENGINE:
            self.preview_view = QWebEngineView()
            self.preview_view.setMinimumHeight(400)
            settings = self.preview_view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            self.preview_view.page().setBackgroundColor(QColor("#0a0a12"))
            right_box.addWidget(self.preview_view, 1)
        else:
            no_web = QLabel("⚠️  Chưa cài PySide6-WebEngine\n\nChạy:\nuv add PySide6-WebEngine\nuv sync")
            no_web.setStyleSheet(f"""
                color: {COLORS['warning']};
                background: {COLORS['bg']};
                border: 2px dashed {COLORS['warning']};
                border-radius: 12px;
                padding: 40px;
                font-size: 14px;
                font-weight: 600;
            """)
            no_web.setAlignment(Qt.AlignCenter)
            no_web.setMinimumHeight(400)
            right_box.addWidget(no_web, 1)

        row.addLayout(right_box, 2)
        l.addLayout(row)

        # Load themes
        self._reload_themes()

        return section
            
    def _build_topbar(self):
        """Topbar: logo + kết nối + VOUCHES."""
        topbar = QFrame()
        topbar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['card']},
                    stop:1 {COLORS['bg_alt']});
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        topbar.setFixedHeight(90)
        t_l = QHBoxLayout(topbar)
        t_l.setContentsMargins(20, 12, 20, 12)
        t_l.setSpacing(16)

        # Logo
        logo = QLabel("🎁")
        logo.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        t_l.addWidget(logo)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("TikTok Auction Studio")
        title.setStyleSheet(f"""
            font-size: 16px; font-weight: 900;
            color: {COLORS['primary_hi']};
            letter-spacing: 1px;
            background: transparent; border: none;
        """)
        subtitle = QLabel("Version 1.0 · Đấu giá + Boss + Robux")
        subtitle.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']}; background: transparent; border: none;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        t_l.addLayout(title_box)
        t_l.addSpacing(20)

        # Kết nối
        self.conn_indicator = QLabel("⚪ Chưa kết nối TikTok")
        self.conn_indicator.setStyleSheet(f"""
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            padding: 8px 16px;
            border-radius: 18px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid {COLORS['border']};
        """)
        t_l.addWidget(self.conn_indicator)
                # ★ Status text nhỏ — đang chờ / đã kết nối
        self.conn_status_text = QLabel("")
        self.conn_status_text.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0 8px;
        """)
        t_l.addWidget(self.conn_status_text)

        self.live_input = QLineEdit()
        self.live_input.setPlaceholderText("@username hoặc link live")
        self.live_input.setMinimumHeight(38)
        self.live_input.setMinimumWidth(220)
        self.live_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
            }}
        """)
        self.live_input.returnPressed.connect(self.connect_tiktok)
        t_l.addWidget(self.live_input)

        self.btn_connect = QPushButton("🔗  Kết nối")
        self.btn_connect.setStyleSheet(btn_style("primary", "md"))
        self.btn_connect.setMinimumHeight(38)
        self.btn_connect.setFixedWidth(120)
        self.btn_connect.clicked.connect(self.connect_tiktok)
        t_l.addWidget(self.btn_connect)

        self.btn_disconnect = QPushButton("⛔  Ngắt")
        self.btn_disconnect.setStyleSheet(btn_style("danger", "md"))
        self.btn_disconnect.setMinimumHeight(38)
        self.btn_disconnect.setFixedWidth(100)
        self.btn_disconnect.clicked.connect(self.disconnect_tiktok)
        self.btn_disconnect.setEnabled(False)
        t_l.addWidget(self.btn_disconnect)

        t_l.addStretch()

        # VOUCHES
        vouch_box = QFrame()
        vouch_box.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        vouch_l = QHBoxLayout(vouch_box)
        vouch_l.setContentsMargins(14, 6, 14, 6)
        vouch_l.setSpacing(8)
        vouch_icon = QLabel("⭐")
        vouch_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        vouch_l.addWidget(vouch_icon)
        vouch_label = QLabel("VOUCHES")
        vouch_label.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {COLORS['text_muted']}; letter-spacing: 2px; background: transparent; border: none;")
        vouch_l.addWidget(vouch_label)
        self.vouch_display = QLabel("0")
        self.vouch_display.setStyleSheet(f"font-size: 18px; font-weight: 900; color: {COLORS['gold']}; background: transparent; border: none;")
        vouch_l.addWidget(self.vouch_display)
        t_l.addWidget(vouch_box)

        return topbar
            
    def _build_col_players(self):
        """Cột 2: Người tham gia."""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        box.setMinimumHeight(520)   # ★ Cố định chiều cao
        box.setMaximumHeight(600)   # ★
        l = QVBoxLayout(box)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(10)

        # Header
        header = QLabel("👥  NGƯỜI THAM GIA")
        header.setStyleSheet(f"""
            font-size: 13px; font-weight: 900;
            color: {COLORS['success']};
            letter-spacing: 2px;
            padding: 10px;
            background: rgba(0, 214, 143, 0.08);
            border: 1px solid rgba(0, 214, 143, 0.3);
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignCenter)
        l.addWidget(header)

        # List
        self.ranking_list = QListWidget()
        self.ranking_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        l.addWidget(self.ranking_list, 1)

        # Actions
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(38)
        self.user_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
            }}
        """)
        action_row.addWidget(self.user_combo, 1)

        btn_balance = QPushButton("⚖  Cân bằng")
        btn_balance.setStyleSheet(btn_style("warning", "md"))
        btn_balance.setMinimumHeight(38)
        btn_balance.clicked.connect(self.balance_top)
        action_row.addWidget(btn_balance)

                # ⚡ Nút Flash mới — mở dialog chọn user + flash
        btn_flash = QPushButton("⚡  Flash")
        btn_flash.setStyleSheet(btn_style("warning", "md"))
        btn_flash.setMinimumHeight(38)
        btn_flash.setToolTip("Chọn user → Flash vượt top 1 một khoảng = 1/5 điểm top 1")
        btn_flash.clicked.connect(self._open_flash_dialog)
        action_row.addWidget(btn_flash)

        l.addLayout(action_row)

        # Footer
        footer = QHBoxLayout()
        self.players_count_label = QLabel("Tổng tham gia: 0")
        self.players_count_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px; font-weight: 700;"
        )
        footer.addWidget(self.players_count_label)
        footer.addStretch()

        self.points_count_label = QLabel("Tổng kim cương: 0")
        self.points_count_label.setStyleSheet(
            f"color: {COLORS['gold']}; font-size: 12px; font-weight: 700;"
        )
        footer.addWidget(self.points_count_label)

        btn_add_player = QPushButton("➕")
        btn_add_player.setStyleSheet(btn_style("success", "sm"))
        btn_add_player.setFixedWidth(44)
        btn_add_player.setMinimumHeight(32)
        btn_add_player.clicked.connect(self._add_player_manual)
        footer.addWidget(btn_add_player)
        l.addLayout(footer)

        return box
            
    def _build_col_winners(self):
        """Cột 1: Người thắng."""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        box.setMinimumHeight(520)   # ★ Cố định chiều cao
        box.setMaximumHeight(600)   # ★
        l = QVBoxLayout(box)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(10)

        # Header
        header = QLabel("🏆  NGƯỜI THẮNG")
        header.setStyleSheet(f"""
            font-size: 13px; font-weight: 900;
            color: {COLORS['gold']};
            letter-spacing: 2px;
            padding: 10px;
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignCenter)
        l.addWidget(header)

        # List
        self.winners_list = QListWidget()
        self.winners_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        l.addWidget(self.winners_list, 1)

        # Footer
        footer = QHBoxLayout()
        self.winners_count_label = QLabel("Tổng thắng: 0")
        self.winners_count_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px; font-weight: 700;"
        )
        footer.addWidget(self.winners_count_label)
        footer.addStretch()

        btn_clear_winners = QPushButton("🗑")
        btn_clear_winners.setStyleSheet(btn_style("danger", "sm"))
        btn_clear_winners.setFixedWidth(44)
        btn_clear_winners.setMinimumHeight(32)
        btn_clear_winners.clicked.connect(self._clear_winners)
        footer.addWidget(btn_clear_winners)
        l.addLayout(footer)

        return box
            
    def _on_overlay_selected(self, idx):
        """★ Cập nhật URL khi chọn overlay."""
        key = self.overlay_selector.currentData()
        if not key:
            return
        srv = self.worker.server
        urls = srv.build_all_local()
        if key in urls:
            self.overlay_url_input.setText(urls[key])

    def _clear_winners(self):
        """★ Xóa danh sách người thắng."""
        reply = QMessageBox.question(
            self, "Xóa người thắng",
            "Xóa toàn bộ danh sách người thắng?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.winners_list.clear()
            self._append_log("🗑 Đã xóa danh sách người thắng")

    def _add_player_manual(self):
        """★ Thêm người chơi thủ công."""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self, "Thêm người chơi",
            "Nhập @username hoặc tên:"
        )
        if ok and name:
            if not name.startswith("@"):
                name = "@" + name
            self.worker.engine.add_score(name, 0)
            self._refresh_user_combo()
            self._append_log(f"➕ Đã thêm {name}")

    def _update_topbar_vouch(self, vouch):
        """★ Cập nhật VOUCHES trên topbar."""
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText(str(vouch))

    def _on_boss_level_changed(self, level):
        import bosses as boss_data
        self.worker.engine.set_boss_level(level)
        b = boss_data.get_boss_name(level)
        hp = self.worker.engine.get_boss_hp(level)
        reward = boss_data.get_robux_reward(
            level,
            self.robux_base_spin.value(),
            self.robux_mult_spin.value(),
        )
        gift = self.worker.engine.get_boss_gift_count(level)
        self.boss_info_label.setText(
            f"Lv.{level} {b['emoji']} {b['name']} — "
            f"{hp:,} HP — {reward:,} R$ — {gift:,} gifts"
        )
    def _on_auto_reset_changed(self):
        """★ Cập nhật config auto reset boss + pot."""
        self.worker.engine.set_auto_reset(
            boss=self.auto_reset_boss_chk.isChecked(),
            pot=self.auto_reset_pot_chk.isChecked(),
            boss_level=self.auto_reset_level_spin.value(),
        )

    def _reset_boss(self):
        self.worker.engine.reset_boss()
        self._append_log("Boss healed")
        
    def _on_auto_reset_changed(self):
        """★ Cập nhật config auto reset boss + pot."""
        self.worker.engine.set_auto_reset(
            boss=self.auto_reset_boss_chk.isChecked(),
            pot=self.auto_reset_pot_chk.isChecked(),
            boss_level=self.auto_reset_level_spin.value(),
        )

    def _apply_boss_config(self):
        self.worker.engine.set_boss_config(
            hp_base=self.hp_base_spin.value(),
            hp_mult=self.hp_mult_spin.value(),
            robux_base=self.robux_base_spin.value(),
            robux_mult=self.robux_mult_spin.value(),
            gift_base=self.gift_base_spin.value(),
            gift_mult=self.gift_mult_spin.value(),
            gift_max=self.gift_max_spin.value(),
        )
        self.worker.engine.apply_boss_config()
        self._append_log("Boss config applied")

    def _on_reset_pot_changed(self, value):
        self.worker.engine.set_reset_robux_value(value)

    def _reset_robux_pot(self):
        reply = QMessageBox.question(
            self, "Reset Robux Pot",
            "Reset the Robux pot to default value?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.worker.engine.reset_robux_pot()
            self._append_log("Robux pot reset")

    def _on_min_coins_changed(self, value):
        self.worker.engine.set_min_coins(value)

    def _on_vouch_changed(self, value):
        self.worker.engine.set_vouch(value)

    def _reset_vouch(self):
        self.worker.engine.reset_vouch()
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText("0")
        self._append_log("🎮 Đã reset vouch = 0")
        
    def _on_completer_selected(self, text):
        """★ Khi user chọn từ completer → set index đúng."""
        # Tìm item có tên khớp
        for i in range(self.gift_combo.count()):
            data = self.gift_combo.itemData(i)
            if data and data[2].lower() == text.lower():
                self.gift_combo.setCurrentIndex(i)
                return
    
    def _auto_start_mic(self):
        """Tự động bật VoiceListener khi app khởi động."""
        try:
            self.voice_listener = VoiceListener(
                on_volume=lambda v: self.voice_volume_signal.emit(v),
                on_status=lambda s: self.voice_status_signal.emit(s),
                on_speak_audio=None,   # Không cần vì không fake giọng
            )

            # Cấu hình mặc định (chống ồn tốt nhất)
            self.voice_listener.threshold = 12        # Ngưỡng mở miệng
            self.voice_listener.sensitivity = 2.5     # Độ nhạy
            self.voice_listener.noise_floor = 300     # Nền
            self.voice_listener.noise_gate_enabled = True
            self.voice_listener.noise_gate_threshold = 200
            self.voice_listener.highpass_enabled = True
            self.voice_listener.highpass_cutoff = 80
            self.voice_listener.smoothing_enabled = True

            self.voice_listener.start()
            self._append_log("🎤 Mic đã tự động bật — nói để nhân vật nhép miệng")

        except Exception as e:
            self._append_log(f"❌ Không bật được mic tự động: {e}")
        def _collect_sample(volume):
            if len(self._noise_samples) < 40:  # ~2s
                self._noise_samples.append(volume)
            else:
                # Đã đủ mẫu → tính trung bình
                avg = sum(self._noise_samples) / len(self._noise_samples)
                gate = int(avg * 1.5) + 50
                self.noise_gate_threshold.setValue(gate)
                self.voice_listener.noise_gate_threshold = gate

                self._append_log(
                    f"🎚️ Đã đo nhiễu nền: avg={avg:.1f}% → "
                    f"gate={gate}"
                )
                QMessageBox.information(
                    self, "Đo xong",
                    f"Nhiễu nền trung bình: {avg:.1f}%\n"
                    f"Ngưỡng Noise Gate mới: {gate}"
                )
                # Ngắt sample
                self._noise_samples = None

        # Tạm gắn callback
        original_cb = self.voice_listener.on_volume

        def temp_cb(v):
            original_cb(v)
            if self._noise_samples is not None:
                _collect_sample(v)

        self.voice_listener.on_volume = temp_cb

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎁 TikTok Auction Tool")
        self._gift_populating = False
        self.resize(1300, 950)
        self.setMinimumSize(1100, 750)

        self.worker = AsyncWorker()
        self.worker.log_signal.connect(self._append_log)
        self.worker.status_signal.connect(self._set_status)

        self.tiktok_connected = False
        self.tiktok_username = ""

                # Voice state (chỉ dùng listener, không UI)
        self.voice_listener = None
        self.voice_volume_signal.connect(self._on_voice_volume)
        self.voice_status_signal.connect(self._on_voice_status)

        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self._tick)
        self.tick_timer.start(250)

        self._build_ui()
        self._render_state(self.worker.engine.snapshot())
        self._update_overlay_links()
        self._update_start_button()
        self._refresh_user_combo()

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._vtuber_say)
                # ★ Auto-start mic (chạy ngầm)
        QTimer.singleShot(1500, self._auto_start_mic)
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._vtuber_say)

        # ★ Nhắc kết nối TikTok Live khi mở tool (delay 1s để UI load xong)
        QTimer.singleShot(1000, self._check_live_connection)

        # ★ Auto-start mic (chạy ngầm)
        QTimer.singleShot(1500, self._auto_start_mic)

    # ---------- UI ----------
    def _build_ui(self):
        """Layout dọc — tất cả section xếp chồng."""
        # ★ Bọc toàn bộ trong scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {COLORS['bg']}; border: none; }}
            QScrollArea > QWidget > QWidget {{ background: {COLORS['bg']}; }}
        """)
        self.setCentralWidget(scroll)

        central = QWidget()
        scroll.setWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # ═══ 1. TOPBAR ═══
        root.addWidget(self._build_topbar())

        # ═══ 2. BẢNG ĐIỀU KHIỂN (3 cột) ═══
        control_row = QHBoxLayout()
        control_row.setSpacing(12)
        control_row.addWidget(self._build_col_winners(), 1)
        control_row.addWidget(self._build_col_players(), 1)
        control_row.addWidget(self._build_col_control(), 1)
        root.addLayout(control_row)

        # ═══ 3. FAKE USER GIFT ═══
        root.addWidget(self._build_section_fake_gift())

        # ═══ 4. LIVE URLS ═══
        root.addWidget(self._build_section_live_urls())

        # ═══ 5. BOSS SETTINGS ═══
        root.addWidget(self._build_section_boss())

        # ═══ 6. AUTO RESET ═══
        root.addWidget(self._build_section_auto_reset())

        # ═══ 7. AUTO NEXT BOSS ═══
        root.addWidget(self._build_section_auto_next())

        # ═══ 8. ROBUX POT ═══
        root.addWidget(self._build_section_pot())

        # ═══ 9. NHẬT KÝ (build TRƯỚC để có log_view) ═══
        root.addWidget(self._build_section_log())

        # ═══ 10. THEME ═══
        root.addWidget(self._build_section_theme())

        # ═══ 11. BOT TEST ═══
        root.addWidget(self._build_section_bot())

        # ═══ 12. HƯỚNG DẪN ═══
        root.addWidget(self._build_section_help())
        
    def _build_section_help(self):
        """Section: Hướng dẫn sử dụng."""
        section = self._make_section("❓  HƯỚNG DẪN SỬ DỤNG")
        l = section.layout()

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMinimumHeight(400)
        help_text.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 20px;
                font-size: 13px;
            }}
        """)
        help_text.setHtml(f"""
        <style>
            h2 {{ color: {COLORS['primary_hi']}; }}
            h3 {{ color: {COLORS['gold']}; margin-top: 20px; }}
            code {{ background: {COLORS['card']}; padding: 2px 8px;
                    border-radius: 4px; color: {COLORS['success']}; }}
            li {{ margin-bottom: 6px; line-height: 1.7; }}
        </style>

        <h2>🎁 TikTok Auction Tool — Hướng dẫn</h2>

        <h3>⚡ Quy trình</h3>
        <ol>
            <li>Nhập <code>@username</code> vào ô trên cùng → bấm <b>🔗 Kết nối</b></li>
            <li>Copy link overlay → dán vào TikTok Studio</li>
            <li>Bấm <b>▶ BẮT ĐẦU</b> để bắt đầu ván đấu giá</li>
        </ol>

        <h3>📺 Danh sách overlay</h3>
        <ul>
            <li><b>Bảng đấu giá</b> — BXH + timer</li>
            <li><b>Fake Comment</b> — comment Roblox</li>
            <li><b>Fake Gift FX</b> — hiệu ứng quà lớn</li>
            <li><b>Fake Gift Text</b> — dòng chữ quà nhỏ (LIVE chat)</li>
            <li><b>Boss + Pot</b> — thanh máu boss + hũ Robux</li>
            <li><b>Gift Chat</b> — chat gift ảo (chỉ hiện bot/manual)</li>
        </ul>

        <h3>👹 Boss System</h3>
        <ul>
            <li>Boss có HP giảm dần khi người chơi tặng quà</li>
            <li>Mỗi 1 điểm = 1 máu boss</li>
            <li>Boss chết → rơi Robux vào hũ</li>
            <li>Auto lên level sau khi kill</li>
        </ul>

        <h3>🛡️ Nhắc nhở</h3>
        <ul>
            <li>Công bố luật đầu live</li>
            <li>KHÔNG dùng bot khi live thật</li>
        </ul>
        """)
        l.addWidget(help_text)
        return section
        
    def _build_section_auto_next(self):
        section = self._make_section("⚡  AUTO NEXT BOSS")
        l = section.layout()

        row = QHBoxLayout()
        row.setSpacing(15)

        self.auto_next_chk = QCheckBox("⚡ Auto next boss when defeated")
        self.auto_next_chk.setChecked(True)
        self.auto_next_chk.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: 700;")
        self.auto_next_chk.toggled.connect(self._on_auto_next_toggled)
        row.addWidget(self.auto_next_chk)

        row.addSpacing(15)
        row.addWidget(self._label("Delay (giây):"))
        self.auto_next_delay_spin = NoWheelDoubleSpinBox()
        self.auto_next_delay_spin.setRange(0.5, 30.0)
        self.auto_next_delay_spin.setValue(3.0)
        self.auto_next_delay_spin.setSingleStep(0.5)
        self.auto_next_delay_spin.setFixedWidth(90)
        self.auto_next_delay_spin.setMinimumHeight(38)
        self.auto_next_delay_spin.setSuffix(" s")
        self.auto_next_delay_spin.valueChanged.connect(self._on_auto_next_delay_changed)
        row.addWidget(self.auto_next_delay_spin)

        row.addStretch()
        l.addLayout(row)
        return section
    
    def _build_section_pot(self):
        section = self._make_section("💰  ROBUX POT")
        l = section.layout()

        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(self._label("Reset value:"))
        self.reset_pot_spin = NoWheelSpinBox()
        self.reset_pot_spin.setRange(0, 10_000_000)
        self.reset_pot_spin.setValue(500)
        self.reset_pot_spin.setFixedWidth(140)
        self.reset_pot_spin.setMinimumHeight(40)
        self.reset_pot_spin.setGroupSeparatorShown(True)
        self.reset_pot_spin.valueChanged.connect(self._on_reset_pot_changed)
        row.addWidget(self.reset_pot_spin)

        self.pot_current_label = QLabel("Current: 500")
        self.pot_current_label.setStyleSheet(f"color: {COLORS['gold']}; font-size: 14px; font-weight: 700;")
        row.addWidget(self.pot_current_label)

        btn_reset_pot = QPushButton("🗑  Reset Pot Now")
        btn_reset_pot.setStyleSheet(btn_style("danger", "md"))
        btn_reset_pot.setMinimumHeight(40)
        btn_reset_pot.clicked.connect(self._reset_robux_pot)
        row.addWidget(btn_reset_pot)

        row.addStretch()
        l.addLayout(row)
        return section
        
    def _build_section_auto_reset(self):
        section = self._make_section("🔄  AUTO RESET")
        l = section.layout()

        row = QHBoxLayout()
        row.setSpacing(15)

        self.auto_reset_boss_chk = QCheckBox("🔄 Auto reset Boss")
        self.auto_reset_boss_chk.setChecked(True)
        self.auto_reset_boss_chk.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: 700;")
        self.auto_reset_boss_chk.toggled.connect(self._on_auto_reset_changed)
        row.addWidget(self.auto_reset_boss_chk)

        row.addWidget(self._label("→ Level:"))
        self.auto_reset_level_spin = NoWheelSpinBox()
        self.auto_reset_level_spin.setRange(1, 15)
        self.auto_reset_level_spin.setValue(1)
        self.auto_reset_level_spin.setFixedWidth(70)
        self.auto_reset_level_spin.setMinimumHeight(38)
        self.auto_reset_level_spin.valueChanged.connect(self._on_auto_reset_changed)
        row.addWidget(self.auto_reset_level_spin)

        row.addSpacing(20)

        self.auto_reset_pot_chk = QCheckBox("💰 Auto reset Pot")
        self.auto_reset_pot_chk.setChecked(True)
        self.auto_reset_pot_chk.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: 700;")
        self.auto_reset_pot_chk.toggled.connect(self._on_auto_reset_changed)
        row.addWidget(self.auto_reset_pot_chk)

        row.addStretch()
        l.addLayout(row)
        return section
        
    def _build_section_boss(self):
        """Section: Boss Settings."""
        section = self._make_section("👹  BOSS SETTINGS")
        l = section.layout()

        # Row 1: Level + Info + Heal
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row1.addWidget(self._label("Level:"))
        self.boss_level_spin = NoWheelSpinBox()
        self.boss_level_spin.setRange(1, 15)
        self.boss_level_spin.setValue(1)
        self.boss_level_spin.setFixedWidth(80)
        self.boss_level_spin.setMinimumHeight(40)
        self.boss_level_spin.valueChanged.connect(self._on_boss_level_changed)
        row1.addWidget(self.boss_level_spin)

        self.boss_info_label = QLabel("Lv.1 🟢 SLIME — 500 HP — 100 R$")
        self.boss_info_label.setStyleSheet(f"""
            color: {COLORS['danger']};
            background: rgba(255, 61, 90, 0.1);
            border: 1px solid rgba(255, 61, 90, 0.4);
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 800;
        """)
        row1.addWidget(self.boss_info_label, 1)

        btn_heal = QPushButton("🔄  Heal Boss")
        btn_heal.setStyleSheet(btn_style("warning", "md"))
        btn_heal.setMinimumHeight(40)
        btn_heal.setFixedWidth(140)
        btn_heal.clicked.connect(self._reset_boss)
        row1.addWidget(btn_heal)
        l.addLayout(row1)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px;")
        l.addWidget(sep)

        # Grid config
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(12)

        grid.addWidget(self._label("HP Base (Lv.1):"), 0, 0)
        self.hp_base_spin = NoWheelSpinBox()
        self.hp_base_spin.setRange(1, 10_000_000)
        self.hp_base_spin.setValue(500)
        self.hp_base_spin.setMinimumHeight(40)
        self.hp_base_spin.setGroupSeparatorShown(True)
        grid.addWidget(self.hp_base_spin, 0, 1)

        grid.addWidget(self._label("HP Multiplier:"), 1, 0)
        self.hp_mult_spin = NoWheelDoubleSpinBox()
        self.hp_mult_spin.setRange(1.0, 10.0)
        self.hp_mult_spin.setValue(2.0)
        self.hp_mult_spin.setSingleStep(0.1)
        self.hp_mult_spin.setMinimumHeight(40)
        self.hp_mult_spin.setSuffix(" x")
        grid.addWidget(self.hp_mult_spin, 1, 1)

        grid.addWidget(self._label("Robux Base (Lv.1):"), 0, 2)
        self.robux_base_spin = NoWheelSpinBox()
        self.robux_base_spin.setRange(0, 10_000_000)
        self.robux_base_spin.setValue(100)
        self.robux_base_spin.setMinimumHeight(40)
        self.robux_base_spin.setGroupSeparatorShown(True)
        grid.addWidget(self.robux_base_spin, 0, 3)

        grid.addWidget(self._label("Robux Multiplier:"), 1, 2)
        self.robux_mult_spin = NoWheelDoubleSpinBox()
        self.robux_mult_spin.setRange(1.0, 10.0)
        self.robux_mult_spin.setValue(2.0)
        self.robux_mult_spin.setSingleStep(0.1)
        self.robux_mult_spin.setMinimumHeight(40)
        self.robux_mult_spin.setSuffix(" x")
        grid.addWidget(self.robux_mult_spin, 1, 3)

        grid.addWidget(self._label("Gift Base (Lv.1):"), 0, 4)
        self.gift_base_spin = NoWheelSpinBox()
        self.gift_base_spin.setRange(1, 100_000)
        self.gift_base_spin.setValue(1)
        self.gift_base_spin.setMinimumHeight(40)
        grid.addWidget(self.gift_base_spin, 0, 5)

        grid.addWidget(self._label("Gift Multiplier:"), 1, 4)
        self.gift_mult_spin = NoWheelDoubleSpinBox()
        self.gift_mult_spin.setRange(1.0, 10.0)
        self.gift_mult_spin.setValue(2.0)
        self.gift_mult_spin.setSingleStep(0.1)
        self.gift_mult_spin.setMinimumHeight(40)
        self.gift_mult_spin.setSuffix(" x")
        grid.addWidget(self.gift_mult_spin, 1, 5)

        grid.addWidget(self._label("Gift Max:"), 0, 6)
        self.gift_max_spin = NoWheelSpinBox()
        self.gift_max_spin.setRange(1, 10_000_000)
        self.gift_max_spin.setValue(100_000)
        self.gift_max_spin.setMinimumHeight(40)
        self.gift_max_spin.setGroupSeparatorShown(True)
        grid.addWidget(self.gift_max_spin, 0, 7)
        grid.setColumnStretch(8, 1)

        l.addLayout(grid)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px;")
        l.addWidget(sep2)

        # Preview
        l.addWidget(self._label("📊  PREVIEW — 15 LEVELS"))
        self.boss_preview = QTextEdit()
        self.boss_preview.setReadOnly(True)
        self.boss_preview.setMinimumHeight(280)
        self.boss_preview.setStyleSheet(f"""
            QTextEdit {{
                background: #0a0a0f;
                color: {COLORS['success']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 10px;
                padding: 12px 16px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        l.addWidget(self.boss_preview)

        # Apply button
        btn_apply = QPushButton("💾   APPLY & RESET BOSS")
        btn_apply.setStyleSheet(btn_style("primary", "lg"))
        btn_apply.setMinimumHeight(50)
        btn_apply.clicked.connect(self._apply_boss_config)
        l.addWidget(btn_apply)

        # Init preview
        for spin in [self.hp_base_spin, self.hp_mult_spin,
                     self.robux_base_spin, self.robux_mult_spin,
                     self.gift_base_spin, self.gift_mult_spin,
                     self.gift_max_spin]:
            spin.valueChanged.connect(self._update_boss_preview)
        self._update_boss_preview()

        return section
    
    def _build_section_live_urls(self):
        """Section: Live URLs — bỏ VTuber."""
        section = self._make_section("📡  LIVE URLS")
        l = section.layout()

        # Danh sách overlay (không có vtuber)
        overlays = [
            ("🏆  BẢNG ĐẤU GIÁ",   "widget"),
            ("💬  FAKE COMMENT",   "cmt"),
            ("🎆  FAKE GIFT FX",   "gift_fx"),
            ("📝  FAKE GIFT TEXT", "gift_text"),
            ("👹  BOSS + POT",     "boss"),
            ("💬  GIFT CHAT",      "gift_chat"),
        ]

        self.link_widgets = {}

        for label_text, key in overlays:
            row = QHBoxLayout()
            row.setSpacing(8)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px; font-weight: 700; min-width: 180px;")
            row.addWidget(lbl)

            inp = QLineEdit()
            inp.setReadOnly(True)
            inp.setMinimumHeight(36)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background: {COLORS['bg']};
                    color: {COLORS['primary_hi']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-family: 'Consolas', monospace;
                    font-size: 11px;
                }}
            """)
            row.addWidget(inp, 1)

            btn = QPushButton("📋")
            btn.setStyleSheet(btn_style("primary", "sm"))
            btn.setFixedWidth(44)
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked=False, i=inp, b=btn: self._copy_text(i.text(), b))
            row.addWidget(btn)

            l.addLayout(row)
            self.link_widgets[key] = {"local": inp, "lan": inp, "btn": btn}

        return section
        
    def _make_section(self, title):
        """Tạo QGroupBox section với style chuẩn."""
        section = QGroupBox(title)
        section.setStyleSheet(f"""
            QGroupBox {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 14px;
                padding-top: 12px;
                font-weight: 800;
                font-size: 14px;
                color: {COLORS['primary_hi']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background: {COLORS['bg']};
                border-radius: 6px;
            }}
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 24, 18, 18)
        layout.setSpacing(12)
        return section

    def _fake_gift_launch(self):
        """★ Gửi fake gift."""
        pseudo = self.fake_pseudo_input.text().strip()
        if not pseudo:
            QMessageBox.warning(self, "Thiếu pseudo", "Nhập pseudo trước.")
            return
        if not pseudo.startswith("@"):
            pseudo = "@" + pseudo

        anim_data = self.fake_anim_combo.currentData()
        if not anim_data:
            return
        pts, effect, name, icon, folder = anim_data
        repeat = self.fake_repeat_spin.value()
        total = pts * repeat

        self.worker.engine.add_score(
            pseudo, total,
            source=f"{name} x{repeat}",
            display_name=pseudo.lstrip("@"),
        )

        if self.worker.bot_manager.gift_effects_enabled:
            self.worker.server.send_event_sync("gift_event", {
                "user": pseudo,
                "display_name": pseudo.lstrip("@"),
                "avatar": "",
                "points": total,
                "gift_name": name,
                "gift_icon": icon,
                "gift_points": pts,
                "gift_count": repeat,
                "effect": effect,
                "folder": folder,
                "is_bot": False,
            })

        self._append_log(f"🎁 Fake gift: {pseudo} +{total} ({name} × {repeat})")

    def _fake_gift_stop(self):
        """★ Dừng fake gift."""
        self._append_log("⏹ Đã dừng fake gift")
        
    def _on_auto_fake_gift_toggled(self, checked):
        """★ Bật/tắt auto fake gift cho CẢ engine + bot."""
        # 1. Bật cho engine (xử lý user thật + manual)
        self.worker.engine.set_auto_fake_gift(checked)
        
        # 2. Bật cho bot manager (xử lý bot)
        self.worker.bot_manager.set_auto_fake_gift(checked)
        
        # 3. Log
        self._append_log(f"🎯 Auto Fake Gift: {'BẬT' if checked else 'TẮT'}")

    def _on_auto_fake_gift_toggled(self, checked):
        """★ Bật/tắt auto fake gift."""
        self._append_log(f"Auto Fake Gift: {'BẬT' if checked else 'TẮT'}")
        
    def _build_section_fake_gift(self):
        """Section: Cộng điểm thủ công + Auto Fake Gift + Auto Tie."""
        section = self._make_section("🎁  FAKE USER GIFT")
        l = section.layout()

        # ═══════════════════════════════════════════════════
        # PHẦN 1: CỘNG ĐIỂM THỦ CÔNG
        # ═══════════════════════════════════════════════════
        manual_box = QGroupBox("➕  THÊM ĐIỂM THỦ CÔNG")
        manual_box.setStyleSheet(f"""
            QGroupBox {{
                background: rgba(124, 92, 255, 0.05);
                border: 1px solid rgba(124, 92, 255, 0.3);
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: 800;
                font-size: 12px;
                color: {COLORS['primary_hi']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                background: {COLORS['bg']};
                border-radius: 6px;
            }}
        """)
        m_l = QVBoxLayout(manual_box)
        m_l.setContentsMargins(14, 20, 14, 14)
        m_l.setSpacing(10)

        # ═══ ROW 1: NGƯỜI CHƠI ═══
        m_row1 = QHBoxLayout()
        m_row1.setSpacing(10)

        lbl_user = self._label("Người chơi:")
        lbl_user.setFixedWidth(90)
        m_row1.addWidget(lbl_user)

        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(42)
        self.user_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border_hi']};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
        """)
        m_row1.addWidget(self.user_combo, 1)

        btn_refresh_users = QPushButton("🔄")
        btn_refresh_users.setStyleSheet(btn_style("default", "md"))
        btn_refresh_users.setFixedWidth(50)
        btn_refresh_users.setMinimumHeight(42)
        btn_refresh_users.setToolTip("Tải lại danh sách")
        btn_refresh_users.clicked.connect(self._refresh_user_combo)
        m_row1.addWidget(btn_refresh_users)
        m_l.addLayout(m_row1)

        # ═══ ROW 2: QUÀ + SỐ LƯỢNG + ĐIỂM ═══
        m_row2 = QHBoxLayout()
        m_row2.setSpacing(12)

        # Quà tặng
        lbl_gift = self._label("Quà tặng:")
        lbl_gift.setFixedWidth(90)
        m_row2.addWidget(lbl_gift)

        # ★ Gift picker button thay vì combobox
            # ★ Gift picker button
        self.gift_combo = QComboBox()   # Ẩn — giữ để tương thích code cũ
        self.gift_combo.setVisible(False)
        self.gift_combo.currentIndexChanged.connect(self._on_gift_changed)

        self.gift_picker_btn = QPushButton("🎁  Chọn Gift")
        self.gift_picker_btn.setStyleSheet(btn_style("primary", "md"))
        self.gift_picker_btn.setMinimumHeight(42)
        self.gift_picker_btn.setMinimumWidth(180)
        self.gift_picker_btn.clicked.connect(self._open_gift_picker)
        m_row2.addWidget(self.gift_picker_btn, 1)

        self.selected_gift_label = QLabel("(chưa chọn gift)")
        self.selected_gift_label.setStyleSheet(f"""
            color: {COLORS['gold']};
            font-size: 13px;
            font-weight: 700;
            padding: 8px 14px;
            background: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        """)
        self.selected_gift_label.setMinimumHeight(42)
        m_row2.addWidget(self.selected_gift_label, 1)

        # Số lượng
        m_row2.addSpacing(10)
        m_row2.addWidget(self._label("Số lượng:"))
        self.gift_count_spin = NoWheelSpinBox()
        self.gift_count_spin.setRange(1, 99_999)
        self.gift_count_spin.setValue(1)
        self.gift_count_spin.setFixedWidth(90)
        self.gift_count_spin.setMinimumHeight(42)
        self.gift_count_spin.setSuffix(" x")
        self.gift_count_spin.valueChanged.connect(self._on_gift_count_changed)
        m_row2.addWidget(self.gift_count_spin)

        # Điểm
        m_row2.addSpacing(10)
        m_row2.addWidget(self._label("Điểm:"))
        self.pts_input = NoWheelSpinBox()
        self.pts_input.setRange(1, 100_000_000)
        self.pts_input.setValue(1)
        self.pts_input.setFixedWidth(130)
        self.pts_input.setMinimumHeight(42)
        self.pts_input.setGroupSeparatorShown(True)
        self.pts_input.setStyleSheet(f"""
            QSpinBox {{
                background: {COLORS['bg']};
                color: {COLORS['gold']};
                border: 2px solid {COLORS['warning']};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 800;
            }}
        """)
        m_row2.addWidget(self.pts_input)
        m_l.addLayout(m_row2)

        # ═══ ROW 3: PREVIEW ═══
        self.manual_preview = QLabel("📊 Rose × 1 = 1 điểm")
        self.manual_preview.setStyleSheet(f"""
            color: {COLORS['success']};
            font-size: 12px;
            font-weight: 800;
            padding: 8px 14px;
            background: rgba(0, 214, 143, 0.08);
            border: 1px solid rgba(0, 214, 143, 0.3);
            border-radius: 8px;
        """)
        self.manual_preview.setMinimumHeight(38)
        self.manual_preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        m_l.addWidget(self.manual_preview)

        # ═══ ROW 4: NÚT THÊM ĐIỂM ═══
        btn_add_score = QPushButton("＋   THÊM ĐIỂM")
        btn_add_score.setStyleSheet(btn_style("primary", "lg"))
        btn_add_score.setMinimumHeight(46)
        btn_add_score.clicked.connect(self.add_manual_score)
        m_l.addWidget(btn_add_score)

        l.addWidget(manual_box)

        # ★ Init preview
        self._update_manual_preview()

        return section
        
    def _build_col_control(self):
        """Cột 3: Điều khiển."""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        box.setMinimumHeight(520)   # ★ Cố định chiều cao
        box.setMaximumHeight(600)   # ★
        l = QVBoxLayout(box)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(10)

        # Header
        header = QLabel("🎮  ĐIỀU KHIỂN")
        header.setStyleSheet(f"""
            font-size: 13px; font-weight: 900;
            color: {COLORS['primary_hi']};
            letter-spacing: 2px;
            padding: 10px;
            background: rgba(124, 92, 255, 0.08);
            border: 1px solid rgba(124, 92, 255, 0.3);
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignCenter)
        l.addWidget(header)

        # ─── CẤU HÌNH ───
        cfg_row = QHBoxLayout()
        cfg_row.setSpacing(6)

        # Main duration
        main_box = QVBoxLayout()
        main_box.setSpacing(2)
        lbl1 = QLabel("Thời gian (giây):")
        lbl1.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 700;")
        main_box.addWidget(lbl1)
        self.main_spin = NoWheelSpinBox()
        self.main_spin.setRange(10, 7200)
        self.main_spin.setValue(60)
        self.main_spin.setMinimumHeight(36)
        main_box.addWidget(self.main_spin)
        cfg_row.addLayout(main_box, 1)

        # Snap duration
        snap_box = QVBoxLayout()
        snap_box.setSpacing(2)
        lbl2 = QLabel("Snap time:")
        lbl2.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 700;")
        snap_box.addWidget(lbl2)
        self.snap_spin = NoWheelSpinBox()
        self.snap_spin.setRange(5, 600)
        self.snap_spin.setValue(30)
        self.snap_spin.setMinimumHeight(36)
        snap_box.addWidget(self.snap_spin)
        cfg_row.addLayout(snap_box, 1)

        # Min coins
        min_box = QVBoxLayout()
        min_box.setSpacing(2)
        lbl3 = QLabel("Min coins:")
        lbl3.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 700;")
        min_box.addWidget(lbl3)
        self.min_coins_spin = NoWheelSpinBox()
        self.min_coins_spin.setRange(0, 10_000_000)
        self.min_coins_spin.setValue(10)
        self.min_coins_spin.setMinimumHeight(36)
        self.min_coins_spin.valueChanged.connect(self._on_min_coins_changed)
        min_box.addWidget(self.min_coins_spin)
        cfg_row.addLayout(min_box, 1)

        l.addLayout(cfg_row)

        # ─── BUTTONS ───
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(8)

        self.btn_start = QPushButton("▶  BẮT ĐẦU")
        self.btn_start.setStyleSheet(btn_style("success", "lg"))
        self.btn_start.setMinimumHeight(44)
        self.btn_start.clicked.connect(self.start_auction)
        btn_row1.addWidget(self.btn_start, 1)

        self.btn_stop = QPushButton("⏸  DỪNG")
        self.btn_stop.setStyleSheet(btn_style("danger", "lg"))
        self.btn_stop.setMinimumHeight(44)
        self.btn_stop.clicked.connect(self.stop_auction)
        btn_row1.addWidget(self.btn_stop, 1)

        l.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(8)

        self.btn_reset = QPushButton("🔄  ĐẶT LẠI")
        self.btn_reset.setStyleSheet(btn_style("default", "md"))
        self.btn_reset.setMinimumHeight(40)
        self.btn_reset.clicked.connect(self.reset_auction)
        btn_row2.addWidget(self.btn_reset, 1)

        self.btn_snap = QPushButton("⚡  SNAP")
        self.btn_snap.setStyleSheet(btn_style("warning", "md"))
        self.btn_snap.setMinimumHeight(40)
        self.btn_snap.clicked.connect(self.start_snap_manual)
        btn_row2.addWidget(self.btn_snap, 1)

        l.addLayout(btn_row2)

        # ─── TIMER ───
        timer_box = QFrame()
        timer_box.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg']};
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
            }}
        """)
        timer_box.setMinimumHeight(110)
        timer_l = QVBoxLayout(timer_box)
        timer_l.setContentsMargins(14, 10, 14, 10)
        timer_l.setSpacing(4)

        self.phase_label = QLabel("CHƯA BẮT ĐẦU")
        self.phase_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 800;
            color: {COLORS['text_muted']};
            letter-spacing: 2px;
            background: transparent; border: none;
        """)
        self.phase_label.setAlignment(Qt.AlignCenter)
        timer_l.addWidget(self.phase_label)

        self.timer_label = QLabel("--:--")
        self.timer_label.setStyleSheet(f"""
            font-size: 44px; font-weight: 900;
            color: {COLORS['primary_hi']};
            font-family: 'Consolas', monospace;
            background: transparent; border: none;
        """)
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_l.addWidget(self.timer_label)

        l.addWidget(timer_box)

        # ─── BOSS INFO ───
        boss_box = QFrame()
        boss_box.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 61, 90, 0.08);
                border: 1px solid rgba(255, 61, 90, 0.3);
                border-radius: 10px;
            }}
        """)
        boss_box.setMinimumHeight(90)
        boss_l = QVBoxLayout(boss_box)
        boss_l.setContentsMargins(14, 10, 14, 10)
        boss_l.setSpacing(4)

        self.boss_display_label = QLabel("👹  Boss Lv.1 SLIME")
        self.boss_display_label.setStyleSheet(f"""
            color: {COLORS['danger']};
            font-size: 13px;
            font-weight: 900;
            background: transparent; border: none;
        """)
        boss_l.addWidget(self.boss_display_label)

        self.boss_hp_display = QLabel("HP: 500 / 500")
        self.boss_hp_display.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            font-size: 11px;
            font-weight: 700;
            background: transparent; border: none;
        """)
        boss_l.addWidget(self.boss_hp_display)

        self.pot_display_label = QLabel("💰  Robux Pot: 500")
        self.pot_display_label.setStyleSheet(f"""
            color: {COLORS['gold']};
            font-size: 13px;
            font-weight: 900;
            background: transparent; border: none;
        """)
        boss_l.addWidget(self.pot_display_label)

        l.addWidget(boss_box)

        # ─── WINNER ───
        self.winner_label = QLabel("")
        self.winner_label.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {COLORS['gold']}, stop:1 {COLORS['warning']});
            color: #1a1a1a;
            padding: 14px;
            font-size: 15px;
            font-weight: 900;
            border-radius: 10px;
            letter-spacing: 1px;
        """)
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.hide()
        l.addWidget(self.winner_label)

        # ═══ LINK VOUCHES + BOSS & POT (mở tab) ═══
        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)

        btn_goto_boss = QPushButton("👹  Boss & Pot")
        btn_goto_boss.setStyleSheet(btn_style("warning", "md"))
        btn_goto_boss.setMinimumHeight(38)
        btn_goto_boss.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        nav_row.addWidget(btn_goto_boss, 1)

        btn_goto_log = QPushButton("📜  Nhật ký")
        btn_goto_log.setStyleSheet(btn_style("default", "md"))
        btn_goto_log.setMinimumHeight(38)
        btn_goto_log.clicked.connect(lambda: self.tabs.setCurrentIndex(4))
        nav_row.addWidget(btn_goto_log, 1)

        l.addLayout(nav_row)

        l.addStretch()

        return box

    # ---------- Tab 1: Điều khiển ----------
    # ---------- Tab 2: Kết nối Live ----------

        # ---------- Tab: Theme ----------
        # ---------- Tab: Theme ----------

  #  def _on_theme_selected(self, item):
  #      """Click theme → load preview trong web view."""
  #      theme_name = item.data(Qt.UserRole)
  #      if not theme_name:
  #          return

  #      url = (
  #          f"http://localhost:{self.worker.server.port}/widget.html"
  #          f"?theme={theme_name}&preview=1"
  #      )
  #      self.preview_url.setText(url)

  #      if HAS_WEBENGINE and hasattr(self, 'preview_view'):
  #          from PySide6.QtCore import QUrl
  #          self.preview_view.load(QUrl(url))
  #          self._append_log(f"🎨 Preview: {theme_name}")

    def _reload_themes(self):
        """Đọc folder themes."""
        self.theme_list.clear()

        themes_dir = Path(__file__).parent / "themes"
        if not themes_dir.exists():
            self.theme_list.addItem("❌ Không tìm thấy folder themes/")
            return

        theme_icons = {
            "halloween": "🎃", "christmas": "🎄", "tet": "🧧",
            "valentine": "💝", "gaming": "🎮", "neon": "🌃",
            "cherry": "🌸", "dragon": "🐉", "ocean": "🌊",
            "forest": "🌲", "sunset": "🌅", "night": "🌙",
            "galaxy": "🌌", "fire": "🔥", "ice": "❄️",
            "gold": "👑", "blood": "🩸", "matrix": "💚",
            "retro": "📼", "rainbow": "🌈",
        }

        for theme_dir in sorted(themes_dir.iterdir()):
            if not theme_dir.is_dir():
                continue
            config_file = theme_dir / "config.json"
            if not config_file.exists():
                continue

            try:
                config = _json.loads(config_file.read_text(encoding="utf-8"))
                icon = theme_icons.get(theme_dir.name, "🎨")
                title = config.get("title", theme_dir.name)
                item = QListWidgetItem(f"{icon}   {title}")
                item.setData(Qt.UserRole, theme_dir.name)
                self.theme_list.addItem(item)
            except Exception as e:
                print(f"❌ Lỗi theme {theme_dir.name}: {e}")

        self._append_log(f"🎨 Đã load {self.theme_list.count()} theme")

    def _apply_selected_theme(self):
        """Áp dụng theme đang chọn — KHÔNG tự mở browser."""
        item = self.theme_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "Chưa chọn theme",
                "Chọn 1 theme trong danh sách trước."
            )
            return

        theme_name = item.data(Qt.UserRole)
        if not theme_name:
            return

        # Gửi event tới overlay TikTok Studio
        self.worker.server.send_event_sync("theme_change", {
            "theme": theme_name,
        })

        # Cập nhật preview trong app (web view)
        if HAS_WEBENGINE and hasattr(self, 'preview_view'):
            from PySide6.QtCore import QUrl
            import time as _t
            url = (
                f"http://localhost:{self.worker.server.port}/widget.html"
                f"?theme={theme_name}&preview=1&t={int(_t.time())}"
            )
            self.preview_view.load(QUrl(url))
            self.preview_url.setText(url.split('&t=')[0])

        self._append_log(f"🎨 Đã đổi theme → {theme_name}")
        self.statusBar().showMessage(
            f"🎨 Đã áp dụng theme: {theme_name}", 3000
        )
        # ★ KHÔNG mở browser nữa — bỏ hộp thoại QMessageBox.question
        
    def _on_auto_tie_toggled(self, checked):
        """★ Bật/tắt Auto Tie."""
        self.worker.engine.set_auto_tie(enabled=checked)
        self._append_log(f"Auto Tie: {'BẬT' if checked else 'TẮT'}")

    def _on_auto_tie_user_changed(self, idx):
        """★ Đổi user Auto Tie."""
        user = self.auto_tie_combo.currentData()
        if user:
            self.worker.engine.set_auto_tie(user=user)

    def _on_auto_tie_amount_changed(self, value):
        """★ Đổi số điểm cộng."""
        self.worker.engine.set_auto_tie(amount=value)

    def _on_auto_tie_delay_changed(self, value):
        """★ Đổi delay."""
        self.worker.engine.set_auto_tie(delay=value)
    
    def _on_auto_next_toggled(self, checked):
        self.worker.engine.set_auto_next_boss(
            checked,
            self.auto_next_delay_spin.value()
        )
        self._append_log(f"Auto next boss: {checked}")

    def _on_auto_next_delay_changed(self, value):
        self.worker.engine.set_auto_next_boss(
            self.auto_next_chk.isChecked(),
            value
        )
    def _on_theme_selected(self, item):
        """Khi click theme → hiện preview TRỰC QUAN."""
        theme_name = item.data(Qt.UserRole)
        if not theme_name:
            return

        theme_dir = Path(__file__).parent / "themes" / theme_name
        config_file = theme_dir / "config.json"

        if not config_file.exists():
            return

        try:
            config = _json.loads(config_file.read_text(encoding="utf-8"))

            # ★ Xóa widget cũ
            layout = self.theme_preview_frame.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # ★ Tạo preview trực quan bằng QLabel với stylesheet từ theme
            preview_html = f"""
            <div style="
                padding: 20px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-radius: 16px;
                font-family: 'Segoe UI', sans-serif;
            ">
                <div style="text-align:center; font-size:22px; font-weight:900;
                            color:#ffd700; margin-bottom:16px;
                            letter-spacing:3px;">
                    {config.get('logo', '🏆')} {config.get('title', 'AUCTION')}
                </div>

                <div style="display:flex; gap:12px; margin-bottom:16px;">
                    <div style="
                        flex:1; padding:14px; border-radius:12px;
                        background:rgba(255,200,0,0.3);
                        border:2px solid #ffcc00;
                        color:#fff; font-weight:900;
                    ">
                        🥇 Hary<br>
                        <span style="color:#ffcc00; font-size:18px;">115 pts</span>
                    </div>
                    <div style="
                        flex:1; padding:14px; border-radius:12px;
                        background:rgba(200,200,220,0.3);
                        border:2px solid #c0c0c0;
                        color:#fff; font-weight:900;
                    ">
                        🥈 あ<br>
                        <span style="color:#00ff88; font-size:18px;">101 pts</span>
                    </div>
                </div>

                <div style="
                    padding:12px; border-radius:10px;
                    background:rgba(255,50,0,0.4);
                    text-align:center; color:#fff;
                    font-weight:900; letter-spacing:3px;
                ">
                    ⚡ SNAP TIME #1 — 30s
                </div>
            </div>
            """

            preview_label = QLabel()
            preview_label.setTextFormat(Qt.RichText)
            preview_label.setText(preview_html)
            preview_label.setWordWrap(True)
            preview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(preview_label)

            self.theme_preview_label = preview_label

            self._append_log(f"🎨 Preview: {config.get('title', theme_name)}")

        except Exception as e:
            self._append_log(f"❌ Preview error: {e}")

    def _open_theme_preview(self):
        """Mở browser preview theme hiện tại."""
        item = self.theme_list.currentItem()
        theme_name = "halloween"
        if item:
            theme_name = item.data(Qt.UserRole) or "halloween"

        # URL overlay với theme được chọn
        url = f"http://localhost:{self.worker.server.port}/widget.html?theme={theme_name}"
        import webbrowser
        webbrowser.open(url)
        self._append_log(f"🌐 Preview browser: {url}")

    def _reload_themes(self):
        """Đọc folder themes và load vào list."""
        self.theme_list.clear()

        themes_dir = Path(__file__).parent / "themes"
        if not themes_dir.exists():
            self.theme_list.addItem("❌ Không tìm thấy folder themes/")
            return

        theme_icons = {
            "halloween": "🎃", "christmas": "🎄", "tet": "🧧",
            "valentine": "💝", "gaming": "🎮", "neon": "🌃",
            "cherry": "🌸", "dragon": "🐉", "ocean": "🌊",
            "forest": "🌲", "sunset": "🌅", "night": "🌙",
            "galaxy": "🌌", "fire": "🔥", "ice": "❄️",
            "gold": "👑", "blood": "🩸", "matrix": "💚",
            "retro": "📼", "rainbow": "🌈",
        }

        for theme_dir in sorted(themes_dir.iterdir()):
            if not theme_dir.is_dir():
                continue
            config_file = theme_dir / "config.json"
            if not config_file.exists():
                continue

            try:
                config = _json.loads(config_file.read_text(encoding="utf-8"))
                icon = theme_icons.get(theme_dir.name, "🎨")
                title = config.get("title", theme_dir.name)
                item = QListWidgetItem(f"{icon}   {title}")
                item.setData(Qt.UserRole, theme_dir.name)
                self.theme_list.addItem(item)
            except Exception as e:
                print(f"❌ Lỗi load theme {theme_dir.name}: {e}")

        self._append_log(f"🎨 Đã load {self.theme_list.count()} theme")

    def _on_theme_selected(self, item):
        """Click theme → load preview trong web view."""
        theme_name = item.data(Qt.UserRole)
        if not theme_name:
            return

        url = (
            f"http://localhost:{self.worker.server.port}/widget.html"
            f"?theme={theme_name}&preview=1"
        )
        self.preview_url.setText(url)

        if HAS_WEBENGINE and hasattr(self, 'preview_view'):
            from PySide6.QtCore import QUrl
            self.preview_view.load(QUrl(url))
            self._append_log(f"🎨 Preview: {theme_name}")

    def _apply_selected_theme(self):
        """Áp dụng theme đang chọn."""
        item = self.theme_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "Chưa chọn theme",
                "Chọn 1 theme trong danh sách trước."
            )
            return

        theme_name = item.data(Qt.UserRole)
        if not theme_name:
            return

        # Gửi event tới overlay
        self.worker.server.send_event_sync("theme_change", {
            "theme": theme_name,
        })

        self._append_log(f"🎨 Đã đổi theme → {theme_name}")
        self.statusBar().showMessage(
            f"🎨 Đã áp dụng theme: {theme_name}", 3000
        )

        # ★ Mở preview trong browser nếu chưa có
        reply = QMessageBox.question(
            self, "Áp dụng theme",
            f"Đã áp dụng theme: <b>{theme_name}</b><br><br>"
            f"Để xem overlay có theme mới, đảm bảo:<br>"
            f"• Overlay đang mở (browser hoặc TikTok Studio)<br>"
            f"• Tab browser đã reload (Ctrl+Shift+R)<br><br>"
            f"Mở preview trong browser để kiểm tra?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self._open_theme_preview()
    
    # ---------- Tab 6: Hướng dẫn ----------
    # ---------- Helpers ----------
    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px;"
        )
        return lbl

    def _update_overlay_links(self):
        srv = self.worker.server
        local_urls = srv.build_all_local()
        lan_urls = srv.build_all_lan()
  
        for key in ["widget", "cmt", "gift_fx", "gift_text", "vtuber", "boss", "gift_chat"]:
            if key not in self.link_widgets:
                continue
            local_inp = self.link_widgets[key]["local"]
            lan_inp = self.link_widgets[key]["lan"]

            if key in local_urls:
                local_inp.setText(local_urls[key])
                local_inp.setToolTip(local_urls[key])
                local_inp.setCursorPosition(0)

            if key in lan_urls:
                lan_inp.setText(lan_urls[key])
                lan_inp.setToolTip(lan_urls[key])
                lan_inp.setCursorPosition(0)

       # self.device_label.setText(srv.device_id)

    def _update_start_button(self):
        self.btn_start.setEnabled(True)
        if self.tiktok_connected:
            self.btn_start.setToolTip("Bắt đầu đấu giá")
        else:
            self.btn_start.setToolTip(
                "Bắt đầu ở chế độ TEST (chưa kết nối TikTok)"
            )

    def _copy_text(self, text, button):
        if not text:
            return
        QApplication.clipboard().setText(text)
        original = button.text()
        button.setText("✅  ĐÃ COPY")
        QTimer.singleShot(1500, lambda: button.setText(original))
        self._append_log(f"📋 Đã copy: {text[:80]}...")
        self.statusBar().showMessage("✅ Đã copy", 3000)


    def _refresh_user_combo(self):
        if not hasattr(self, "user_combo"):
            return
        current = self.user_combo.currentData()
        self.user_combo.clear()

        engine_users = sorted(
            self.worker.engine.scores.keys(),
            key=lambda u: -self.worker.engine.scores[u]
        )
        bot_users = []
        for bot in self.worker.bot_manager.bots:
            if bot.user not in engine_users:
                bot_users.append(bot.user)
        all_users = engine_users + bot_users

        if not all_users:
            self.user_combo.addItem("(chưa có ai)", "")
        else:
            for u in all_users:
                score = self.worker.engine.scores.get(u, 0)
                bot = self.worker.bot_manager.get_by_user(u)
                if bot and bot.is_chaser:
                    prefix = "🎯 CHASE  "
                elif bot:
                    prefix = "🤖 BOT  "
                else:
                    prefix = "👤 "
                self.user_combo.addItem(f"{prefix}{u}  —  {score} điểm", u)

            if current:
                for i in range(self.user_combo.count()):
                    if self.user_combo.itemData(i) == current:
                        self.user_combo.setCurrentIndex(i)
                        break

        # ★ Cập nhật auto_tie_combo
        if hasattr(self, "auto_tie_combo"):
            current_tie = self.auto_tie_combo.currentData()
            self.auto_tie_combo.blockSignals(True)
            self.auto_tie_combo.clear()
            self.auto_tie_combo.addItem("-- Chọn user Auto Tie --", "")
            for u in all_users:
                score = self.worker.engine.scores.get(u, 0)
                bot = self.worker.bot_manager.get_by_user(u)
                prefix = "🤖 " if bot else "👤 "
                self.auto_tie_combo.addItem(f"{prefix}{u} — {score}", u)
            # Restore selection
            if current_tie:
                for i in range(self.auto_tie_combo.count()):
                    if self.auto_tie_combo.itemData(i) == current_tie:
                        self.auto_tie_combo.setCurrentIndex(i)
                        break
            self.auto_tie_combo.blockSignals(False)
                    
    def _on_gift_delay_changed(self, value):
        """★ Cập nhật delay dedup gift."""
        self.worker.tiktok.set_dedup_delay(value)
        self._append_log(f"⏱ Gift delay = {value}s")

    def _on_gift_changed(self, idx):
        data = self.gift_combo.itemData(idx)
        if data:
            pts, effect, name, icon, folder = data
            # ★ Nhân với số lượng hiện tại
            count = self.gift_count_spin.value() if hasattr(self, "gift_count_spin") else 1
            self.pts_input.blockSignals(True)
            self.pts_input.setValue(int(pts) * count)
            self.pts_input.blockSignals(False)
        self._update_manual_preview()
        
    def _open_gift_picker(self):
        """★ Mở dialog chọn gift theo tab giá."""
        from gift_picker import GiftPickerDialog

        dlg = GiftPickerDialog(self)
        if dlg.exec():
            gift = dlg.selected_gift
            if gift:
                name, icon, points, effect, folder = gift
                self._current_gift = gift

                # Update label
                self.selected_gift_label.setText(
                    f"{name}  ({points:,} coins)"
                )

                # Update gift_combo ẩn (để tương thích add_manual_score)
                self.gift_combo.blockSignals(True)
                self.gift_combo.clear()
                self.gift_combo.addItem(
                    f"{name} ({points} điểm)",
                    (points, effect, name, icon, folder)
                )
                self.gift_combo.setCurrentIndex(0)
                self.gift_combo.blockSignals(False)

                if hasattr(self, "_on_gift_changed"):
                    self._on_gift_changed(0)

                self._append_log(f"🎁 Đã chọn: {name} ({points:,} coins)")
        
    def _on_gift_count_changed(self, value):
        """★ Cập nhật điểm khi đổi số lượng = điểm_quà × số_lượng."""
        data = self.gift_combo.currentData()
        if data:
            pts_per_gift, effect, name, icon, folder = data
            total = pts_per_gift * value
            self.pts_input.blockSignals(True)
            self.pts_input.setValue(total)
            self.pts_input.blockSignals(False)
        self._update_manual_preview()

    def _update_manual_preview(self):
        """★ Cập nhật dòng preview: tổng điểm."""
        if not hasattr(self, "gift_combo") or not hasattr(self, "manual_preview"):
            return
        data = self.gift_combo.currentData()
        count = self.gift_count_spin.value() if hasattr(self, "gift_count_spin") else 1
        if data:
            pts_per_gift, effect, name, icon, folder = data
            total = pts_per_gift * count
            self.manual_preview.setText(
                f"📊 {icon} {name} × {count} = {total:,} điểm"
            )
        else:
            self.manual_preview.setText("")

    # ---------- Actions ----------
    def start_snap_manual(self):
        """★ Bắt đầu SNAP thủ công."""
        eng = self.worker.engine
        if eng.phase == Phase.IDLE:
            QMessageBox.warning(
                self, "Chưa bắt đầu",
                "Bạn cần bấm BẮT ĐẦU trước khi vào SNAP."
            )
            return
        if eng.phase == Phase.FINISHED:
            QMessageBox.warning(
                self, "Ván đã kết thúc",
                "Ván đã kết thúc. Bấm ĐẶT LẠI để bắt đầu ván mới."
            )
            return

        eng.start_snap_manual()
        self._append_log("⚡ SNAP thủ công")
    def start_snap_manual(self):
        """★ Bắt đầu SNAP thủ công."""
        eng = self.worker.engine
        if eng.phase == Phase.IDLE:
            QMessageBox.warning(
                self, "Chưa bắt đầu",
                "Bạn cần bấm BẮT ĐẦU trước khi vào SNAP."
            )
            return
        if eng.phase == Phase.FINISHED:
            QMessageBox.warning(
                self, "Ván đã kết thúc",
                "Ván đã kết thúc. Bấm ĐẶT LẠI để bắt đầu ván mới."
            )
            return

        eng.start_snap_manual()
        self._append_log("⚡ SNAP thủ công")
    def start_auction(self):
        if not self.tiktok_connected:
            reply = QMessageBox.question(
                self, "Chưa kết nối TikTok",
                "Bạn chưa kết nối với TikTok Live.\n\n"
                "Vẫn BẮT ĐẦU để TEST tool?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply != QMessageBox.Yes:
                self.tabs.setCurrentIndex(1)
                return
            self._append_log("🧪 Bắt đầu ở CHẾ ĐỘ TEST")

        eng = self.worker.engine
        eng.main_duration = self.main_spin.value()
        eng.snap_duration = self.snap_spin.value()
        eng.min_coins = self.min_coins_spin.value()
        eng.start()

        # ★ Tăng vouch mỗi lần bắt đầu ván mới
        eng.increment_vouch()
        # ★ Update VOUCHES topbar (nếu có)
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText(str(eng.vouch))

        self.winner_label.hide()
        self._refresh_user_combo()
        self._append_log(
            f"▶ Phiên bắt đầu: {eng.main_duration}s chính, "
            f"{eng.snap_duration}s snap, min_coins={eng.min_coins}, "
            f"vouch={eng.vouch}"
        )

    def stop_auction(self):
        eng = self.worker.engine
        winner = eng.winner
        eng.stop()
        if winner:
            self.worker.bot_manager.notify_winner(winner)
        self._append_log("⏹ Đã dừng phiên")

    def reset_auction(self):
        self.worker.engine.reset()
        self.winner_label.hide()
        self._refresh_user_combo()
        self._append_log("🔄 Đã đặt lại")

    def balance_top(self):
        """★ Tự động cân bằng top 2 — không hỏi, random gift 1 coin."""
        eng = self.worker.engine
        sorted_users = sorted(eng.scores.items(), key=lambda x: -x[1])[:2]

        if len(sorted_users) < 2:
            eng.balance_top2()
            self._refresh_user_combo()
            self._append_log("⚖ Đã cân bằng top 2 (tạo bot @alice/@bob)")
            return

        u1, s1 = sorted_users[0]
        u2, s2 = sorted_users[1]
        diff = s1 - s2

        if diff == 0:
            self._append_log(f"⚖ {u1} và {u2} đã bằng điểm ({s1})")
            return

        # ★ Random gift 1 coin từ danh sách
        import random
        one_coin_gifts = [
            (1, "text", "Rose",   "🌹", "rose"),
            (1, "text", "TikTok", "🎵", "tiktok"),
            (1, "text", "GG",     "🎮", "gg"),
        ]
        # Nếu có gift 1 coin trong gift_data, dùng luôn
        for g in gift_data.GIFTS:
            if g[2] == 1:
                one_coin_gifts.append(g)

        # Loại trùng
        seen = set()
        unique_gifts = []
        for g in one_coin_gifts:
            if g[2] not in seen:
                seen.add(g[2])
                unique_gifts.append(g)

        pts_g, effect, name, icon, folder = random.choice(unique_gifts)
        rose_count = diff  # 1 coin mỗi gift → cần `diff` gift

        # ★ Cân bằng ngay
        eng.balance_top2()
        self._refresh_user_combo()
        self._append_log(
            f"⚖ Cân bằng: {u2} +{diff:,} điểm "
            f"({icon} {name} × {rose_count:,}) → {s1:,}"
        )

        # ★ Gửi gift_event hiện hiệu ứng
        if self.worker.bot_manager.gift_effects_enabled:
            display_name = eng.display_names.get(u2, u2.lstrip("@"))
            avatar = eng.avatars.get(u2, "")

            # Bot avatar nếu là bot
            bot = self.worker.bot_manager.get_by_user(u2)
            if bot:
                avatar = self.worker.bot_manager.get_avatar_url(bot)
                display_name = bot.display_name

            self.worker.server.send_event_sync("gift_event", {
                "user": u2,
                "display_name": display_name,
                "avatar": avatar,
                "points": diff,
                "gift_name": name,
                "gift_icon": icon,
                "gift_points": pts_g,
                "gift_count": rose_count,
                "effect": effect,
                "folder": folder,
                "is_bot": False,
                "is_real": False,
            })

            # ★ Auto fake gift (nếu bật)
            fake = eng.pick_fake_gift_by_points(diff)
            if fake:
                fake_payload = {
                    "user": u2,
                    "display_name": display_name,
                    "avatar": avatar,
                    "points": diff,
                    "gift_name": fake["name"],
                    "gift_icon": fake["icon"],
                    "gift_points": diff,
                    "gift_count": 1,
                    "effect": "text",
                    "folder": fake["folder"],
                    "is_bot": False,
                    "is_real": False,
                }
                self.worker.server.send_event_sync("gift_event", fake_payload)
    
    def _on_min_coins_changed(self, value):
        """★ Cập nhật min_coins vào engine."""
        self.worker.engine.set_min_coins(value)
        self._append_log(f"💰 Min coins = {value}")

    def _on_vouch_changed(self, value):
        self.worker.engine.set_vouch(value)
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText(str(value))
        self._append_log(f"🎮 Vouch = {value}")

    def _reset_vouch(self):
        self.worker.engine.reset_vouch()
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText("0")
        self._append_log("🎮 Đã reset vouch = 0")

    def add_manual_score(self):
        user = self.user_combo.currentData()
        if not user:
            self._append_log("❌ Chưa chọn người chơi")
            return

        count = self.gift_count_spin.value()
        gift_cur = self.gift_combo.currentData()

        if gift_cur:
            pts_g, effect, name, icon, folder = gift_cur
            pts = pts_g * count
        else:
            effect, name, icon, folder = "text", "Rose", "🌹", "rose"
            pts_g = 1
            pts = self.pts_input.value()

        display_name = self.worker.engine.display_names.get(user, user.lstrip("@"))
        avatar = self.worker.engine.avatars.get(user, "")

        bot = self.worker.bot_manager.get_by_user(user)
        if bot:
            avatar = self.worker.bot_manager.get_avatar_url(bot)
            display_name = bot.display_name

        self.worker.engine.add_score(user, pts, source=f"{name} x{count}",
                                     avatar=avatar, display_name=display_name)

        if self.worker.bot_manager.gift_effects_enabled:
            payload = {
                "user": user,
                "display_name": display_name,
                "avatar": avatar,
                "points": pts,
                "gift_name": name,
                "gift_icon": icon,
                "gift_points": pts_g,
                "gift_count": count,
                "effect": effect,
                "folder": folder,
                "is_bot": False,
                "is_real": False,
            }
            self.worker.server.send_event_sync("gift_event", payload)

            # ★ AUTO FAKE GIFT
            fake = self.worker.engine.pick_fake_gift_by_points(pts)
            if fake:
                fake_payload = dict(payload)
                fake_payload["gift_name"] = fake["name"]
                fake_payload["gift_icon"] = fake["icon"]
                fake_payload["folder"] = fake["folder"]
                fake_payload["gift_points"] = pts
                fake_payload["gift_count"] = 1
                self.worker.server.send_event_sync("gift_event", fake_payload)
                self._append_log(f"🎁 Auto fake: {fake['name']}")

        # Roblox comment
        if self.worker.bot_manager.roblox_cmt_enabled:
            roblox_user = ""
            if bot and bot.roblox_username:
                roblox_user = bot.roblox_username
            else:
                from bot_manager import make_roblox_username
                roblox_user = make_roblox_username(display_name)

            self.worker.server.send_event_sync("roblox_comment", {
                "user": user,
                "display_name": display_name,
                "roblox_username": roblox_user,
                "delay": self.worker.bot_manager.roblox_cmt_delay,
            })

        self._append_log(f"🎁 {user} +{pts} ({name} × {count})")

    # ---------- Kết nối TikTok ----------
    def connect_tiktok(self):
        """Bắt đầu kết nối TikTok Live."""
        raw = self.live_input.text().strip()
        if not raw:
            QMessageBox.warning(
                self, "Thiếu thông tin",
                "Nhập username hoặc link TikTok Live"
            )
            return

        # Disable nút Connect, enable Disconnect
        if hasattr(self, "btn_connect"):
            self.btn_connect.setEnabled(False)
        if hasattr(self, "btn_disconnect"):
            self.btn_disconnect.setEnabled(True)
            self.btn_disconnect.setText("⏹   DỪNG CHỜ")

        # Submit connect
        self.worker.submit(self.worker.tiktok.connect(raw, retry=True))

        # Cập nhật conn_indicator
        if hasattr(self, "conn_indicator"):
            self.conn_indicator.setText(f"🟣 Đang chờ {raw} live")
            self.conn_indicator.setStyleSheet(f"""
                background: rgba(124, 92, 255, 0.15);
                color: {COLORS['primary_hi']};
                padding: 8px 16px;
                border-radius: 18px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid {COLORS['primary']};
            """)

        # Cập nhật conn_status_text
        if hasattr(self, "conn_status_text"):
            self.conn_status_text.setText(f"⏳ Đang chờ {raw} lên live...")
            self.conn_status_text.setStyleSheet(f"""
                color: {COLORS['primary_hi']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                border: none;
                padding: 0 8px;
            """)

        # Log
        self._append_log(f"🔗 Bắt đầu kết nối: {raw}")

    def disconnect_tiktok(self):
        """Ngắt kết nối TikTok Live."""
        self.worker.tiktok.stop_waiting()
        self.worker.submit(self.worker.tiktok.disconnect())

        self.tiktok_connected = False
        self.tiktok_username = ""

        # Reset nút
        if hasattr(self, "btn_connect"):
            self.btn_connect.setEnabled(True)
        if hasattr(self, "btn_disconnect"):
            self.btn_disconnect.setEnabled(False)
            self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

        # Reset conn_indicator
        if hasattr(self, "conn_indicator"):
            self.conn_indicator.setText("⚪ Chưa kết nối TikTok")
            self.conn_indicator.setStyleSheet(f"""
                background: {COLORS['bg']};
                color: {COLORS['text_dim']};
                padding: 8px 16px;
                border-radius: 18px;
                font-size: 12px;
                font-weight: 600;
                border: 1px solid {COLORS['border']};
            """)

        # Reset conn_status_text
        if hasattr(self, "conn_status_text"):
            self.conn_status_text.setText("")
            self.conn_status_text.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0 8px;
            """)

        # Update nút BẮT ĐẦU
        if hasattr(self, "_update_start_button"):
            self._update_start_button()

        self._append_log("⛔ Đã ngắt kết nối TikTok Live")

    # ---------- Bot actions ----------
    def _add_bots(self):
        n = self.bot_count_spin.value()
        added = self.worker.bot_manager.add_bots(n)
        self._refresh_bot_list()
        self._refresh_user_combo()
        self._append_log(f"🤖 Đã thêm {added} bot")

    def _clear_bots(self):
        if not self.worker.bot_manager.bots:
            return
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Xóa tất cả {len(self.worker.bot_manager.bots)} bot?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.worker.bot_manager.clear_bots()
            self._refresh_bot_list()
            self._refresh_user_combo()

    def _apply_bot_config(self):
        bm = self.worker.bot_manager
        bm.configure(
            interval_min=self.bot_int_min.value(),
            interval_max=self.bot_int_max.value(),
            points_min=self.bot_pts_min.value(),
            points_max=self.bot_pts_max.value(),
            max_score=self.bot_max_score.value(),
        )
        self._append_log("⚙ Đã áp dụng cấu hình bot")

    def _start_bots(self):
        if not self.worker.bot_manager.bots:
            QMessageBox.warning(self, "Chưa có bot", "Hãy thêm bot trước.")
            return
        reply = QMessageBox.warning(
            self, "⚠️ Xác nhận bật bot",
            "Bot CHỈ dùng để TEST TOOL.\n\n"
            "KHÔNG dùng khi live thật.\n\n"
            "Tiếp tục?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        self._apply_bot_config()
        self.worker.bot_manager.start(self.worker.loop)
        self.btn_bot_start.setEnabled(False)
        self.btn_bot_stop.setEnabled(True)
        self.bot_status.setText(
            f"🟢  BOT ĐANG CHẠY — "
            f"{len(self.worker.bot_manager.bots)} bot"
        )
        self.bot_status.setStyleSheet(f"""
            padding: 12px 16px;
            background: rgba(0, 214, 143, 0.1);
            color: {COLORS['success']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid {COLORS['success']};
        """)

    def _stop_bots(self):
        self.worker.bot_manager.stop()
        self.btn_bot_start.setEnabled(True)
        self.btn_bot_stop.setEnabled(False)
        self.bot_status.setText("🤖  Bot đã tắt")
        self.bot_status.setStyleSheet(f"""
            padding: 12px 16px;
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)

    def _refresh_bot_list(self):
        self.bot_list.clear()
        bots = self.worker.bot_manager.bots
        if not bots:
            item = QListWidgetItem("(chưa có bot nào)")
            item.setForeground(QColor(COLORS["text_muted"]))
            self.bot_list.addItem(item)
            return

        for i, bot in enumerate(bots, 1):
            avatar_txt = "🖼" if bot.avatar_path else "👤"
            status = "🟢" if bot.active else "⚪"
            if bot.is_chaser:
                tag = f"🎯 [CHASE #{i:02d}]"
                color = QColor("#ff6b35")
            else:
                tag = f"🤖 [BOT #{i:02d}]"
                color = QColor(COLORS["warning"])

            txt = (
                f"{tag}  {status} {avatar_txt}  "
                f"{bot.display_name}   ({bot.user})   —   "
                f"{bot.score} điểm"
            )
            if bot.roblox_username:
                txt += f"   🎮 {bot.roblox_username}"

            item = QListWidgetItem(txt)
            item.setForeground(color)
            self.bot_list.addItem(item)

    def _open_folder(self, folder: Path):
        import subprocess
        folder.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không mở được: {e}")

    def _open_bots_folder(self):
        base = Path(__file__).parent
        self._open_folder(base / "assets" / "bots")

    def _open_gifts_folder(self):
        base = Path(__file__).parent
        self._open_folder(base / "assets" / "gifts")

    def _apply_chase_config(self):
        bm = self.worker.bot_manager
        bm.configure_chase(
            count=self.chase_count_spin.value(),
            gap_min=self.chase_gap_min.value(),
            gap_max=self.chase_gap_max.value(),
            interval=self.chase_interval.value(),
        )
        self._append_log("🎯 Đã áp dụng cấu hình rượt đuổi")

    def _create_chasers(self):
        bm = self.worker.bot_manager
        bm.configure_chase(
            count=self.chase_count_spin.value(),
            gap_min=self.chase_gap_min.value(),
            gap_max=self.chase_gap_max.value(),
            interval=self.chase_interval.value(),
        )
        bm.chase_enabled = True
        for _ in range(bm.chase_count):
            bm.add_bot(is_chaser=True)
        self._refresh_bot_list()
        self._refresh_user_combo()
        self._append_log(f"🎯 Đã tạo {bm.chase_count} bot rượt")

    def _toggle_roblox_cmt(self, checked):
        self.worker.bot_manager.roblox_cmt_enabled = checked
        self._append_log(
            f"💬 Comment Roblox: {'BẬT' if checked else 'TẮT'}"
        )

    def _apply_cmt_config(self):
        bm = self.worker.bot_manager
        bm.roblox_cmt_enabled = self.cmt_enabled_chk.isChecked()
        bm.roblox_cmt_delay = self.cmt_delay.value()
        self._append_log("💬 Đã áp dụng cấu hình comment")

    def _toggle_gift_fx(self, checked):
        self.worker.bot_manager.gift_effects_enabled = checked
        self._append_log(
            f"🎆 Hiệu ứng quà: {'BẬT' if checked else 'TẮT'}"
        )

    def _test_roblox_cmt(self):
        bm = self.worker.bot_manager
        leaders = self.worker.engine.get_leaders()
        if not leaders:
            QMessageBox.information(
                self, "Chưa có ai",
                "Chưa có người chơi. Thêm bot trước."
            )
            return
        top_user = leaders[0]
        bot = bm.get_by_user(top_user)
        if not bot:
            QMessageBox.information(
                self, "Top 1 không phải bot",
                f"Top 1 hiện tại là {top_user} — không phải bot."
            )
            return
        if not bot.roblox_username:
            from bot_manager import make_roblox_username
            bot.roblox_username = make_roblox_username(bot.display_name)
        bm._emit_roblox_comment(bot)
        self._append_log(f"🧪 Test cmt Roblox cho {bot.display_name}")

    # ---------- VTuber ----------
    def _vtuber_say(self):
        """Giả lập nhân vật nói (dùng volume 80%)."""
        self.worker.server.send_event_sync("vtuber_volume", {
            "volume": 80,
        })
        self._append_log("🎭 Nhân vật đang nói")

    # ---------- Voice methods ----------
    def _on_voice_volume(self, volume):
        self.worker.server.send_event_sync("vtuber_volume", {
            "volume": round(volume, 1),
        })

        if hasattr(self, 'volume_bar'):
            pct = min(100, volume)
            color = "#00d68f" if volume < 12 else \
                    "#ffaa00" if volume < 50 else "#ff3d5a"
            self.volume_bar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:{pct/100} {color},
                    stop:{min(1, pct/100 + 0.01)} {COLORS['bg']},
                    stop:1 {COLORS['bg']});
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            """)
            self.volume_label.setText(f"{int(volume)}%")

    def _on_voice_status(self, status):
        """Chỉ ghi log, không có UI."""
        self._append_log(f"[mic] {status}")

    # ---------- Tick ----------
    def _tick(self):
        eng = self.worker.engine
        if eng.phase not in (Phase.IDLE, Phase.FINISHED):
            eng.tick()
        self._render_state(eng.snapshot())

        hist = eng.history
        if hist:
            text = "\n".join(
                f"[{time.strftime('%H:%M:%S', time.localtime(h['t']))}] "
                f"{h['msg']}"
                for h in hist[-300:]
            )
            sb = self.log_view.verticalScrollBar()
            at_bottom = sb.value() >= sb.maximum() - 10
            self.log_view.setPlainText(text)
            if at_bottom:
                sb.setValue(sb.maximum())
        if not hasattr(self, "_tick_count"):
            self._tick_count = 0
        self._tick_count += 1
        if self._tick_count % 8 == 0:
            if hasattr(self, "user_combo"):
                self._refresh_user_combo()
            if hasattr(self, "bot_list"):
                self._refresh_bot_list()

    # ---------- Render ----------
    def _render_state(self, d):
        phase = d["phase"]
                # ★ Sync vouch spinbox nếu thay đổi từ engine
                # Sync boss level
        if hasattr(self, "boss_level_spin"):
            lv = d.get("boss", {}).get("level", 1)
            if self.boss_level_spin.value() != lv:
                self.boss_level_spin.blockSignals(True)
                self.boss_level_spin.setValue(lv)
                self.boss_level_spin.blockSignals(False)

        # Sync vouch display
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText(str(d.get("vouch", 0)))

        # Sync pot
        if hasattr(self, "pot_current_label"):
            pot = d.get("robux_pot", 0)
            self.pot_current_label.setText(f"Current: {pot:,}")
        phase_text = {
            "idle": "CHƯA BẮT ĐẦU",
            "main": "ĐANG ĐẤU GIÁ",
            "snap": f"SNAP TIME #{d['snap_count']}",
            "finished": "ĐÃ KẾT THÚC",
        }
        phase_colors = {
            "idle": (COLORS["bg"], COLORS["text_dim"], COLORS["border"]),
            "main": ("rgba(0,214,143,0.15)", COLORS["success"],
                     COLORS["success"]),
            "snap": ("rgba(255,61,90,0.2)", COLORS["danger"],
                     COLORS["danger"]),
            "finished": (COLORS["gold"], "#1a1a1a", COLORS["gold"]),
        }
        bg, fg, border = phase_colors[phase]
        self.phase_label.setText(phase_text[phase])
        self.phase_label.setStyleSheet(f"""
            background: {bg};
            color: {fg};
            padding: 10px 22px;
            border-radius: 10px;
            font-weight: 800;
            font-size: 16px;
            letter-spacing: 1px;
            border: 1px solid {border};
        """)

        if phase == "idle":
            self.timer_label.setText("--:--")
            color = COLORS['text_muted']
        elif phase == "finished":
            self.timer_label.setText("00:00")
            color = COLORS['gold']
        else:
            rem = int(d["remaining"])
            m, s = divmod(max(0, rem), 60)
            self.timer_label.setText(f"{m:02d}:{s:02d}")
            color = (COLORS["danger"] if phase == "snap"
                     else COLORS["success"])

        self.timer_label.setStyleSheet(f"""
            font-size: 56px; font-weight: 900;
            color: {color};
            background: transparent; border: none;
            font-family: 'Consolas', monospace;
        """)

        self.ranking_list.clear()
        leaders = set(d["leaders"])
        for i, row in enumerate(d["top"]):
            rank = i + 1
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{rank}"
            bot = self.worker.bot_manager.get_by_user(row["user"])
            if bot and bot.is_chaser:
                tag = "  [🎯 CHASE]"
            elif bot:
                tag = "  [🤖 BOT]"
            else:
                tag = ""
            txt = (
                f"{medal}   {row['user']}{tag}          "
                f"{row['score']} điểm"
            )
            item = QListWidgetItem(txt)

            font = item.font()
            font.setPointSize(11)
            if rank == 1:
                font.setBold(True)
                font.setPointSize(12)
                item.setForeground(QColor(COLORS["gold"]))
            elif rank == 2:
                item.setForeground(QColor(COLORS["silver"]))
            elif rank == 3:
                item.setForeground(QColor(COLORS["bronze"]))
            elif bot:
                item.setForeground(QColor(COLORS["warning"]))

            if row["user"] in leaders and phase not in ("idle", "finished"):
                font.setBold(True)
                item.setBackground(QColor(COLORS["card_hover"]))
            item.setFont(font)
            self.ranking_list.addItem(item)
        if phase == "finished" and d["winner"]:
            self.winner_label.setText(f"🏆  NGƯỜI THẮNG:  {d['winner']}")
            self.winner_label.show()
        else:
            self.winner_label.hide()

        # ═══════════════════════════════════════════════════
        # ★ BƯỚC 7 — UPDATE TOPBAR + 3 CỘT
        # ═══════════════════════════════════════════════════

        # Cập nhật VOUCHES topbar
        if hasattr(self, "vouch_display"):
            self.vouch_display.setText(str(d.get("vouch", 0)))

        # Cập nhật boss display
        if hasattr(self, "boss_display_label") and "boss" in d:
            b = d["boss"]
            self.boss_display_label.setText(
                f"{b['emoji']}  Boss Lv.{b['level']} {b['name']}"
            )
            self.boss_hp_display.setText(
                f"HP: {b['hp']:,} / {b['max_hp']:,}"
            )
            self.pot_display_label.setText(
                f"💰  Robux Pot: {d.get('robux_pot', 0):,}"
            )

        # Cập nhật tổng số người
        if hasattr(self, "players_count_label"):
            self.players_count_label.setText(
                f"Tổng tham gia: {len(self.worker.engine.scores)}"
            )
            total = sum(self.worker.engine.scores.values())
            self.points_count_label.setText(f"Tổng kim cương: {total:,}")

    # ---------- Signals ----------
    def _append_log(self, msg):
        self.log_view.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _set_status(self, text):
        """Cập nhật trạng thái kết nối TikTok Live."""
        # Bảng dịch
        translations = {
            "Connected:": "Đã kết nối:",
            "Waiting for": "Đang chờ",
            "Connecting to": "Đang kết nối tới",
            "Disconnected": "Đã ngắt kết nối",
            "Stopped waiting": "Đã dừng chờ",
            "Connection error:": "Lỗi kết nối:",
            "is not live": "chưa lên live",
            "to go live": "lên live",
            "TikTok Live disconnected": "TikTok Live đã ngắt kết nối",
            "TikTokLive not installed": "Chưa cài TikTokLive",
            "Empty username/link": "Username/link trống",
        }
        translated = text
        for en, vi in translations.items():
            translated = translated.replace(en, vi)

        # ═══════════════════════════════════════════════════
        # Cập nhật conn_indicator + conn_status_text
        # ═══════════════════════════════════════════════════

        if text.startswith("✅"):
            # ─── ĐÃ KẾT NỐI ───
            self.tiktok_connected = True
            self.tiktok_username = self.live_input.text().strip()

            if hasattr(self, "conn_indicator"):
                self.conn_indicator.setText(f"🟢 Đã kết nối: {self.tiktok_username}")
                self.conn_indicator.setStyleSheet(f"""
                    background: rgba(0, 214, 143, 0.15);
                    color: {COLORS['success']};
                    padding: 8px 16px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 700;
                    border: 1px solid {COLORS['success']};
                """)

            if hasattr(self, "conn_status_text"):
                self.conn_status_text.setText("✅ Đã kết nối TikTok Live")
                self.conn_status_text.setStyleSheet(f"""
                    color: {COLORS['success']};
                    font-size: 11px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                    padding: 0 8px;
                """)

            if hasattr(self, "btn_connect"):
                self.btn_connect.setEnabled(False)
            if hasattr(self, "btn_disconnect"):
                self.btn_disconnect.setEnabled(True)
                self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

            QTimer.singleShot(800, lambda: self._show_connect_success(self.tiktok_username))

        elif text.startswith("⏳") or "waiting" in text.lower():
            # ─── ĐANG CHỜ LIVE ───
            if hasattr(self, "conn_indicator"):
                self.conn_indicator.setText("🟣 Đang chờ live")
                self.conn_indicator.setStyleSheet(f"""
                    background: rgba(124, 92, 255, 0.15);
                    color: {COLORS['primary_hi']};
                    padding: 8px 16px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 700;
                    border: 1px solid {COLORS['primary']};
                """)

            if hasattr(self, "conn_status_text"):
                self.conn_status_text.setText("⏳ Đang chờ user lên live...")
                self.conn_status_text.setStyleSheet(f"""
                    color: {COLORS['primary_hi']};
                    font-size: 11px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                    padding: 0 8px;
                """)

        elif text.startswith("⏹"):
            # ─── ĐÃ DỪNG CHỜ ───
            self.tiktok_connected = False
            if hasattr(self, "btn_connect"):
                self.btn_connect.setEnabled(True)
            if hasattr(self, "btn_disconnect"):
                self.btn_disconnect.setEnabled(False)
                self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

            if hasattr(self, "conn_indicator"):
                self.conn_indicator.setText("⚪ Chưa kết nối TikTok")
                self.conn_indicator.setStyleSheet(f"""
                    background: {COLORS['bg']};
                    color: {COLORS['text_dim']};
                    padding: 8px 16px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 600;
                    border: 1px solid {COLORS['border']};
                """)

            if hasattr(self, "conn_status_text"):
                self.conn_status_text.setText("")
                self.conn_status_text.setStyleSheet(f"""
                    color: {COLORS['text_muted']};
                    font-size: 11px;
                    font-weight: 600;
                    background: transparent;
                    border: none;
                    padding: 0 8px;
                """)

        elif text.startswith("⚠️") or text.startswith("❌"):
            # ─── LỖI KẾT NỐI ───
            self.tiktok_connected = False

            if hasattr(self, "conn_indicator"):
                self.conn_indicator.setText("🔴 Lỗi kết nối")
                self.conn_indicator.setStyleSheet(f"""
                    background: rgba(255, 61, 90, 0.15);
                    color: {COLORS['danger']};
                    padding: 8px 16px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 700;
                    border: 1px solid {COLORS['danger']};
                """)

            if hasattr(self, "conn_status_text"):
                self.conn_status_text.setText("❌ Lỗi kết nối")
                self.conn_status_text.setStyleSheet(f"""
                    color: {COLORS['danger']};
                    font-size: 11px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                    padding: 0 8px;
                """)

            if hasattr(self, "btn_connect"):
                self.btn_connect.setEnabled(True)
            if hasattr(self, "btn_disconnect"):
                self.btn_disconnect.setEnabled(False)
                self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

        elif text.startswith("⛔"):
            # ─── ĐÃ NGẮT ───
            self.tiktok_connected = False
            if hasattr(self, "conn_indicator"):
                self.conn_indicator.setText("⚪ Chưa kết nối TikTok")
                self.conn_indicator.setStyleSheet(f"""
                    background: {COLORS['bg']};
                    color: {COLORS['text_dim']};
                    padding: 8px 16px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 600;
                    border: 1px solid {COLORS['border']};
                """)
            if hasattr(self, "conn_status_text"):
                self.conn_status_text.setText("")

        # Cập nhật trạng thái nút BẮT ĐẦU
        if hasattr(self, "_update_start_button"):
            self._update_start_button()

        # Hiện trên status bar
        self.statusBar().showMessage(translated, 5000)
    
    def _show_connect_success(self, username):
        """★ Thông báo kết nối thành công."""
        msg = QMessageBox(self)
        msg.setWindowTitle("✅ Đã kết nối TikTok Live")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"<b>✅ ĐÃ KẾT NỐI TIKTOK LIVE</b>")
        msg.setInformativeText(
            f"Tài khoản: <b>{username}</b><br><br>"
            f"Bây giờ bạn có thể:<br>"
            f"• Bấm <b>▶ BẮT ĐẦU</b> để bắt đầu ván đấu giá<br>"
            f"• Copy link overlay vào <b>TikTok Studio</b><br>"
            f"• Người xem tặng quà → tự động cộng điểm"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QMessageBox QPushButton {{
                background: {COLORS['success']};
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 700;
                font-size: 13px;
                min-width: 100px;
            }}
            QMessageBox QPushButton:hover {{
                background: #00e6a0;
            }}
        """)
        msg.exec()
        
    def _check_live_connection(self):
        """★ Kiểm tra kết nối TikTok Live khi mới mở tool."""
        if self.tiktok_connected:
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Chưa kết nối TikTok Live")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "<b>⚠️ BẠN CHƯA KẾT NỐI TIKTOK LIVE</b>"
        )
        msg.setInformativeText(
            "Tool sẽ <b>không nhận được quà</b> từ người xem nếu chưa kết nối.\n\n"
            "👉 Vào tab <b>📡 Kết nối Live</b> để nhập:\n"
            "   • <code>@username</code> TikTok của bạn\n"
            "   • Hoặc link live: <code>https://tiktok.com/@user/live</code>\n\n"
            "💡 Bạn vẫn có thể bấm <b>▶ BẮT ĐẦU</b> để chạy ở chế độ TEST."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QMessageBox QPushButton {{
                background: {COLORS['primary']};
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 700;
                font-size: 13px;
                min-width: 100px;
            }}
            QMessageBox QPushButton:hover {{
                background: {COLORS['primary_hi']};
            }}
        """)

        # Nút "MỞ TAB KẾT NỐI"
        btn_open_live = msg.addButton("📡  Mở tab Kết nối Live", QMessageBox.ActionRole)
        btn_open_live.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']};
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 700;
                font-size: 13px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: #00e6a0;
            }}
        """)

        msg.exec()

        # Nếu bấm "Mở tab Kết nối Live"
        if msg.clickedButton() == btn_open_live:
            self.tabs.setCurrentIndex(1)   # Tab thứ 2 (index 1)

    def closeEvent(self, event):
        try:
            if self.voice_listener:
                self.voice_listener.stop()
        except Exception:
            pass
        try:
            self.worker.bot_manager.stop()
        except Exception:
            pass
        try:
            self.worker.stop()
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(main_stylesheet())

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()