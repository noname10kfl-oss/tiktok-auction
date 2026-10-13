"""Auction engine - no UI dependency."""
import json
import time
import asyncio
import threading
from collections import defaultdict
from enum import Enum
from pathlib import Path

import bosses as boss_data


class Phase(Enum):
    IDLE = "idle"
    MAIN = "main"
    SNAP = "snap"
    FINISHED = "finished"


class AuctionEngine:
    def __init__(self, main_duration=60, snap_duration=30, min_coins=10,
                 vouch_file=None, robux_file=None):
        self.scores = defaultdict(int)
                # ★ AUTO RESET
        self.auto_reset_boss = True       # Tự động reset boss khi xong ván
        self.auto_reset_pot = True        # Tự động reset pot khi xong ván
        self.auto_reset_boss_level = 1    # Reset về level nào (1 = từ đầu)
        self.first_reach = {}
        self.avatars = {}
        self.display_names = {}
        self.auto_next_boss = True   # ★ Tự động lên level
        self.auto_next_delay = 3.0   # Giây
        self.min_coins = min_coins
        self.phase = Phase.IDLE
        self.main_duration = main_duration
        self.snap_duration = snap_duration
        self.snap_count = 0
        self.phase_start = None
        self.phase_duration = 0
        self.winner = None
        self.history = []
        self._stop_flag = False
        self.listeners = []
        self._last_notify_sec = -1
        
                # ★ AUTO TIE
        self.auto_tie_enabled = False
        self.auto_tie_user = ""
        self.auto_tie_amount = 1
        self.auto_tie_delay = 2.0
        self.last_auto_tie_time = 0

        # VOUCH
        self.vouch_file = Path(vouch_file) if vouch_file else None
        self.vouch = self._load_vouch()
        
                # ★ AUTO FAKE GIFT
        self.auto_fake_gift_enabled = False
        self.auto_fake_gift_mapping = [
            (30,   "Donut",           "🍩", "doughnut"),
            (100,  "Game Controller", "🎮", "game_controller"),
            (299,  "Corgi",           "🐕", "corgi"),
            (500,  "Money Gun",       "💸", "money_gun"),
            (699,  "Swan",            "🦢", "swan"),
            (1000, "Galaxy",          "🌌", "galaxy"),
        ]

        # ROBUX
        self.robux_file = Path(robux_file) if robux_file else None
        self.reset_robux_value = self._load_robux()
        self.robux_pot = self.reset_robux_value
        self.last_winner_pot = 0

        # BOSS CONFIG
        self.boss_level = 1
        self.hp_base = boss_data.DEFAULT_HP_BASE
        self.hp_multiplier = boss_data.DEFAULT_HP_MULTIPLIER
        self.robux_base = boss_data.DEFAULT_ROBUX_BASE
        self.robux_multiplier = boss_data.DEFAULT_ROBUX_MULTIPLIER
        self.gift_base = boss_data.DEFAULT_GIFT_BASE
        self.gift_multiplier = boss_data.DEFAULT_GIFT_MULTIPLIER
        self.gift_max = boss_data.DEFAULT_GIFT_MAX

        self.boss_hp = boss_data.get_hp(1, self.hp_base, self.hp_multiplier)
        self.boss_max_hp = self.boss_hp
        self.boss_alive = True
        self.boss_killed_count = 0
        self.damage_flash_until = 0
        self.boss_died_at = 0

    # ============ VOUCH ============
    def start_snap_manual(self):
        """★ Bắt đầu SNAP thủ công — không cần hòa hay ≥ 2 người."""
        if self.phase == Phase.IDLE:
            self._log("⚠️ Chưa bắt đầu ván — không thể SNAP")
            return False
        if self.phase == Phase.FINISHED:
            self._log("⚠️ Ván đã kết thúc — không thể SNAP")
            return False

        self.snap_count += 1
        self._enter_phase(Phase.SNAP, self.snap_duration)
        leaders = self.get_leaders()
        tie_status = "TIE" if len(leaders) > 1 else "NO TIE"
        self._log(
            f"⚡ MANUAL SNAP #{self.snap_count} – {self.snap_duration}s – "
            f"{tie_status} – leaders: {leaders}"
        )
        return True
    def _load_vouch(self):
        if self.vouch_file and self.vouch_file.exists():
            try:
                data = json.loads(self.vouch_file.read_text(encoding="utf-8"))
                return int(data.get("vouch", 0))
            except Exception:
                pass
        return 0

    def _save_vouch(self):
        if not self.vouch_file:
            return
        try:
            self.vouch_file.parent.mkdir(parents=True, exist_ok=True)
            self.vouch_file.write_text(
                json.dumps({"vouch": self.vouch}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def increment_vouch(self):
        self.vouch += 1
        self._save_vouch()
        self._log(f"Vouch = {self.vouch}")
        self._notify()
        
    def set_auto_tie(self, enabled=None, user=None, amount=None, delay=None):
        """Cập nhật config auto tie."""
        if enabled is not None:
            self.auto_tie_enabled = bool(enabled)
        if user is not None:
            self.auto_tie_user = user
        if amount is not None:
            self.auto_tie_amount = max(1, int(amount))
        if delay is not None:
            self.auto_tie_delay = max(0.5, float(delay))
        self._log(
            f"Auto Tie: enabled={self.auto_tie_enabled}, "
            f"user={self.auto_tie_user}, amount={self.auto_tie_amount}, "
            f"delay={self.auto_tie_delay}"
        )
        self._notify()

    def _apply_auto_tie(self):
        """★ Áp dụng auto tie nếu đang hòa."""
        if not self.auto_tie_enabled or not self.auto_tie_user:
            return

        leaders = self.get_leaders()
        if self.auto_tie_user not in leaders:
            return

        # Check delay
        now = time.time()
        if now - self.last_auto_tie_time < self.auto_tie_delay:
            return
        self.last_auto_tie_time = now

        # Cộng điểm cho user
        self.scores[self.auto_tie_user] += self.auto_tie_amount
        if self.auto_tie_user not in self.first_reach:
            self.first_reach[self.auto_tie_user] = now

        self._log(
            f"⚖ Auto Tie: +{self.auto_tie_amount} cho {self.auto_tie_user} "
            f"(total {self.scores[self.auto_tie_user]})"
        )
        self._notify()

    def reset_vouch(self):
        self.vouch = 0
        self._save_vouch()
        self._log("Vouch reset = 0")
        self._notify()

    def set_vouch(self, value):
        try:
            self.vouch = max(0, int(value))
        except Exception:
            self.vouch = 0
        self._save_vouch()
        self._notify()

    # ============ ROBUX ============
    def _load_robux(self):
        if self.robux_file and self.robux_file.exists():
            try:
                data = json.loads(self.robux_file.read_text(encoding="utf-8"))
                return int(data.get("reset_robux", 500))
            except Exception:
                pass
        return 500

    def _save_robux(self):
        if not self.robux_file:
            return
        try:
            self.robux_file.parent.mkdir(parents=True, exist_ok=True)
            self.robux_file.write_text(
                json.dumps({"reset_robux": self.reset_robux_value}, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def set_reset_robux_value(self, value):
        try:
            self.reset_robux_value = max(0, int(value))
        except Exception:
            self.reset_robux_value = 500
        self._save_robux()
        self._log(f"Reset Robux = {self.reset_robux_value}")
        self._notify()

    def reset_robux_pot(self):
        self.robux_pot = self.reset_robux_value
        self._log(f"Robux pot reset = {self.robux_pot}")
        self._notify()

    # ============ BOSS ============
    def set_boss_level(self, level):
        level = max(1, min(level, boss_data.max_level()))
        self.boss_level = level
        self.boss_hp = boss_data.get_hp(level, self.hp_base, self.hp_multiplier)
        self.boss_max_hp = self.boss_hp
        self.boss_alive = True
        self.boss_died_at = 0
        b = boss_data.get_boss_name(level)
        self._log(f"Boss Lv.{level} {b['name']} ({self.boss_hp} HP)")
        self._notify()

    def set_boss_config(self, hp_base=None, hp_mult=None,
                        robux_base=None, robux_mult=None,
                        gift_base=None, gift_mult=None, gift_max=None):
        if hp_base is not None:
            self.hp_base = max(1, int(hp_base))
        if hp_mult is not None:
            self.hp_multiplier = max(1.0, float(hp_mult))
        if robux_base is not None:
            self.robux_base = max(0, int(robux_base))
        if robux_mult is not None:
            self.robux_multiplier = max(1.0, float(robux_mult))
        if gift_base is not None:
            self.gift_base = max(1, int(gift_base))
        if gift_mult is not None:
            self.gift_multiplier = max(1.0, float(gift_mult))
        if gift_max is not None:
            self.gift_max = max(1, int(gift_max))
        self._log("Boss config updated")
        self._notify()

    def apply_boss_config(self):
        self.boss_hp = boss_data.get_hp(self.boss_level, self.hp_base, self.hp_multiplier)
        self.boss_max_hp = self.boss_hp
        self.boss_alive = True
        self.boss_died_at = 0
        self._log(f"Boss config applied — Lv.{self.boss_level} HP={self.boss_hp}")
        self._notify()

    def reset_boss(self):
        b = boss_data.get_boss_name(self.boss_level)
        self.boss_hp = boss_data.get_hp(self.boss_level, self.hp_base, self.hp_multiplier)
        self.boss_max_hp = self.boss_hp
        self.boss_alive = True
        self.boss_died_at = 0
        self._log(f"Boss reset — {b['name']} ({self.boss_hp} HP)")
        self._notify()

    def damage_boss(self, damage):
        if not self.boss_alive or damage <= 0:
            return False
        self.boss_hp = max(0, self.boss_hp - damage)
        self.damage_flash_until = time.time() + 0.4
        if self.boss_hp <= 0:
            self.boss_alive = False
            self.boss_killed_count += 1
            self.boss_died_at = time.time()
            reward = self.get_boss_reward()
            self.robux_pot += reward
            b = boss_data.get_boss_name(self.boss_level)
            self._log(f"BOSS DEFEATED! Lv.{self.boss_level} {b['name']} "
                      f"+{reward} Robux (Pot: {self.robux_pot})")
            # ★ Tự động lên level tiếp theo sau 3s
            self._schedule_next_boss()
            return True
        return False

    def _schedule_next_boss(self, delay=None):
        if not self.auto_next_boss:
            return
        delay = delay if delay is not None else self.auto_next_delay

        def _next():
            time.sleep(delay)
            if not self.boss_alive:
                next_level = self.boss_level + 1
                max_lv = boss_data.max_level()
                if next_level > max_lv:
                    next_level = max_lv
                self.set_boss_level(next_level)
                self._log(f"⬆ Auto next boss → Lv.{next_level}")

        t = threading.Thread(target=_next, daemon=True)
        t.start()

    def set_auto_next_boss(self, enabled, delay=None):
        self.auto_next_boss = bool(enabled)
        if delay is not None:
            self.auto_next_delay = max(0.5, float(delay))
        self._log(f"Auto next boss: {self.auto_next_boss}")
        self._notify()
        
    def set_auto_fake_gift(self, enabled, mapping=None):
        """Bật/tắt auto fake gift."""
        self.auto_fake_gift_enabled = bool(enabled)
        if mapping is not None:
            self.auto_fake_gift_mapping = mapping
        self._log(f"Auto Fake Gift: {self.auto_fake_gift_enabled}")
        self._notify()

    def pick_fake_gift_by_points(self, points):
        """★ Chọn gift ảo theo điểm (gần nhất nhưng ≤ points)."""
        if not self.auto_fake_gift_enabled:
            return None
        chosen = None
        for threshold, name, icon, folder in self.auto_fake_gift_mapping:
            if points >= threshold:
                chosen = {"name": name, "icon": icon, "folder": folder}
            else:
                break
        return chosen

    def get_boss_reward(self):
        return boss_data.get_robux_reward(
            self.boss_level, self.robux_base, self.robux_multiplier)

    def get_boss_gift_count(self, level=None):
        lv = level if level is not None else self.boss_level
        return boss_data.get_gift_count(
            lv, self.gift_base, self.gift_multiplier, self.gift_max)

    def get_boss_hp(self, level=None):
        lv = level if level is not None else self.boss_level
        return boss_data.get_hp(lv, self.hp_base, self.hp_multiplier)

    # ============ LISTENERS ============
    def add_listener(self, cb):
        self.listeners.append(cb)

    def _notify(self):
        snap = self.snapshot()
        for cb in self.listeners:
            try:
                cb(snap)
            except Exception as e:
                print(f"[listener] {e}")

    def start(self):
        self.scores.clear()
        self.first_reach.clear()
        self.avatars.clear()
        self.display_names.clear()
        self.snap_count = 0
        self.winner = None
        self.history.clear()
        self._stop_flag = False
        self._last_notify_sec = -1

        # Reset pot về giá trị khởi tạo
        self.robux_pot = self.reset_robux_value

        # Reset boss full HP
        self.boss_hp = boss_data.get_hp(
            self.boss_level, self.hp_base, self.hp_multiplier
        )
        self.boss_max_hp = self.boss_hp
        self.boss_alive = True
        self.boss_died_at = 0

        self._enter_phase(Phase.MAIN, self.main_duration)
        self._log(f"Main round started ({self.main_duration}s) — "
                  f"pot reset to {self.robux_pot}")

    def stop(self):
        self._stop_flag = True
        self.phase = Phase.FINISHED
        self._log("Stopped manually")
        self._notify()

    def reset(self):
        self.scores.clear()
        self.first_reach.clear()
        self.avatars.clear()
        self.display_names.clear()
        self.snap_count = 0
        self.winner = None
        self.history.clear()
        self.phase = Phase.IDLE
        self._stop_flag = False
        self._last_notify_sec = -1
        self._log("Reset")
        self._notify()

    def _enter_phase(self, phase, duration):
        self.phase = phase
        self.phase_start = time.time()
        self.phase_duration = duration
        self._last_notify_sec = -1
        self._log(f"Phase {phase.value}, {duration}s")
        self._notify()

    def remaining(self):
        if self.phase in (Phase.IDLE, Phase.FINISHED):
            return 0
        return max(0, self.phase_duration - (time.time() - self.phase_start))

    def set_avatar(self, user, avatar_url):
        if user and avatar_url:
            self.avatars[user] = avatar_url

    def set_display_name(self, user, display_name):
        if user and display_name:
            self.display_names[user] = display_name

    def set_min_coins(self, value):
        try:
            v = max(0, int(value))
        except Exception:
            v = 1
        self.min_coins = v
        self._log(f"min_coins = {v}")
        self._notify()

    def add_score(self, user, points, source="gift", avatar=None, display_name=None):
        """★ Cộng điểm + trừ máu boss (tập trung)."""
        # Chặn khi ván đã kết thúc
        if self.phase == Phase.FINISHED:
            self._log(f"⚠️ {user} +{points} skipped — phase FINISHED")
            return

        if points <= 0:
            return

        if avatar:
            self.set_avatar(user, avatar)
        if display_name:
            self.set_display_name(user, display_name)

        before = self.scores[user]
        self.scores[user] += points
        if self.scores[user] > before:
            self.first_reach[user] = time.time()

        self._log(f"{user} +{points} [{source}] (total {self.scores[user]})")

        # ★ Trừ máu boss — luôn chạy nếu boss còn sống
        if self.boss_alive:
            died = self.damage_boss(points)
            if died:
                self._log(
                    f"💀 Boss killed → +{self.get_boss_reward()} Robux "
                    f"(pot: {self.robux_pot})"
                )

        self._notify()

    def get_leaders(self):
        if not self.scores:
            return []
        qualified = {u: s for u, s in self.scores.items() if s >= self.min_coins}
        if not qualified:
            return []
        mx = max(qualified.values())
        return [u for u, s in qualified.items() if s == mx]

    def is_tie_at_top(self):
        return len(self.get_leaders()) > 1

    def tick(self):
        if self.phase in (Phase.IDLE, Phase.FINISHED) or self._stop_flag:
            return False
        cur = self.remaining()
        cur_sec = int(cur)
        if cur_sec != self._last_notify_sec:
            self._last_notify_sec = cur_sec
            self._notify()
        if cur > 0:
            return True

        if self.phase == Phase.MAIN:
            # ★ LUÔN vào SNAP 1 lần sau MAIN
            # Không cần hòa, không cần ≥ 2 người
            self._start_snap()

        elif self.phase == Phase.SNAP:
            # Auto Tie (nếu bật)
            self._apply_auto_tie()

            # ★ Nếu còn hòa → SNAP tiếp; nếu hết hòa → FINISHED
            if self.is_tie_at_top():
                self._start_snap()
            else:
                self._finish()
                return False
        return True

    def _start_snap(self):
        self.snap_count += 1
        self._enter_phase(Phase.SNAP, self.snap_duration)
        leaders = self.get_leaders()
        self._log(f"SNAP #{self.snap_count} – leaders: {leaders}")

    def _finish(self):
        leaders = self.get_leaders()
        if len(leaders) > 1:
            self.winner = min(leaders, key=lambda u: self.first_reach.get(u, 9e9))
            self._log(f"Tiebreak → {self.winner}")
        else:
            self.winner = leaders[0] if leaders else None
        self.phase = Phase.FINISHED
        self.last_winner_pot = self.robux_pot

        # Chốt last_winner + robux NGAY tại thời điểm finish
        if self.winner:
            self.last_winner = self.winner
            self.last_winner_display = self.display_names.get(
                self.winner, self.winner.lstrip("@")
            )
            self.last_winner_robux = self.robux_pot

        self._log(f"Winner: {self.winner} — {self.robux_pot} Robux")
        self._notify()

    def _schedule_auto_reset(self, delay=7.5):
        """★ Tự động reset boss + pot sau khi ván kết thúc."""
        import threading

        def _do_reset():
            time.sleep(delay)
            # Chỉ reset nếu phase vẫn FINISHED (chưa bắt đầu ván mới)
            if self.phase != Phase.FINISHED:
                return

            if self.auto_reset_boss:
                b = boss_data.get_boss_name(self.auto_reset_boss_level)
                self.boss_level = self.auto_reset_boss_level
                self.boss_hp = boss_data.get_hp(
                    self.boss_level, self.hp_base, self.hp_multiplier
                )
                self.boss_max_hp = self.boss_hp
                self.boss_alive = True
                self.boss_died_at = 0
                self._log(f"🔄 Auto reset boss → Lv.{self.boss_level} {b['name']}")

            if self.auto_reset_pot:
                self.robux_pot = self.reset_robux_value
                self._log(f"🔄 Auto reset pot → {self.robux_pot}")

            self._notify()

        t = threading.Thread(target=_do_reset, daemon=True)
        t.start()

    def set_auto_reset(self, boss=None, pot=None, boss_level=None):
        """★ Cập nhật config auto reset."""
        if boss is not None:
            self.auto_reset_boss = bool(boss)
        if pot is not None:
            self.auto_reset_pot = bool(pot)
        if boss_level is not None:
            self.auto_reset_boss_level = max(1, min(boss_level, boss_data.max_level()))
        self._log(
            f"Auto reset: boss={self.auto_reset_boss}, "
            f"pot={self.auto_reset_pot}, level={self.auto_reset_boss_level}"
        )
        self._notify()

    def balance_top2(self):
        if len(self.scores) >= 2:
            sorted_users = sorted(self.scores, key=lambda u: -self.scores[u])[:2]
            mx = max(self.scores[u] for u in sorted_users)
            for u in sorted_users:
                self.scores[u] = mx
                self.first_reach[u] = time.time()
        else:
            self.scores["@alice"] = 100
            self.scores["@bob"] = 100
            self.first_reach["@alice"] = time.time()
            self.first_reach["@bob"] = time.time()
        self._notify()

    def snapshot(self):
        # ★ Lấy top 3 bất kể min_coins
        all_sorted = sorted(self.scores.items(), key=lambda x: -x[1])
        top = all_sorted[:3]

        return {
            "phase": self.phase.value,
            "snap_count": self.snap_count,
            "remaining": round(self.remaining(), 1),
            "leaders": self.get_leaders(),   # vẫn lọc theo min_coins
            "is_tie": self.is_tie_at_top(),
            "min_coins": self.min_coins,
            "vouch": self.vouch,
            "auto_reset_boss": self.auto_reset_boss,
            "auto_reset_pot": self.auto_reset_pot,
            "auto_reset_boss_level": self.auto_reset_boss_level,
            "robux_pot": self.robux_pot,
            "reset_robux_value": self.reset_robux_value,
            "damage_flash": time.time() < self.damage_flash_until,
            "boss_died_at": self.boss_died_at,
            "top": [
                {
                    "user": u,
                    "display_name": self.display_names.get(u, u.lstrip("@")),
                    "score": s,
                    "avatar": self.avatars.get(u),
                    "qualified": s >= self.min_coins,   # ★ Đánh dấu đủ điều kiện
                }
                for u, s in top
            ],
            "winner": self.winner,
            "winner_display": self.display_names.get(self.winner, "") if self.winner else "",
            "main_duration": self.main_duration,
            "snap_duration": self.snap_duration,
            "boss": {
                "level": self.boss_level,
                "name": boss_data.get_boss_name(self.boss_level)["name"],
                "emoji": boss_data.get_boss_name(self.boss_level)["emoji"],
                "hp": self.boss_hp,
                "max_hp": self.boss_max_hp,
                "alive": self.boss_alive,
                "reward": self.get_boss_reward(),
                "killed_count": self.boss_killed_count,
                "gift_count": self.get_boss_gift_count(),
            },
        }

    def _log(self, msg):
        self.history.append({"t": time.time(), "msg": msg})
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")