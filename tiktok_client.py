"""TikTokLive client — Queue tuần tự, không chồng animation."""
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
                 on_gift: Callable[[str, int, str, str, str], None],
                 on_status: Callable[[str], None],
                 on_connected: Optional[Callable[[str], None]] = None,
                 retry_interval: int = 10,
                 combo_wait: float = 1.5,
                 animation_duration: float = 2.5):
        self.loop = loop
        self.on_gift = on_gift
        self.on_status = on_status
        self.on_connected = on_connected
        self.retry_interval = retry_interval
        self.combo_wait = combo_wait                # Đợi gom combo (1.5s)
        self.animation_duration = animation_duration  # Thời gian animation (2.5s)

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

                # ★ QUEUE — hàng đợi event
                _queue = asyncio.Queue()
                _seen_msg_ids = set()
                _worker_task = None

                # ═══════════════════════════════════════════════════
                # WORKER — lấy event từ queue, xử lý tuần tự
                # ═══════════════════════════════════════════════════
                async def _worker():
                    """Worker chạy liên tục, xử lý event tuần tự."""
                    print("[worker] Started")
                    while True:
                        try:
                            # Lấy event đầu tiên từ queue (block)
                            event_data = await _queue.get()

                            # ★ Gom combo: đợi 1.5s, nếu có event cùng key → gộp
                            key = event_data["key"]
                            count = event_data["repeat"]
                            last_event = event_data
                            deadline = time.time() + self.combo_wait

                            while True:
                                remaining = deadline - time.time()
                                if remaining <= 0:
                                    break
                                try:
                                    # Đợi event mới trong `remaining` giây
                                    next_event = await asyncio.wait_for(
                                        _queue.get(),
                                        timeout=remaining
                                    )
                                    # Nếu cùng key → gộp
                                    if next_event["key"] == key:
                                        count += next_event["repeat"]
                                        last_event = next_event
                                        # Reset deadline (chờ thêm 1.5s nữa)
                                        deadline = time.time() + self.combo_wait
                                        print(f"📦 COMBO MERGE: "
                                              f"{last_event['user']} "
                                              f"{last_event['gift_name']} × {count}")
                                    else:
                                        # Khác key → đẩy lại queue, thoát loop
                                        await _queue.put(next_event)
                                        break
                                except asyncio.TimeoutError:
                                    break

                            # ★ Gửi callback 1 lần
                            diamonds = last_event["diamonds"]
                            points = diamonds * count if diamonds > 0 else count

                            print(f"✅ SEND: {last_event['user']} "
                                  f"{last_event['gift_name']} × {count} "
                                  f"→ +{points} pts")

                            try:
                                self.on_gift(
                                    last_event["user"],
                                    points,
                                    last_event["avatar"],
                                    last_event["display_name"],
                                    last_event["gift_name"],
                                )
                            except Exception as e:
                                print(f"[on_gift callback] {e}")

                            # ★ Đợi animation xong trước khi xử lý event tiếp
                            await asyncio.sleep(self.animation_duration)

                            _queue.task_done()

                        except asyncio.CancelledError:
                            print("[worker] Cancelled")
                            break
                        except Exception as e:
                            print(f"[worker] Error: {e}")
                            import traceback
                            traceback.print_exc()

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
                        display_name = (
                            getattr(event.user, "nickname", "")
                            or getattr(event.user, "display_name", "")
                            or event.user.unique_id
                        )
                        gift = event.gift
                        gift_name = getattr(gift, "name", "Unknown")
                        gift_id = getattr(gift, "id", 0)
                        diamonds = getattr(gift, "diamond_count", 0) or 0
                        repeat = getattr(event, "repeat_count", 1) or 1

                        # Avatar
                        avatar_url = ""
                        try:
                            for attr in ["avatar_thumb", "avatar_medium", "avatar_larger"]:
                                obj = getattr(event.user, attr, None)
                                if obj:
                                    urls = getattr(obj, "url_list", None)
                                    if urls and isinstance(urls, list) and len(urls) > 0:
                                        avatar_url = urls[0]
                                        break
                                    elif urls and hasattr(urls, "url_list"):
                                        inner = urls.url_list
                                        if isinstance(inner, list) and len(inner) > 0:
                                            avatar_url = inner[0]
                                            break
                            if not avatar_url:
                                avatar_url = getattr(event.user, "avatar_url", "") or ""
                        except Exception as e:
                            print(f"[avatar] {e}")

                        # msg_id dedup
                        msg_id = None
                        try:
                            common = getattr(event, "common", None)
                            if common:
                                mid = getattr(common, "msg_id", None)
                                if mid:
                                    msg_id = str(mid)
                        except Exception:
                            pass

                        if msg_id:
                            if msg_id in _seen_msg_ids:
                                print(f"📦 SKIP (msg_id): {user} {gift_name}")
                                return
                            _seen_msg_ids.add(msg_id)
                            if len(_seen_msg_ids) > 10000:
                                _seen_msg_ids.clear()

                        # ★ Đẩy vào queue
                        key = (user, gift_id)
                        await _queue.put({
                            "key": key,
                            "user": user,
                            "display_name": display_name,
                            "avatar": avatar_url,
                            "gift_name": gift_name,
                            "gift_id": gift_id,
                            "diamonds": diamonds,
                            "repeat": repeat,
                        })

                        print(f"📥 QUEUE: {user} {gift_name} × {repeat} "
                              f"(queue size: {_queue.qsize()})")

                    except Exception as e:
                        print(f"[gift] error: {e}")
                        import traceback
                        traceback.print_exc()

                # Start worker
                _worker_task = asyncio.create_task(_worker())

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