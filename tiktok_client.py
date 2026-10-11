"""TikTokLive client — dedup thông minh cho combo."""
import asyncio
import re
import time
from typing import Callable, Optional


def normalize_live_id(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("http"):
        m = re.search(r"@([\w\.]+)", raw)
        if m:
            return f"@{m.group(1)}"
        m = re.search(r"/live/(\d+)", raw)
        if m:
            return m.group(1)
    if not raw.startswith("@"):
        raw = "@" + raw
    return raw


class TikTokLiveRunner:
    def __init__(self, loop,
                 on_gift: Callable[[str, int], None],
                 on_status: Callable[[str], None],
                 on_connected: Optional[Callable[[str], None]] = None,
                 retry_interval: int = 10):
        self.loop = loop
        self.on_gift = on_gift
        self.on_status = on_status
        self.on_connected = on_connected
        self.retry_interval = retry_interval

        self.client = None
        self._connected = False
        self._waiting = False
        self._stop_wait = False
        self._current_id = ""

    async def connect(self, raw_id: str, retry: bool = True):
        try:
            from TikTokLive import TikTokLiveClient
            from TikTokLive.events import (
                GiftEvent, ConnectEvent, DisconnectEvent
            )
        except ImportError as e:
            self.on_status(f"❌ TikTokLive not installed: {e}")
            return

        UserOfflineError = None
        try:
            from TikTokLive.client.errors import UserOfflineError
        except ImportError:
            pass

        unique_id = normalize_live_id(raw_id)
        if not unique_id:
            self.on_status("❌ Empty username/link")
            return

        self._current_id = unique_id
        self._stop_wait = False
        self._waiting = True

        attempt = 0
        while not self._stop_wait:
            attempt += 1
            if attempt == 1:
                self.on_status(f"⏳ Connecting to {unique_id} ...")
            else:
                self.on_status(
                    f"⏳ Waiting for {unique_id} to go live "
                    f"(attempt #{attempt}) ..."
                )

            try:
                client = TikTokLiveClient(unique_id=unique_id)

                # ============================================================
                # ★ STATE cho dedup thông minh
                # Lưu trạng thái theo (user, gift_id):
                #   - last_repeat: repeat_count lần trước
                #   - last_time: thời điểm nhận
                #   - total_repeat: tổng số đã cộng
                #
                # Logic:
                #   - Nếu repeat_count == last_repeat (trong 6s) → SKIP (dup)
                #   - Nếu repeat_count > last_repeat → cộng phần chênh lệch
                #   - Nếu repeat_count < last_repeat → reset (user tặng lại từ đầu)
                # ============================================================
                _gift_state = {}   # {(user, gift_id): {"repeat": int, "time": float, "counted": int}}
                _lock = asyncio.Lock()

                @client.on(ConnectEvent)
                async def _on_connect(event):
                    self._connected = True
                    self._waiting = False
                    self.on_status(f"✅ Connected: {unique_id}")
                    if self.on_connected:
                        try:
                            self.on_connected(unique_id)
                        except Exception as e:
                            print(f"[on_connected] {e}")

                @client.on(DisconnectEvent)
                async def _on_disconnect(event):
                    self._connected = False
                    self.on_status("⚠️ TikTok Live disconnected")

                @client.on(GiftEvent)
                async def _on_gift(event):
                    try:
                        user = "@" + event.user.unique_id
                        gift = event.gift
                        gift_name = getattr(gift, "name", "Unknown")
                        gift_id = getattr(gift, "id", 0)
                        diamonds = getattr(gift, "diamond_count", 0) or 0
                        repeat = getattr(event, "repeat_count", 1) or 1

                        key = (user, gift_id)
                        now = time.time()

                        async with _lock:
                            state = _gift_state.get(key)

                            # Lần đầu nhận quà này
                            if state is None:
                                _gift_state[key] = {
                                    "repeat": repeat,
                                    "time": now,
                                    "counted": repeat,
                                }
                                points_to_add = repeat * (diamonds if diamonds > 0 else 1)

                                print(f"📦 GIFT NEW: {user} sent "
                                      f"{gift_name} x{repeat} → +{points_to_add} pts")
                                self.on_gift(user, points_to_add)
                                return

                            # Đã có state trước
                            last_repeat = state["repeat"]
                            last_time = state["time"]
                            time_diff = now - last_time

                            # ★ Case 1: repeat_count GIỐNG HỆT trong 6s → DUP
                            if repeat == last_repeat and time_diff < 6.0:
                                print(f"📦 SKIP DUP: {user} {gift_name} "
                                      f"x{repeat} (cách {time_diff:.1f}s)")
                                return

                            # ★ Case 2: repeat_count TĂNG (combo) → cộng chênh lệch
                            if repeat > last_repeat:
                                diff = repeat - last_repeat
                                points_to_add = diff * (diamonds if diamonds > 0 else 1)
                                state["repeat"] = repeat
                                state["time"] = now
                                state["counted"] += diff

                                print(f"📦 GIFT COMBO: {user} {gift_name} "
                                      f"x{repeat} (+{diff}) → +{points_to_add} pts")
                                self.on_gift(user, points_to_add)
                                return

                            # ★ Case 3: repeat_count GIẢM (user tặng lại mới) → reset
                            if repeat < last_repeat:
                                # Kiểm tra thêm: nếu cách > 2s thì coi là tặng mới
                                state["repeat"] = repeat
                                state["time"] = now
                                state["counted"] += repeat

                                points_to_add = repeat * (diamonds if diamonds > 0 else 1)

                                print(f"📦 GIFT RESET: {user} {gift_name} "
                                      f"x{repeat} → +{points_to_add} pts")
                                self.on_gift(user, points_to_add)
                                return

                    except Exception as e:
                        print(f"[gift] error: {e}")
                        import traceback
                        traceback.print_exc()

                self.client = client
                await client.connect()
                return

            except Exception as e:
                err = str(e).lower()
                is_offline = (
                    (UserOfflineError and isinstance(e, UserOfflineError))
                    or "offline" in err
                    or "not live" in err
                    or "is not live" in err
                )

                if not is_offline:
                    self.on_status(f"❌ Connection error: {e}")
                    self._waiting = False
                    self._connected = False
                    return

                if not retry or self._stop_wait:
                    self.on_status(
                        f"❌ {unique_id} is not live. "
                        f"Go live and click CONNECT again."
                    )
                    self._waiting = False
                    return

                for _ in range(self.retry_interval):
                    if self._stop_wait:
                        break
                    await asyncio.sleep(1)

                if self._stop_wait:
                    self.on_status("⏹ Stopped waiting")
                    self._waiting = False
                    return

    def stop_waiting(self):
        self._stop_wait = True
        self._waiting = False

    async def disconnect(self):
        self.stop_waiting()
        if self.client:
            try:
                await self.client.disconnect()
            except Exception:
                pass
        self.client = None
        self._connected = False
        self.on_status("⛔ Disconnected")

    @property
    def connected(self):
        return self._connected

    @property
    def waiting(self):
        return self._waiting