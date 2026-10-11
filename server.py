"""WebSocket + HTTP server for 5 overlays."""
import asyncio
import hashlib
import json
import platform
import random
import socket
import uuid
from pathlib import Path

from aiohttp import web


DEVICE_FILE = Path.home() / ".tiktok_auction_device"


def get_device_id() -> str:
    if DEVICE_FILE.exists():
        try:
            dev = DEVICE_FILE.read_text().strip()
            if dev:
                return dev
        except Exception:
            pass
    raw = f"{platform.node()}-{uuid.getnode()}-{platform.machine()}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:20]
    sys_name = platform.system().lower() or "dev"
    dev_id = f"{sys_name}_{h}"
    try:
        DEVICE_FILE.write_text(dev_id)
    except Exception:
        pass
    return dev_id


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class OverlayServer:
    def __init__(self, engine, static_dir: Path, port=3000,
                 license_key="Tunchill", device_id=None):
        self.engine = engine
        self.static_dir = static_dir
        self.port = port
        self.license_key = license_key
        self.device_id = device_id or get_device_id()
        self.ws_clients = set()
        self.runner = None
        self._loop = None

    # ============ URL BUILDERS ============
    def _base_url(self, host, path):
        return (
            f"http://{host}:{self.port}/{path}"
            f"?key={self.license_key}"
            f"&deviceId={self.device_id}"
            f"&isWidget=true"
        )

    def build_widget_url(self, host="localhost"):
        return self._base_url(host, "widget.html")

    def build_cmt_url(self, host="localhost"):
        return self._base_url(host, "cmt.html")

    def build_gift_fx_url(self, host="localhost"):
        return self._base_url(host, "gift-fx.html")

    def build_gift_text_url(self, host="localhost"):
        return self._base_url(host, "gift-text.html")

    def build_vtuber_url(self, host="localhost"):
        return self._base_url(host, "vtuber.html")

    def build_all_urls(self, host="localhost"):
        return {
            "widget":    self.build_widget_url(host),
            "cmt":       self.build_cmt_url(host),
            "gift_fx":   self.build_gift_fx_url(host),
            "gift_text": self.build_gift_text_url(host),
            "vtuber":    self.build_vtuber_url(host),
        }

    def build_all_local(self):
        return self.build_all_urls("localhost")

    def build_all_lan(self):
        return self.build_all_urls(get_lan_ip())

    # ============ BROADCAST ============
    async def broadcast(self, data=None):
        if data is None:
            data = {"type": "state", "data": self.engine.snapshot()}
        elif "type" not in data:
            data = {"type": "state", "data": data}

        if not self.ws_clients:
            return
        msg = json.dumps(data)
        dead = []
        for ws in list(self.ws_clients):
            try:
                await ws.send_str(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.ws_clients.discard(ws)

    async def send_event(self, event_type: str, payload: dict):
        if not self.ws_clients:
            return
        msg = json.dumps({"type": event_type, "data": payload})
        dead = []
        for ws in list(self.ws_clients):
            try:
                await ws.send_str(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.ws_clients.discard(ws)

    def broadcast_sync(self, data=None):
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(data), self._loop)

    def send_event_sync(self, event_type: str, payload: dict):
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(
            self.send_event(event_type, payload), self._loop
        )

    # ============ HANDLERS ============
    async def _widget(self, request):
        return web.FileResponse(self.static_dir / "overlay.html")

    async def _cmt(self, request):
        return web.FileResponse(self.static_dir / "cmt.html")

    async def _gift_fx(self, request):
        return web.FileResponse(self.static_dir / "gift-fx.html")

    async def _gift_text(self, request):
        return web.FileResponse(self.static_dir / "gift-text.html")

    async def _vtuber(self, request):
        return web.FileResponse(
            self.static_dir / "vtuber" / "vtuber.html"
        )

    async def _ws_handler(self, request):
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        self.ws_clients.add(ws)
        print(f"🔌 Client connected ({len(self.ws_clients)})")
        try:
            await ws.send_str(json.dumps({
                "type": "state",
                "data": self.engine.snapshot()
            }))
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("type") == "vtuber_volume":
                            await self.send_event(
                                "vtuber_volume", data.get("data", {})
                            )
                    except Exception:
                        pass
        finally:
            self.ws_clients.discard(ws)
            print(f"🔌 Client disconnected ({len(self.ws_clients)})")
        return ws

    async def send_event(self, event_type: str, payload: dict):
        if not self.ws_clients:
            return

        msg = json.dumps({"type": event_type, "data": payload})
        dead = []

        for ws in list(self.ws_clients):
            try:
                await ws.send_str(msg)
            except Exception as e:
                print(f"❌ send_event error: {e}")
                dead.append(ws)

        for ws in dead:
            self.ws_clients.discard(ws)

        # ★ Chỉ log event quan trọng (không log vtuber_volume)
        if event_type != "vtuber_volume":
            print(f"📤 send_event '{event_type}' → {len(self.ws_clients)} client(s)")

    async def _state(self, request):
        return web.json_response(self.engine.snapshot())

    async def _health(self, request):
        return web.json_response({
            "ok": True,
            "clients": len(self.ws_clients),
            "lan_ip": get_lan_ip(),
            "device_id": self.device_id,
            "key": self.license_key,
            "urls_local": self.build_all_local(),
            "urls_lan": self.build_all_lan(),
        })

    async def _ping(self, request):
        return web.Response(text="pong")

    # ============ GIFT ASSETS SCAN ============
    async def _gifts_list(self, request):
        icons_dir = self.static_dir / "assets" / "gift-icons"
        effects_dir = self.static_dir / "assets" / "gift-effects"

        icons = {}
        effects = {}

        if icons_dir.exists():
            icon_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
            for f in icons_dir.iterdir():
                if not f.is_file():
                    continue
                if f.suffix.lower() not in icon_exts:
                    continue
                stem = f.stem.lower()
                if stem not in icons:
                    icons[stem] = f.name

        if effects_dir.exists():
            priority = {
                ".webm": ("video", 1),
                ".mp4":  ("video", 2),
                ".gif":  ("gif",   3),
                ".json": ("lottie", 4),
            }
            by_stem = {}
            for f in effects_dir.iterdir():
                if not f.is_file():
                    continue
                ext = f.suffix.lower()
                if ext not in priority:
                    continue
                stem = f.stem.lower()
                media_type, prio = priority[ext]
                if stem not in by_stem or prio < by_stem[stem][0]:
                    by_stem[stem] = (prio, f.name, media_type)

            for stem, (_, fname, mtype) in by_stem.items():
                effects[stem] = {"file": fname, "type": mtype}

        return web.json_response({
            "icons": icons,
            "effects": effects,
        })

    # ============ BOT AVATARS ============
    async def _bot_avatars(self, request):
        """Trả về danh sách avatar bot có sẵn."""
        avatars_dir = self.static_dir / "assets" / "bots" / "avatars"
        avatars = []
        if avatars_dir.exists():
            exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
            for f in avatars_dir.iterdir():
                if f.is_file() and f.suffix.lower() in exts:
                    avatars.append(f.name)
        return web.json_response({"avatars": sorted(avatars)})

    # ============ LIFECYCLE ============
    async def start(self):
        self._loop = asyncio.get_running_loop()
        app = web.Application()

        app.router.add_get("/widget.html", self._widget)
        app.router.add_get("/overlay", self._widget)
        app.router.add_get("/cmt.html", self._cmt)
        app.router.add_get("/gift-fx.html", self._gift_fx)
        app.router.add_get("/gift-text.html", self._gift_text)
        app.router.add_get("/vtuber.html", self._vtuber)

        app.router.add_get("/ws", self._ws_handler)
        app.router.add_get("/api/state", self._state)
        app.router.add_get("/api/health", self._health)
        app.router.add_get("/api/gifts/list", self._gifts_list)
        app.router.add_get("/api/bots/avatars", self._bot_avatars)
        app.router.add_get("/ping", self._ping)
        app.router.add_static("/static/", self.static_dir)

        @web.middleware
        async def cors_middleware(request, handler):
            if request.method == "OPTIONS":
                resp = web.Response()
            else:
                resp = await handler(request)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            return resp

        app.middlewares.append(cors_middleware)

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await site.start()

        print("=" * 70)
        print("🌐 OVERLAY SERVER RUNNING — Port:", self.port)
        print(f"   Device ID: {self.device_id}")
        print("=" * 70)

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()