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
from PySide6.QtGui import QFont, QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QGroupBox, QListWidget, QListWidgetItem, QTextEdit, QMessageBox,
    QTabWidget, QFrame, QComboBox, QCheckBox, QScrollArea
)

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
        self.engine = AuctionEngine()
        static_dir = resource_path(".")

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

    def _on_gift(self, user, points):
        """Người thật tặng quà qua TikTok Live."""
        self.engine.add_score(user, points)
        self.log_signal.emit(f"🎁 {user} +{points}")

        # ★ Gửi event tới overlay (gift-text + gift-fx)
        # Đoán loại quà từ số điểm
        gift = gift_data.gift_from_points(points)
        name, icon, gift_pts, effect, folder = gift

        payload = {
            "user": user,
            "display_name": user.lstrip("@"),
            "points": points,
            "gift_name": name,
            "gift_icon": icon,
            "gift_points": gift_pts,
            "gift_count": max(1, points // gift_pts) if gift_pts > 0 else 1,
            "effect": effect,
            "folder": folder,
            "is_bot": False,
        }

        print(f"📤 Emit gift_event: {payload}")   # ← Debug
        self.server.send_event_sync("gift_event", payload)

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

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Topbar
        topbar = QFrame()
        topbar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['card']},
                    stop:1 {COLORS['bg_alt']});
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        topbar.setFixedHeight(72)
        t_l = QHBoxLayout(topbar)
        t_l.setContentsMargins(20, 12, 20, 12)

        logo = QLabel("🎁")
        logo.setStyleSheet(
            "font-size: 32px; background: transparent; border: none;"
        )

        brand_box = QVBoxLayout()
        brand_box.setSpacing(2)
        title = QLabel("TIKTOK AUCTION TOOL")
        title.setStyleSheet(f"""
            font-size: 16px; font-weight: 900;
            color: {COLORS['primary_hi']};
            letter-spacing: 2px;
            background: transparent; border: none;
        """)
        subtitle = QLabel("Đấu giá + Nhân vật AI nhép miệng theo mic")
        subtitle.setStyleSheet(f"""
            font-size: 11px; color: {COLORS['text_dim']};
            background: transparent; border: none;
        """)
        brand_box.addWidget(title)
        brand_box.addWidget(subtitle)

        t_l.addWidget(logo)
        t_l.addLayout(brand_box)
        t_l.addStretch()

        self.conn_indicator = QLabel("⚪ Chưa kết nối TikTok")
        self.conn_indicator.setStyleSheet(f"""
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        t_l.addWidget(self.conn_indicator)

        root.addWidget(topbar)

        # Tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        t1 = QWidget(); self.tabs.addTab(t1, "  🎛️   Điều khiển  ")
        self._build_tab_control(t1)

        t2 = QWidget(); self.tabs.addTab(t2, "  📡   Kết nối Live  ")
        self._build_tab_live(t2)

        t_bot = QWidget(); self.tabs.addTab(t_bot, "  🤖   Bot (Test)  ")
        self._build_tab_bot(t_bot)

        t3 = QWidget(); self.tabs.addTab(t3, "  📜   Nhật ký  ")
        self._build_tab_log(t3)
        
        t_theme = QWidget(); self.tabs.addTab(t_theme, "  🎨   Theme  ")
        self._build_tab_theme(t_theme)

        t4 = QWidget(); self.tabs.addTab(t4, "  ❓   Hướng dẫn  ")
        self._build_tab_help(t4)

    # ---------- Tab 1: Điều khiển ----------
    def _build_tab_control(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 12, 4, 4)
        layout.setSpacing(12)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {COLORS['card']},
                    stop:1 {COLORS['bg_alt']});
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        header.setFixedHeight(110)
        h_l = QHBoxLayout(header)
        h_l.setContentsMargins(24, 16, 24, 16)

        left = QVBoxLayout()
        left.setSpacing(6)
        pl = QLabel("TRẠNG THÁI PHIÊN")
        pl.setStyleSheet(f"""
            color: {COLORS['text_muted']}; font-size: 11px;
            font-weight: 700; letter-spacing: 2px;
            background: transparent; border: none;
        """)
        self.phase_label = QLabel("CHƯA BẮT ĐẦU")
        self.phase_label.setStyleSheet(f"""
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            padding: 10px 22px;
            border-radius: 10px;
            font-weight: 800;
            font-size: 16px;
            letter-spacing: 1px;
            border: 1px solid {COLORS['border']};
        """)
        left.addWidget(pl)
        left.addWidget(self.phase_label)
        left.addStretch()

        right = QVBoxLayout()
        right.setSpacing(4)
        tl = QLabel("THỜI GIAN CÒN LẠI")
        tl.setStyleSheet(f"""
            color: {COLORS['text_muted']}; font-size: 11px;
            font-weight: 700; letter-spacing: 2px;
            background: transparent; border: none;
        """)
        tl.setAlignment(Qt.AlignRight)
        self.timer_label = QLabel("--:--")
        self.timer_label.setStyleSheet(f"""
            font-size: 56px; font-weight: 900;
            color: {COLORS['text_muted']};
            background: transparent; border: none;
            font-family: 'Consolas', monospace;
        """)
        self.timer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.addWidget(tl)
        right.addWidget(self.timer_label)

        h_l.addLayout(left)
        h_l.addStretch()
        h_l.addLayout(right)
        layout.addWidget(header)

        cfg = QGroupBox("CẤU HÌNH PHIÊN")
        cl = QHBoxLayout(cfg)
        cl.setSpacing(16)

        cl.addWidget(self._label("Vòng chính (giây):"))
        self.main_spin = QSpinBox()
        self.main_spin.setRange(10, 7200)
        self.main_spin.setValue(60)
        self.main_spin.setFixedWidth(120)
        cl.addWidget(self.main_spin)

        cl.addWidget(self._label("Snap time (giây):"))
        self.snap_spin = QSpinBox()
        self.snap_spin.setRange(5, 600)
        self.snap_spin.setValue(30)
        self.snap_spin.setFixedWidth(120)
        cl.addWidget(self.snap_spin)

        hint = QLabel("(Snap lặp lại cho đến khi phá hòa)")
        hint.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 11px;"
        )
        cl.addWidget(hint)
        cl.addStretch()
        layout.addWidget(cfg)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        self.btn_start = QPushButton("▶   BẮT ĐẦU")
        self.btn_start.setStyleSheet(btn_style("success", "lg"))
        self.btn_start.setMinimumHeight(52)
        self.btn_start.clicked.connect(self.start_auction)

        self.btn_stop = QPushButton("⏹   DỪNG")
        self.btn_stop.setStyleSheet(btn_style("danger", "lg"))
        self.btn_stop.setMinimumHeight(52)
        self.btn_stop.clicked.connect(self.stop_auction)

        self.btn_reset = QPushButton("🔄   ĐẶT LẠI")
        self.btn_reset.setStyleSheet(btn_style("default", "lg"))
        self.btn_reset.setMinimumHeight(52)
        self.btn_reset.clicked.connect(self.reset_auction)

        self.btn_balance = QPushButton("⚖   CÂN BẰNG TOP 2")
        self.btn_balance.setStyleSheet(btn_style("warning", "lg"))
        self.btn_balance.setMinimumHeight(52)
        self.btn_balance.clicked.connect(self.balance_top)

        btns.addWidget(self.btn_start, 2)
        btns.addWidget(self.btn_stop, 1)
        btns.addWidget(self.btn_reset, 1)
        btns.addWidget(self.btn_balance, 1)
        layout.addLayout(btns)

        manual = QGroupBox("THÊM ĐIỂM THỦ CÔNG (TEST)")
        m_l = QVBoxLayout(manual)
        m_l.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        row1.addWidget(self._label("Người chơi:"))
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(240)
        self.user_combo.setMinimumHeight(38)
        row1.addWidget(self.user_combo)

        btn_refresh_users = QPushButton("🔄")
        btn_refresh_users.setStyleSheet(btn_style("default", "sm"))
        btn_refresh_users.setFixedWidth(44)
        btn_refresh_users.setMinimumHeight(38)
        btn_refresh_users.clicked.connect(self._refresh_user_combo)
        row1.addWidget(btn_refresh_users)

        row1.addSpacing(20)

        row1.addWidget(self._label("Quà tặng:"))
        self.gift_combo = QComboBox()
        self.gift_combo.setMinimumWidth(280)
        self.gift_combo.setMinimumHeight(38)
        for name, icon, pts, effect, folder in gift_data.GIFTS:
            prefix = "🎆 " if effect == "fx" else "📝 "
            self.gift_combo.addItem(
                f"{prefix}{icon}  {name}  ({pts} điểm)",
                (pts, effect, name, icon, folder)
            )
        self.gift_combo.currentIndexChanged.connect(self._on_gift_changed)
        row1.addWidget(self.gift_combo)

        row1.addWidget(self._label("Điểm:"))
        self.pts_input = QSpinBox()
        self.pts_input.setRange(1, 1_000_000)
        self.pts_input.setValue(1)
        self.pts_input.setFixedWidth(100)
        self.pts_input.setMinimumHeight(38)
        row1.addWidget(self.pts_input)

        row1.addStretch()
        m_l.addLayout(row1)

        row2 = QHBoxLayout()
        btn_add = QPushButton("＋   Thêm điểm")
        btn_add.setStyleSheet(btn_style("primary", "md"))
        btn_add.setMinimumHeight(40)
        btn_add.clicked.connect(self.add_manual_score)
        row2.addWidget(btn_add)
        row2.addStretch()
        m_l.addLayout(row2)

        layout.addWidget(manual)

        rank_box = QGroupBox("🏆   BẢNG XẾP HẠNG (TOP 3)")
        r_l = QVBoxLayout(rank_box)
        self.ranking_list = QListWidget()
        self.ranking_list.setMinimumHeight(220)
        r_l.addWidget(self.ranking_list)
        layout.addWidget(rank_box, 1)

        self.winner_label = QLabel("")
        self.winner_label.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {COLORS['gold']}, stop:1 {COLORS['warning']});
            color: #1a1a1a;
            padding: 20px;
            font-size: 22px;
            font-weight: 900;
            border-radius: 12px;
            letter-spacing: 1px;
        """)
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.hide()
        layout.addWidget(self.winner_label)
    # ---------- Tab 2: Kết nối Live ----------
    def _build_tab_live(self, parent):
        outer = QVBoxLayout(parent)
        outer.setContentsMargins(4, 12, 4, 4)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(16)

        step1 = QGroupBox("BƯỚC 1 — NHẬP ID TIKTOK CỦA BẠN")
        s1_l = QVBoxLayout(step1)
        s1_l.setSpacing(10)

        desc = QLabel(
            "Nhập <b>@username</b> hoặc <b>link TikTok Live</b>. "
            "Nếu người dùng chưa lên live, tool sẽ "
            "<b>tự động chờ và kết nối</b> khi họ bật live."
        )
        desc.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px;"
        )
        desc.setWordWrap(True)
        s1_l.addWidget(desc)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.live_input = QLineEdit()
        self.live_input.setPlaceholderText(
            "@username   hoặc   https://www.tiktok.com/@user/live"
        )
        self.live_input.setMinimumHeight(44)
        self.live_input.returnPressed.connect(self.connect_tiktok)

        self.btn_connect = QPushButton("🔗   KẾT NỐI")
        self.btn_connect.setStyleSheet(btn_style("primary", "md"))
        self.btn_connect.setMinimumHeight(44)
        self.btn_connect.setMinimumWidth(140)
        self.btn_connect.clicked.connect(self.connect_tiktok)

        self.btn_disconnect = QPushButton("⛔   NGẮT KẾT NỐI")
        self.btn_disconnect.setStyleSheet(btn_style("danger", "md"))
        self.btn_disconnect.setMinimumHeight(44)
        self.btn_disconnect.setMinimumWidth(160)
        self.btn_disconnect.clicked.connect(self.disconnect_tiktok)
        self.btn_disconnect.setEnabled(False)

        row.addWidget(self.live_input, 1)
        row.addWidget(self.btn_connect)
        row.addWidget(self.btn_disconnect)
        s1_l.addLayout(row)

        self.live_status = QLabel("⚪  Chưa kết nối")
        self.live_status.setStyleSheet(f"""
            padding: 14px 18px;
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        s1_l.addWidget(self.live_status)
        layout.addWidget(step1)

        step2 = QGroupBox("BƯỚC 2 — COPY 5 LINK OVERLAY VÀO TIKTOK STUDIO")
        s2_l = QVBoxLayout(step2)
        s2_l.setSpacing(12)

        warn = QLabel(
            "💡 <b>5 URL dưới đây là 5 khung riêng biệt trong TikTok Studio.</b><br>"
            "• <b>Bảng đấu giá</b> — bảng xếp hạng + timer<br>"
            "• <b>Fake Comment</b> — comment Roblox khi bot thắng<br>"
            "• <b>Fake Gift FX</b> — hiệu ứng quà lớn<br>"
            "• <b>Fake Gift Text</b> — dòng chữ quà nhỏ<br>"
            "• <b>Nhân vật AI (VTuber)</b> — nhép miệng theo mic<br>"
        )
        warn.setStyleSheet(f"""
            color: {COLORS['success']};
            background: rgba(0, 214, 143, 0.08);
            border: 1px solid rgba(0, 214, 143, 0.3);
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
        """)
        warn.setWordWrap(True)
        s2_l.addWidget(warn)

        self.link_widgets = {}

        link_configs = [
            ("widget",    "🏆  BẢNG ĐẤU GIÁ",         "primary", "primary"),
            ("cmt",       "💬  FAKE COMMENT ROBLOX",  "primary", "primary"),
            ("gift_fx",   "🎆  FAKE GIFT HIỆU ỨNG",   "danger",  "danger"),
            ("gift_text", "📝  FAKE GIFT TEXT",       "success", "success"),
            ("vtuber",    "🎭  NHÂN VẬT AI (VTUBER)", "primary", "primary"),
        ]

        for key, label_text, local_style, lan_style in link_configs:
            group = QVBoxLayout()
            group.setSpacing(6)

            header_row = QHBoxLayout()
            header_row.setSpacing(8)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"""
                color: {COLORS['text_dim']}; font-size: 11px;
                font-weight: 700; letter-spacing: 1px;
                margin-top: 8px;
            """)
            header_row.addWidget(lbl)
            header_row.addStretch()
            group.addLayout(header_row)

            local_row = QHBoxLayout()
            local_row.setSpacing(8)

            local_inp = QLineEdit()
            local_inp.setReadOnly(True)
            local_inp.setMinimumHeight(42)
            local_inp.setStyleSheet(f"""
                QLineEdit {{
                    background: {COLORS['bg']};
                    color: {COLORS[local_style] if local_style in COLORS else COLORS['primary_hi']};
                    border: 1px solid {COLORS[local_style] if local_style in COLORS else COLORS['primary']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Consolas', monospace;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)

            btn_copy_local = QPushButton("📋  COPY LOCAL")
            btn_copy_local.setStyleSheet(btn_style(local_style, "sm"))
            btn_copy_local.setMinimumHeight(42)
            btn_copy_local.setFixedWidth(150)
            btn_copy_local.clicked.connect(
                lambda checked=False, inp=local_inp, b=btn_copy_local:
                self._copy_text(inp.text(), b)
            )

            local_row.addWidget(local_inp, 1)
            local_row.addWidget(btn_copy_local)
            group.addLayout(local_row)

            lan_row = QHBoxLayout()
            lan_row.setSpacing(8)

            lan_inp = QLineEdit()
            lan_inp.setReadOnly(True)
            lan_inp.setMinimumHeight(42)
            lan_inp.setStyleSheet(f"""
                QLineEdit {{
                    background: {COLORS['bg']};
                    color: {COLORS['success']};
                    border: 1px solid {COLORS['success']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Consolas', monospace;
                    font-size: 11px;
                    font-weight: 700;
                }}
            """)

            btn_copy_lan = QPushButton("📋  COPY LAN")
            btn_copy_lan.setStyleSheet(btn_style("success", "sm"))
            btn_copy_lan.setMinimumHeight(42)
            btn_copy_lan.setFixedWidth(150)
            btn_copy_lan.clicked.connect(
                lambda checked=False, inp=lan_inp, b=btn_copy_lan:
                self._copy_text(inp.text(), b)
            )

            lan_row.addWidget(lan_inp, 1)
            lan_row.addWidget(btn_copy_lan)
            group.addLayout(lan_row)

            self.link_widgets[key] = {
                "local": local_inp,
                "lan": lan_inp,
            }

            s2_l.addLayout(group)

        dev_row = QHBoxLayout()
        dev_row.setSpacing(8)
        dev_label = QLabel("🔑  DEVICE ID:")
        dev_label.setStyleSheet(f"""
            color: {COLORS['text_muted']}; font-size: 11px;
            font-weight: 700; letter-spacing: 1px;
        """)
        self.device_label = QLabel("—")
        self.device_label.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            background: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 8px 12px;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            font-weight: 600;
        """)
        self.device_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        dev_row.addWidget(dev_label)
        dev_row.addWidget(self.device_label, 1)
        dev_row.addStretch()
        s2_l.addLayout(dev_row)

        layout.addWidget(step2)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ---------- Tab 3: Bot ----------
    def _build_tab_bot(self, parent):
        outer = QVBoxLayout(parent)
        outer.setContentsMargins(4, 12, 4, 4)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        warn = QLabel(
            "⚠️  <b>CHỈ DÙNG ĐỂ TEST TOOL</b> — TUYỆT ĐỐI KHÔNG dùng bot "
            "khi live thật.<br>Dùng bot để lừa người xem tặng quà là "
            "<b>hành vi gian lận</b> và vi phạm Điều khoản TikTok."
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
        layout.addWidget(warn)

        cfg = QGroupBox("CẤU HÌNH BOT")
        cfg_l = QVBoxLayout(cfg)
        cfg_l.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(self._label("Số lượng thêm:"))
        self.bot_count_spin = QSpinBox()
        self.bot_count_spin.setRange(1, 200)
        self.bot_count_spin.setValue(5)
        self.bot_count_spin.setFixedWidth(90)
        row1.addWidget(self.bot_count_spin)

        btn_add_bots = QPushButton("➕  Thêm bot")
        btn_add_bots.setStyleSheet(btn_style("primary", "md"))
        btn_add_bots.clicked.connect(self._add_bots)
        row1.addWidget(btn_add_bots)

        btn_clear_bots = QPushButton("🗑  Xóa hết")
        btn_clear_bots.setStyleSheet(btn_style("default", "md"))
        btn_clear_bots.clicked.connect(self._clear_bots)
        row1.addWidget(btn_clear_bots)
        row1.addStretch()
        cfg_l.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self._label("Tặng mỗi (giây):"))
        self.bot_int_min = QDoubleSpinBox()
        self.bot_int_min.setRange(0.5, 60)
        self.bot_int_min.setValue(3.0)
        self.bot_int_min.setSingleStep(0.5)
        self.bot_int_min.setFixedWidth(90)
        row2.addWidget(self.bot_int_min)

        row2.addWidget(QLabel("→"))
        self.bot_int_max = QDoubleSpinBox()
        self.bot_int_max.setRange(0.5, 120)
        self.bot_int_max.setValue(8.0)
        self.bot_int_max.setSingleStep(0.5)
        self.bot_int_max.setFixedWidth(90)
        row2.addWidget(self.bot_int_max)

        row2.addSpacing(20)
        row2.addWidget(self._label("Điểm mỗi lần:"))
        self.bot_pts_min = QSpinBox()
        self.bot_pts_min.setRange(1, 100000)
        self.bot_pts_min.setValue(5)
        self.bot_pts_min.setFixedWidth(90)
        row2.addWidget(self.bot_pts_min)

        row2.addWidget(QLabel("→"))
        self.bot_pts_max = QSpinBox()
        self.bot_pts_max.setRange(1, 100000)
        self.bot_pts_max.setValue(100)
        self.bot_pts_max.setFixedWidth(90)
        row2.addWidget(self.bot_pts_max)
        row2.addStretch()
        cfg_l.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(self._label("Điểm tối đa (0=không giới hạn):"))
        self.bot_max_score = QSpinBox()
        self.bot_max_score.setRange(0, 10_000_000)
        self.bot_max_score.setValue(0)
        self.bot_max_score.setFixedWidth(140)
        row3.addWidget(self.bot_max_score)

        btn_apply = QPushButton("💾  Áp dụng cấu hình")
        btn_apply.setStyleSheet(btn_style("default", "md"))
        btn_apply.clicked.connect(self._apply_bot_config)
        row3.addWidget(btn_apply)
        row3.addStretch()
        cfg_l.addLayout(row3)

        row4 = QHBoxLayout()
        self.btn_bot_start = QPushButton("▶   BẬT BOT")
        self.btn_bot_start.setStyleSheet(btn_style("warning", "lg"))
        self.btn_bot_start.setMinimumHeight(48)
        self.btn_bot_start.clicked.connect(self._start_bots)

        self.btn_bot_stop = QPushButton("⏹   TẮT BOT")
        self.btn_bot_stop.setStyleSheet(btn_style("danger", "lg"))
        self.btn_bot_stop.setMinimumHeight(48)
        self.btn_bot_stop.clicked.connect(self._stop_bots)
        self.btn_bot_stop.setEnabled(False)

        row4.addWidget(self.btn_bot_start, 1)
        row4.addWidget(self.btn_bot_stop, 1)
        cfg_l.addLayout(row4)

        layout.addWidget(cfg)

        chase_box = QGroupBox("🎯  CHẾ ĐỘ RƯỢT ĐUỔI (CHASE MODE)")
        chase_l = QVBoxLayout(chase_box)
        chase_l.setSpacing(10)

        chase_desc = QLabel(
            "2-3 bot sẽ <b>rượt đuổi top 1</b> — luôn vượt top 1 một "
            "khoảng điểm ngẫu nhiên."
        )
        chase_desc.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px;"
        )
        chase_desc.setWordWrap(True)
        chase_l.addWidget(chase_desc)

        chase_row1 = QHBoxLayout()
        chase_row1.addWidget(self._label("Số bot rượt:"))
        self.chase_count_spin = QSpinBox()
        self.chase_count_spin.setRange(1, 5)
        self.chase_count_spin.setValue(2)
        self.chase_count_spin.setFixedWidth(80)
        chase_row1.addWidget(self.chase_count_spin)

        chase_row1.addSpacing(15)
        chase_row1.addWidget(self._label("Hơn top 1 từ:"))
        self.chase_gap_min = QSpinBox()
        self.chase_gap_min.setRange(1, 10000)
        self.chase_gap_min.setValue(20)
        self.chase_gap_min.setFixedWidth(100)
        chase_row1.addWidget(self.chase_gap_min)

        chase_row1.addWidget(QLabel("đến"))
        self.chase_gap_max = QSpinBox()
        self.chase_gap_max.setRange(1, 100000)
        self.chase_gap_max.setValue(80)
        self.chase_gap_max.setFixedWidth(100)
        chase_row1.addWidget(self.chase_gap_max)

        chase_row1.addSpacing(15)
        chase_row1.addWidget(self._label("Cập nhật mỗi (giây):"))
        self.chase_interval = QDoubleSpinBox()
        self.chase_interval.setRange(1.0, 60.0)
        self.chase_interval.setValue(4.0)
        self.chase_interval.setSingleStep(0.5)
        self.chase_interval.setFixedWidth(90)
        chase_row1.addWidget(self.chase_interval)
        chase_row1.addStretch()
        chase_l.addLayout(chase_row1)

        chase_row2 = QHBoxLayout()
        btn_apply_chase = QPushButton("💾  Áp dụng")
        btn_apply_chase.setStyleSheet(btn_style("default", "md"))
        btn_apply_chase.clicked.connect(self._apply_chase_config)
        chase_row2.addWidget(btn_apply_chase)

        btn_create_chasers = QPushButton("🎯  Tạo bot rượt ngay")
        btn_create_chasers.setStyleSheet(btn_style("warning", "md"))
        btn_create_chasers.clicked.connect(self._create_chasers)
        chase_row2.addWidget(btn_create_chasers)
        chase_row2.addStretch()
        chase_l.addLayout(chase_row2)

        layout.addWidget(chase_box)

        cmt_box = QGroupBox("💬  COMMENT ROBLOX KHI BOT THẮNG")
        cmt_l = QVBoxLayout(cmt_box)
        cmt_l.setSpacing(10)

        cmt_desc = QLabel(
            "Khi bot giành top 1, comment giả sẽ xuất hiện trên "
            "khung <b>Fake Comment</b> (URL #2) với username Roblox."
        )
        cmt_desc.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px;"
        )
        cmt_desc.setWordWrap(True)
        cmt_l.addWidget(cmt_desc)

        cmt_row = QHBoxLayout()
        self.cmt_enabled_chk = QCheckBox(
            "Bật comment Roblox khi bot thắng"
        )
        self.cmt_enabled_chk.setChecked(True)
        self.cmt_enabled_chk.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text']}; font-size: 13px; }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['border_hi']};
                background: {COLORS['bg']};
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.cmt_enabled_chk.toggled.connect(self._toggle_roblox_cmt)
        cmt_row.addWidget(self.cmt_enabled_chk)

        cmt_row.addSpacing(15)
        cmt_row.addWidget(self._label("Delay (giây):"))
        self.cmt_delay = QDoubleSpinBox()
        self.cmt_delay.setRange(0.0, 10.0)
        self.cmt_delay.setValue(1.5)
        self.cmt_delay.setSingleStep(0.5)
        self.cmt_delay.setFixedWidth(90)
        cmt_row.addWidget(self.cmt_delay)

        btn_apply_cmt = QPushButton("💾  Áp dụng")
        btn_apply_cmt.setStyleSheet(btn_style("default", "sm"))
        btn_apply_cmt.clicked.connect(self._apply_cmt_config)
        cmt_row.addWidget(btn_apply_cmt)
        cmt_row.addStretch()
        cmt_l.addLayout(cmt_row)

        btn_test_cmt = QPushButton("🧪  Test comment ngay (dùng top 1)")
        btn_test_cmt.setStyleSheet(btn_style("primary", "sm"))
        btn_test_cmt.clicked.connect(self._test_roblox_cmt)
        cmt_l.addWidget(btn_test_cmt, alignment=Qt.AlignLeft)

        layout.addWidget(cmt_box)

        fx_box = QGroupBox("🎆  HIỆU ỨNG QUÀ TẶNG")
        fx_l = QVBoxLayout(fx_box)
        fx_l.setSpacing(10)

        fx_desc = QLabel(
            "Khi bot tặng quà, hiệu ứng xuất hiện trên 2 khung:<br>"
            "• <b>Gift FX</b> (URL #3) — quà lớn, phát file "
            "<code>animation.webm</code><br>"
            "• <b>Gift Text</b> (URL #4) — quà nhỏ, chữ chạy"
        )
        fx_desc.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 12px;"
        )
        fx_desc.setWordWrap(True)
        fx_l.addWidget(fx_desc)

        self.fx_enabled_chk = QCheckBox("Bật hiệu ứng quà tặng")
        self.fx_enabled_chk.setChecked(True)
        self.fx_enabled_chk.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text']}; font-size: 13px; }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['border_hi']};
                background: {COLORS['bg']};
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.fx_enabled_chk.toggled.connect(self._toggle_gift_fx)
        fx_l.addWidget(self.fx_enabled_chk)

        layout.addWidget(fx_box)

        list_box = QGroupBox("📋  DANH SÁCH BOT")
        list_l = QVBoxLayout(list_box)
        self.bot_list = QListWidget()
        self.bot_list.setMinimumHeight(220)
        list_l.addWidget(self.bot_list)

        list_btns = QHBoxLayout()
        btn_reload = QPushButton("🔄  Tải lại")
        btn_reload.setStyleSheet(btn_style("default", "sm"))
        btn_reload.clicked.connect(self._refresh_bot_list)

        btn_open_folder = QPushButton("📁  Mở thư mục assets/bots")
        btn_open_folder.setStyleSheet(btn_style("default", "sm"))
        btn_open_folder.clicked.connect(self._open_bots_folder)

        btn_open_gifts = QPushButton("🎁  Mở thư mục assets/gifts")
        btn_open_gifts.setStyleSheet(btn_style("default", "sm"))
        btn_open_gifts.clicked.connect(self._open_gifts_folder)

        list_btns.addWidget(btn_reload)
        list_btns.addWidget(btn_open_folder)
        list_btns.addWidget(btn_open_gifts)
        list_btns.addStretch()
        list_l.addLayout(list_btns)

        layout.addWidget(list_box, 1)

        self.bot_status = QLabel("🤖  Bot đã tắt")
        self.bot_status.setStyleSheet(f"""
            padding: 12px 16px;
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        layout.addWidget(self.bot_status)

        scroll.setWidget(container)
        outer.addWidget(scroll)
    # ---------- Tab 5: Nhật ký ----------
    def _build_tab_log(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 12, 4, 4)

        header = QHBoxLayout()
        title = QLabel("📜  NHẬT KÝ SỰ KIỆN")
        title.setStyleSheet(f"""
            color: {COLORS['primary_hi']};
            font-size: 14px; font-weight: 800;
            letter-spacing: 1px;
        """)
        btn_clear = QPushButton("🗑  Xóa nhật ký")
        btn_clear.setStyleSheet(btn_style("default", "sm"))
        btn_clear.clicked.connect(lambda: self.log_view.clear())
        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_clear)
        layout.addLayout(header)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
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
        layout.addWidget(self.log_view)
    
        # ---------- Tab: Theme ----------
        # ---------- Tab: Theme ----------
    def _build_tab_theme(self, parent):
        # ★ Bọc toàn bộ tab trong scroll area
        outer = QVBoxLayout(parent)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 12, 4, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel(
            "🎨  <b>CHỌN THEME BẢNG ĐẤU GIÁ</b><br>"
            "Chọn theme → xem preview TRỰC TIẾP bên phải → bấm Áp dụng."
        )
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            background: rgba(124, 92, 255, 0.1);
            border: 1px solid rgba(124, 92, 255, 0.4);
            border-radius: 10px;
            padding: 14px;
            font-size: 13px;
        """)
        header.setWordWrap(True)
        layout.addWidget(header)

        body = QHBoxLayout()
        body.setSpacing(12)

        # === LEFT: Danh sách theme ===
        left_box = QGroupBox("DANH SÁCH THEME")
        left_box.setFixedWidth(340)
        left_l = QVBoxLayout(left_box)
        left_l.setSpacing(8)

        self.theme_list = QListWidget()
        # ★ Tăng chiều cao tối thiểu
        self.theme_list.setMinimumHeight(600)
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
        left_l.addWidget(self.theme_list, 1)

        btn_row = QHBoxLayout()
        btn_apply = QPushButton("🎨  ÁP DỤNG")
        btn_apply.setStyleSheet(btn_style("success", "lg"))
        btn_apply.setMinimumHeight(48)
        btn_apply.clicked.connect(self._apply_selected_theme)
        btn_row.addWidget(btn_apply)

        btn_reload = QPushButton("🔄")
        btn_reload.setStyleSheet(btn_style("default", "md"))
        btn_reload.setMinimumHeight(48)
        btn_reload.setFixedWidth(60)
        btn_reload.setToolTip("Tải lại danh sách theme")
        btn_reload.clicked.connect(self._reload_themes)
        btn_row.addWidget(btn_reload)
        left_l.addLayout(btn_row)

        body.addWidget(left_box)

        # === RIGHT: Web view preview ===
        right_box = QGroupBox("XEM TRƯỚC (PREVIEW TRỰC TIẾP)")
        right_l = QVBoxLayout(right_box)
        right_l.setSpacing(8)

        # Thanh URL mini
        url_row = QHBoxLayout()
        url_row.addWidget(self._label("URL:"))

        self.preview_url = QLineEdit()
        self.preview_url.setReadOnly(True)
        self.preview_url.setMinimumHeight(38)
        self.preview_url.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg']};
                color: {COLORS['primary_hi']};
                border: 1px solid {COLORS['primary']};
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }}
        """)
        url_row.addWidget(self.preview_url, 1)

        btn_copy_url = QPushButton("📋")
        btn_copy_url.setStyleSheet(btn_style("default", "md"))
        btn_copy_url.setFixedWidth(50)
        btn_copy_url.setMinimumHeight(38)
        btn_copy_url.setToolTip("Copy URL")
        btn_copy_url.clicked.connect(
            lambda: self._copy_text(self.preview_url.text(), btn_copy_url)
        )
        url_row.addWidget(btn_copy_url)

        right_l.addLayout(url_row)

        # Web view
        if HAS_WEBENGINE:
            self.preview_view = QWebEngineView()
            # ★ Tăng chiều cao tối thiểu
            self.preview_view.setMinimumHeight(600)

            settings = self.preview_view.settings()
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptEnabled, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
            )

            self.preview_view.page().setBackgroundColor(QColor("#0a0a12"))
            right_l.addWidget(self.preview_view, 1)
        else:
            no_web = QLabel(
                "⚠️  Chưa cài PySide6-WebEngine\n\n"
                "Chạy:\nuv add PySide6-WebEngine\nuv sync"
            )
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
            no_web.setMinimumHeight(600)
            right_l.addWidget(no_web, 1)

        body.addWidget(right_box, 1)

        layout.addLayout(body, 1)

        # Nút áp dụng to ở dưới
        bottom_row = QHBoxLayout()
        btn_apply_big = QPushButton("🎨   ÁP DỤNG THEME ĐANG CHỌN   🎨")
        btn_apply_big.setStyleSheet(btn_style("success", "lg"))
        btn_apply_big.setMinimumHeight(56)
        btn_apply_big.clicked.connect(self._apply_selected_theme)
        bottom_row.addWidget(btn_apply_big, 1)
        layout.addLayout(bottom_row)

        scroll.setWidget(container)
        outer.addWidget(scroll)

        self._reload_themes()

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
    def _build_tab_help(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 12, 4, 4)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
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
            <li>Tab <b>Kết nối Live</b> → nhập <code>@username</code></li>
            <li>Copy <b>5 link</b> → dán vào TikTok Studio</li>
            <li>Tab <b>Giọng nói</b> → BẮT ĐẦU NÓI</li>
        </ol>

        <h3>📺 5 URL overlay</h3>
        <table cellpadding="6" style="color: white;">
            <tr><td><b>#1</b></td><td><code>widget.html</code></td>
                <td>Bảng đấu giá + timer</td></tr>
            <tr><td><b>#2</b></td><td><code>cmt.html</code></td>
                <td>Fake comment Roblox</td></tr>
            <tr><td><b>#3</b></td><td><code>gift-fx.html</code></td>
                <td>Hiệu ứng quà</td></tr>
            <tr><td><b>#4</b></td><td><code>gift-text.html</code></td>
                <td>Live chat quà</td></tr>
            <tr><td><b>#5</b></td><td><code>vtuber.html</code></td>
                <td>Nhân vật AI nhép miệng</td></tr>
        </table>

        <h3>🎭 Nhân vật AI</h3>
        <ul>
            <li>Bỏ 3 ảnh vào <code>vtuber/assets/</code>:
                character.png, character-talking.png, character-blink.png</li>
            <li>Nói vào mic → nhân vật nhép miệng</li>
            <li>Đổi giọng → người xem nghe giọng AI</li>
        </ul>

        <h3>🛡️ Nhắc nhở</h3>
        <ul>
            <li>Công bố luật đầu live</li>
            <li>KHÔNG dùng bot khi live thật</li>
        </ul>
        """)
        layout.addWidget(help_text)

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

        for key in ["widget", "cmt", "gift_fx", "gift_text", "vtuber"]:
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

        self.device_label.setText(srv.device_id)

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
                self.user_combo.addItem(
                    f"{prefix}{u}  —  {score} điểm", u
                )
            if current:
                for i in range(self.user_combo.count()):
                    if self.user_combo.itemData(i) == current:
                        self.user_combo.setCurrentIndex(i)
                        break

    def _on_gift_changed(self, idx):
        data = self.gift_combo.itemData(idx)
        if data:
            pts, effect, name, icon, folder = data
            self.pts_input.setValue(int(pts))

    # ---------- Actions ----------
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
        eng.start()
        self.winner_label.hide()
        self._refresh_user_combo()
        self._append_log(
            f"▶ Phiên bắt đầu: {eng.main_duration}s chính, "
            f"{eng.snap_duration}s snap"
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
        self.worker.engine.balance_top2()
        self._refresh_user_combo()
        self._append_log("⚖ Đã cân bằng top 2")

    def add_manual_score(self):
        user = self.user_combo.currentData()
        if not user:
            return
        pts = self.pts_input.value()
        gift_cur = self.gift_combo.currentData()
        if gift_cur:
            pts_g, effect, name, icon, folder = gift_cur
        else:
            effect, name, icon, folder = "text", "Rose", "🌹", "rose"

        self.worker.engine.add_score(user, pts, source=name)

        if self.worker.bot_manager.gift_effects_enabled:
            self.worker.server.send_event_sync("gift_event", {
                "user": user,
                "display_name": user.lstrip("@"),
                "points": pts,
                "gift_name": name,
                "gift_icon": icon,
                "effect": effect,
                "folder": folder,
                "is_bot": False,
            })

    # ---------- Kết nối TikTok ----------
    def connect_tiktok(self):
        raw = self.live_input.text().strip()
        if not raw:
            QMessageBox.warning(
                self, "Thiếu thông tin",
                "Nhập username hoặc link TikTok Live"
            )
            return

        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.btn_disconnect.setText("⏹   DỪNG CHỜ")

        self.live_status.setText(f"⏳  Đang chờ {raw} lên live ...")
        self.live_status.setStyleSheet(f"""
            padding: 14px 18px;
            background: rgba(124, 92, 255, 0.1);
            color: {COLORS['primary_hi']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['primary']};
        """)

        self.worker.submit(self.worker.tiktok.connect(raw, retry=True))

        self.conn_indicator.setText(f"🟣 Đang chờ {raw} live")
        self.conn_indicator.setStyleSheet(f"""
            background: rgba(124, 92, 255, 0.15);
            color: {COLORS['primary_hi']};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid {COLORS['primary']};
        """)

    def disconnect_tiktok(self):
        self.worker.tiktok.stop_waiting()
        self.worker.submit(self.worker.tiktok.disconnect())

        self.tiktok_connected = False
        self.tiktok_username = ""
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

        self.conn_indicator.setText("⚪ Chưa kết nối TikTok")
        self.conn_indicator.setStyleSheet(f"""
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)

        self.live_status.setText("⚪  Đã dừng. Nhập ID và bấm KẾT NỐI.")
        self.live_status.setStyleSheet(f"""
            padding: 14px 18px;
            background: {COLORS['bg']};
            color: {COLORS['text_dim']};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        self._update_start_button()

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

    # ---------- Signals ----------
    def _append_log(self, msg):
        self.log_view.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _set_status(self, text):
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
        self.live_status.setText(translated)

        if text.startswith("✅"):
            self.tiktok_connected = True
            self.tiktok_username = self.live_input.text().strip()
            self.conn_indicator.setText(
                f"🟢 Đã kết nối: {self.tiktok_username}"
            )
            self.conn_indicator.setStyleSheet(f"""
                background: rgba(0, 214, 143, 0.15);
                color: {COLORS['success']};
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid {COLORS['success']};
            """)
            self.live_status.setStyleSheet(f"""
                padding: 14px 18px;
                background: rgba(0, 214, 143, 0.1);
                color: {COLORS['success']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 700;
                border: 1px solid {COLORS['success']};
            """)
            self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")
            QTimer.singleShot(800, lambda: self.tabs.setCurrentIndex(0))

        elif text.startswith("⏳") or "waiting" in text.lower():
            self.conn_indicator.setText("🟣 Đang chờ live")
            self.conn_indicator.setStyleSheet(f"""
                background: rgba(124, 92, 255, 0.15);
                color: {COLORS['primary_hi']};
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid {COLORS['primary']};
            """)
            self.live_status.setStyleSheet(f"""
                padding: 14px 18px;
                background: rgba(124, 92, 255, 0.1);
                color: {COLORS['primary_hi']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid {COLORS['primary']};
            """)

        elif text.startswith("⏹"):
            self.tiktok_connected = False
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")
            self.conn_indicator.setText("⚪ Chưa kết nối TikTok")

        elif text.startswith("⚠️") or text.startswith("❌"):
            self.tiktok_connected = False
            self.conn_indicator.setText("🔴 Lỗi kết nối")
            self.conn_indicator.setStyleSheet(f"""
                background: rgba(255, 61, 90, 0.15);
                color: {COLORS['danger']};
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid {COLORS['danger']};
            """)
            self.live_status.setStyleSheet(f"""
                padding: 14px 18px;
                background: rgba(255, 61, 90, 0.1);
                color: {COLORS['danger']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid {COLORS['danger']};
            """)
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            self.btn_disconnect.setText("⛔   NGẮT KẾT NỐI")

        elif text.startswith("⛔"):
            self.tiktok_connected = False
            self.conn_indicator.setText("⚪ Chưa kết nối TikTok")

        self._update_start_button()
        self.statusBar().showMessage(translated, 5000)

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