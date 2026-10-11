"""Auction engine - no UI dependency."""
import time
from collections import defaultdict
from enum import Enum


class Phase(Enum):
    IDLE = "idle"
    MAIN = "main"
    SNAP = "snap"
    FINISHED = "finished"


class AuctionEngine:
    def __init__(self, main_duration=60, snap_duration=30):
        self.scores = defaultdict(int)
        self.first_reach = {}
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
        self.snap_count = 0
        self.winner = None
        self.history.clear()
        self._stop_flag = False
        self._enter_phase(Phase.MAIN, self.main_duration)
        self._log(f"▶ Main round started ({self.main_duration}s)")

    def stop(self):
        self._stop_flag = True
        self.phase = Phase.FINISHED
        self._log("⏹ Stopped manually")
        self._notify()

    def reset(self):
        self.scores.clear()
        self.first_reach.clear()
        self.snap_count = 0
        self.winner = None
        self.history.clear()
        self.phase = Phase.IDLE
        self._stop_flag = False
        self._log("🔄 Reset")
        self._notify()

    def _enter_phase(self, phase, duration):
        self.phase = phase
        self.phase_start = time.time()
        self.phase_duration = duration
        self._log(f"→ Phase {phase.value}, {duration}s")
        self._notify()

    def remaining(self):
        if self.phase in (Phase.IDLE, Phase.FINISHED):
            return 0
        return max(0, self.phase_duration - (time.time() - self.phase_start))

    def add_score(self, user, points, source="gift"):
        if self.phase not in (Phase.MAIN, Phase.SNAP):
            return

        # ★ Bỏ qua nếu points <= 0
        if points <= 0:
            self._log(f"⚠️ {user} gift {source} has {points} pts — skipped")
            return

        before = self.scores[user]
        self.scores[user] += points
        if self.scores[user] > before:
            self.first_reach[user] = time.time()
        self._log(f"{user} +{points} [{source}] (total {self.scores[user]})")
        self._notify()

    def get_leaders(self):
        if not self.scores:
            return []
        mx = max(self.scores.values())
        return [u for u, s in self.scores.items() if s == mx]

    def is_tie_at_top(self):
        return len(self.get_leaders()) > 1

    def tick(self):
        if self.phase in (Phase.IDLE, Phase.FINISHED) or self._stop_flag:
            return False
        cur = self.remaining()
        self._notify()
        if cur > 0:
            return True

        if self.phase == Phase.MAIN:
            if self.is_tie_at_top():
                self._start_snap()
            else:
                self._finish()
                return False
        elif self.phase == Phase.SNAP:
            if self.is_tie_at_top():
                self._start_snap()
            else:
                self._finish()
                return False
        return True

    def _start_snap(self):
        """★ Tất cả snap đều có cùng thời gian (không giảm dần)."""
        self.snap_count += 1
        duration = self.snap_duration
        self._enter_phase(Phase.SNAP, duration)
        leaders = self.get_leaders()
        self._log(
            f"⚡ SNAP TIME #{self.snap_count} – {duration}s – "
            f"tie: {leaders}"
        )

    def _finish(self):
        leaders = self.get_leaders()
        if len(leaders) > 1:
            self.winner = min(leaders, key=lambda u: self.first_reach.get(u, 9e9))
            self._log(f"Tiebreak → {self.winner}")
        else:
            self.winner = leaders[0] if leaders else None
        self.phase = Phase.FINISHED
        self._log(f"🏆 Winner: {self.winner}")
        self._notify()

    def balance_top2(self):
        if len(self.scores) >= 2:
            sorted_users = sorted(
                self.scores, key=lambda u: -self.scores[u]
            )[:2]
            mx = max(self.scores[u] for u in sorted_users)
            for u in sorted_users:
                self.scores[u] = mx
                self.first_reach[u] = time.time()
            self._log(f"⚖ Balanced top 2: {sorted_users} = {mx}")
        else:
            self.scores["@alice"] = 100
            self.scores["@bob"] = 100
            self.first_reach["@alice"] = time.time()
            self.first_reach["@bob"] = time.time()
            self._log("⚖ Balanced (created @alice vs @bob = 100)")
        self._notify()

    def snapshot(self):
        top = sorted(self.scores.items(), key=lambda x: -x[1])[:3]
        return {
            "phase": self.phase.value,
            "snap_count": self.snap_count,
            "remaining": round(self.remaining(), 1),
            "leaders": self.get_leaders(),
            "is_tie": self.is_tie_at_top(),
            "top": [{"user": u, "score": s} for u, s in top],
            "winner": self.winner,
            "main_duration": self.main_duration,
            "snap_duration": self.snap_duration,
        }

    def _log(self, msg):
        self.history.append({"t": time.time(), "msg": msg})
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")