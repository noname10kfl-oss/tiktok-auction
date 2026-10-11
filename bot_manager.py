"""Bot manager with chase mode, Roblox comments, gift effects."""
import asyncio
import random
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

import gifts as gift_data


@dataclass
class Bot:
    user: str
    display_name: str
    avatar_path: Optional[Path]
    score: int = 0
    active: bool = True
    next_gift_at: float = 0.0
    created_at: float = field(default_factory=time.time)
    is_chaser: bool = False
    roblox_username: str = ""


def make_username(display_name: str, suffix: str = "") -> str:
    norm = unicodedata.normalize("NFKD", display_name)
    ascii_name = norm.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9 _\-]", "", ascii_name)
    username = re.sub(r"[\s\-]+", "_", cleaned.strip())
    if not username:
        username = f"user{random.randint(1000, 9999)}"
    if suffix:
        username += f"_{suffix}"
    return "@" + username


def make_roblox_username(display_name: str) -> str:
    norm = unicodedata.normalize("NFKD", display_name)
    ascii_name = norm.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^A-Za-z0-9]", "", ascii_name)[:10]
    if not base:
        base = "Player"
    suffix = random.choice([
        "Gamer", "Pro", "YT", "VN", "X", "Z", "King", "Boss",
        "2010", "2011", "2012", "99", "888", "UwU", "OP",
        "Roblox", "Bacon", "Noob", "Master", "Legend",
    ])
    number = random.randint(10, 9999)
    return f"{base}_{suffix}{number}"


DEFAULT_NAMES = [
    "Emily Rose", "James Carter", "Sophia Miller", "Michael Brown",
    "Olivia Davis", "William Wilson", "Ava Martinez", "Daniel Anderson",
    "Mia Thompson", "Ethan Garcia", "Charlotte Lee", "Noah Rodriguez",
    "Amelia White", "Lucas Harris", "Isabella Clark", "Mason Lewis",
    "Harper Walker", "Logan Hall", "Evelyn Young", "Jacob King",
    "Yuki Tanaka", "Haruto Sato", "Sakura Ito", "Ren Suzuki",
    "Hina Takahashi", "Sota Watanabe", "Aoi Yamamoto", "Yuto Nakamura",
    "Rin Kobayashi", "Kaito Kato",
    "Min-jun Kim", "Seo-yeon Lee", "Ji-ho Park", "Ha-eun Choi",
    "Do-yun Jung", "Soo-ah Kang", "Jun-seo Yoon", "Ye-jin Jang",
    "Tae-yang Lim", "Na-eun Han",
    "Wei Chen", "Mei Lin", "Jun Wang", "Xin Zhang", "Hao Liu",
    "Yan Zhao", "Bo Huang", "Lan Zhou", "Feng Wu", "Jing Xu",
    "Lukas Müller", "Sofia Rossi", "Pierre Dubois", "Emma Schmidt",
    "Marco Ferrari", "Chloé Martin", "Felix Weber", "Isabella Romano",
    "Antoine Bernard", "Lena Fischer",
    "Alex Storm", "Nova Star", "Luna Moon", "Max Blaze", "Sky Phoenix",
    "Riley Frost", "Zoe Thunder", "Kai Shadow", "Ivy Raven", "Leo Night",
]


class BotManager:
    def __init__(self, base_dir: Path,
                 on_gift: Callable[[str, int], None],
                 on_log: Callable[[str], None],
                 on_overlay_event: Optional[Callable[[str, dict], None]] = None,
                 get_top_user: Optional[Callable[[], tuple]] = None):
        self.base_dir = base_dir
        self.avatars_dir = base_dir / "assets" / "bots" / "avatars"
        self.names_file = base_dir / "assets" / "bots" / "names.txt"
        self.on_gift = on_gift
        self.on_log = on_log
        self.on_overlay_event = on_overlay_event
        self.get_top_user = get_top_user

        self.avatars_dir.mkdir(parents=True, exist_ok=True)
        self.names_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.names_file.exists():
            self._write_default_names()

        self.bots: List[Bot] = []
        self.enabled = False
        self.interval_min = 3.0
        self.interval_max = 8.0
        self.points_min = 5
        self.points_max = 100
        self.max_score = 0
        self._task = None

        self.chase_enabled = False
        self.chase_count = 2
        self.chase_gap_min = 20
        self.chase_gap_max = 80
        self.chase_interval = 4.0

        self.roblox_cmt_enabled = True
        self.roblox_cmt_delay = 1.5

        self.gift_effects_enabled = True

    def _write_default_names(self):
        lines = ["# Bot Names - International",
                 "# One line per name. # = comment.",
                 ""]
        lines.extend(DEFAULT_NAMES)
        try:
            self.names_file.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            print(f"[names file] {e}")

    def load_names(self) -> List[str]:
        if not self.names_file.exists():
            return DEFAULT_NAMES[:]
        try:
            names = []
            for line in self.names_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                names.append(line)
            return names or DEFAULT_NAMES[:]
        except Exception:
            return DEFAULT_NAMES[:]

    def load_avatars(self) -> List[Path]:
        if not self.avatars_dir.exists():
            return []
        exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        return sorted([
            p for p in self.avatars_dir.iterdir()
            if p.is_file() and p.suffix.lower() in exts
        ])

    # ============ BOT CRUD ============
    def add_bot(self, display_name: Optional[str] = None,
                is_chaser: bool = False) -> Bot:
        names = self.load_names()
        avatars = self.load_avatars()

        used = {b.display_name for b in self.bots}
        available = [n for n in names if n not in used]
        if not available:
            available = [f"{n} {random.randint(10, 999)}" for n in names]
        name = display_name or random.choice(available)

        user = make_username(name)
        existing_users = {b.user for b in self.bots}
        if user in existing_users:
            user = make_username(name, suffix=str(random.randint(10, 9999)))

        avatar = random.choice(avatars) if avatars else None
        roblox = make_roblox_username(name) if is_chaser else ""

        bot = Bot(
            user=user,
            display_name=name,
            avatar_path=avatar,
            is_chaser=is_chaser,
            roblox_username=roblox,
        )
        self.bots.append(bot)
        tag = "🎯 [CHASE]" if is_chaser else "🤖 [BOT]"
        self.on_log(
            f"{tag} Đã thêm: {name} ({user})"
            + (f" — Roblox: {roblox}" if roblox else "")
        )
        return bot

    def add_bots(self, count: int) -> int:
        added = 0
        for _ in range(count):
            try:
                self.add_bot()
                added += 1
            except Exception as e:
                self.on_log(f"❌ Không thêm được bot: {e}")
        return added

    def clear_bots(self):
        n = len(self.bots)
        self.bots.clear()
        self.on_log(f"🗑 [BOT] Đã xóa toàn bộ {n} bot")

    def configure(self, interval_min=None, interval_max=None,
                  points_min=None, points_max=None, max_score=None):
        if interval_min is not None:
            self.interval_min = max(0.5, float(interval_min))
        if interval_max is not None:
            self.interval_max = max(self.interval_min, float(interval_max))
        if points_min is not None:
            self.points_min = max(1, int(points_min))
        if points_max is not None:
            self.points_max = max(self.points_min, int(points_max))
        if max_score is not None:
            self.max_score = max(0, int(max_score))

    def configure_chase(self, enabled=None, count=None,
                        gap_min=None, gap_max=None, interval=None):
        if enabled is not None:
            self.chase_enabled = bool(enabled)
        if count is not None:
            self.chase_count = max(1, min(5, int(count)))
        if gap_min is not None:
            self.chase_gap_min = max(1, int(gap_min))
        if gap_max is not None:
            self.chase_gap_max = max(self.chase_gap_min, int(gap_max))
        if interval is not None:
            self.chase_interval = max(1.0, float(interval))

    # ============ GIFT PICKER ============
    def _pick_gift(self, max_points: int):
        """
        Chọn quà có giá <= max_points.
        Ưu tiên: Rose, TikTok, GG, Finger Heart (70%).
        """
        affordable = [
            g for g in gift_data.GIFTS if g[2] <= max_points
        ]
        if not affordable:
            affordable = [min(gift_data.GIFTS, key=lambda g: g[2])]

        priority_names = ["Rose", "TikTok", "GG", "Finger Heart"]
        priority_gifts = [
            g for g in affordable if g[0] in priority_names
        ]

        if priority_gifts and random.random() < 0.7:
            return random.choice(priority_gifts)

        return random.choice(affordable)

    # ============ GIFT EFFECTS ============
    def _emit_gift_event(self, bot: Bot, gift: tuple, count: int):
        """Emit gift event với thông tin quà + số lượng."""
        if not self.gift_effects_enabled or not self.on_overlay_event:
            return
        name, icon, gift_pts, effect, folder = gift
        total_points = gift_pts * count

        payload = {
            "user": bot.user,
            "display_name": bot.display_name,
            "points": total_points,
            "gift_name": name,
            "gift_icon": icon,
            "gift_points": gift_pts,
            "gift_count": count,
            "effect": effect,
            "folder": folder,
            "is_bot": True,
            "is_chaser": bot.is_chaser,
        }
        self.on_overlay_event("gift_event", payload)

    def _emit_roblox_comment(self, bot: Bot):
        if not self.roblox_cmt_enabled or not self.on_overlay_event:
            return
        if not bot.roblox_username:
            bot.roblox_username = make_roblox_username(bot.display_name)
        self.on_overlay_event("roblox_comment", {
            "user": bot.user,
            "display_name": bot.display_name,
            "roblox_username": bot.roblox_username,
            "delay": self.roblox_cmt_delay,
        })
        self.on_log(
            f"💬 [ROBLOX] {bot.display_name} → "
            f"comment Roblox: {bot.roblox_username}"
        )

    # ============ CHASE LOOP ============
    async def _chase_loop(self):
        self.on_log(
            f"🎯 [CHASE] Bật — {self.chase_count} bot, "
            f"hơn top 1 từ {self.chase_gap_min}-{self.chase_gap_max} điểm, "
            f"mỗi {self.chase_interval}s"
        )

        chasers = [b for b in self.bots if b.is_chaser]
        while len(chasers) < self.chase_count:
            new_bot = self.add_bot(is_chaser=True)
            chasers.append(new_bot)

        while self.enabled and self.chase_enabled:
            try:
                await asyncio.sleep(self.chase_interval)

                if not self.get_top_user:
                    continue
                top_user, top_score = self.get_top_user()
                if not top_user or top_score <= 0:
                    continue

                for chaser in chasers:
                    if not chaser.active:
                        continue
                    if chaser.user == top_user:
                        continue

                    gap = random.randint(
                        self.chase_gap_min, self.chase_gap_max
                    )
                    target = top_score + gap
                    delta = target - chaser.score

                    if delta <= 0:
                        continue

                    chaser.score += delta
                    gift = gift_data.gift_from_points(delta)
                    self._emit_gift_event(chaser, gift, 1)
                    try:
                        self.on_gift(chaser.user, delta)
                    except Exception as e:
                        self.on_log(f"❌ Chase gift error: {e}")

                    self.on_log(
                        f"🎯 [CHASE] {chaser.display_name} vượt top — "
                        f"+{delta} điểm (tổng {chaser.score})"
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.on_log(f"❌ Chase loop error: {e}")

        self.on_log("🎯 [CHASE] Đã tắt")

    # ============ MAIN LOOP ============
    async def run(self):
        self.on_log(
            f"🤖 [BOT] BẮT ĐẦU — {len(self.bots)} bot, "
            f"tặng mỗi {self.interval_min:.1f}-{self.interval_max:.1f}s"
        )
        self.on_log(
            "⚠️  [BOT] CẢNH BÁO: Đây là bot TEST. "
            "Không dùng khi live thật."
        )

        chase_task = None
        if self.chase_enabled:
            chase_task = asyncio.create_task(self._chase_loop())

        now = time.time()
        for bot in self.bots:
            if bot.is_chaser:
                continue
            bot.next_gift_at = now + random.uniform(
                self.interval_min, self.interval_max
            )

        while self.enabled:
            try:
                await asyncio.sleep(0.5)
                now = time.time()
                for bot in list(self.bots):
                    if bot.is_chaser:
                        continue
                    if not bot.active:
                        continue
                    if now < bot.next_gift_at:
                        continue
                    if self.max_score > 0 and bot.score >= self.max_score:
                        continue

                    # BƯỚC 1: Mục tiêu điểm
                    target_points = random.randint(
                        self.points_min, self.points_max
                    )

                    if self.max_score > 0:
                        remaining = self.max_score - bot.score
                        if remaining <= 0:
                            continue
                        target_points = min(target_points, remaining)

                    if target_points <= 0:
                        continue

                    # BƯỚC 2: Chọn quà <= target
                    gift = self._pick_gift(target_points)
                    gift_name, gift_icon, gift_pts, gift_effect, gift_folder = gift

                    if gift_pts <= 0:
                        continue

                    # BƯỚC 3: Tính count (chia nguyên)
                    count = max(1, target_points // gift_pts)
                    total_points = gift_pts * count

                    # BƯỚC 4: Cắt nếu vượt max
                    if self.max_score > 0:
                        remaining = self.max_score - bot.score
                        if total_points > remaining:
                            count = remaining // gift_pts
                            if count <= 0:
                                continue
                            total_points = gift_pts * count

                    if total_points <= 0:
                        continue

                    bot.score += total_points
                    self._emit_gift_event(bot, gift, count)
                    try:
                        self.on_gift(bot.user, total_points)
                    except Exception as e:
                        self.on_log(f"❌ Bot gift error: {e}")

                    self.on_log(
                        f"🤖 [BOT] {bot.display_name} tặng "
                        f"{gift_name} x{count} (+{total_points} điểm) "
                        f"→ tổng {bot.score}"
                    )

                    bot.next_gift_at = now + random.uniform(
                        self.interval_min, self.interval_max
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.on_log(f"❌ Bot loop error: {e}")

        if chase_task:
            chase_task.cancel()
            try:
                await chase_task
            except Exception:
                pass

        self.on_log("🤖 [BOT] ĐÃ DỪNG toàn bộ bot")

    def start(self, loop):
        if self.enabled:
            return
        self.enabled = True
        self._task = asyncio.run_coroutine_threadsafe(self.run(), loop)

    def stop(self):
        if not self.enabled:
            return
        self.enabled = False
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass
            self._task = None
        self.on_log("⏹ [BOT] Đã dừng bot")

    def notify_winner(self, winner_user: str):
        bot = self.get_by_user(winner_user)
        if bot:
            self._emit_roblox_comment(bot)

    def get_by_user(self, user: str) -> Optional[Bot]:
        for b in self.bots:
            if b.user == user:
                return b
        return None

    @property
    def chasers(self) -> List[Bot]:
        return [b for b in self.bots if b.is_chaser]