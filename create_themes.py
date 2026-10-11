"""
Tool tạo 40 theme sặc sỡ, chi tiết, có chiều sâu.
Chạy: uv run python create_themes.py
"""
from pathlib import Path
import json


BASE = Path(__file__).parent / "themes"


# ============================================================
# 40 THEME — Mỗi theme có config + CSS riêng
# ============================================================
THEMES = {

    # ═══════════════════════════════════════════════════════
    # 1. HALLOWEEN
    # ═══════════════════════════════════════════════════════
    "halloween": {
        "config": {
            "title": "HALLOWEEN AUCTION",
            "logo": "🎃",
            "deco_text": "HAPPY HALLOWEEN",
            "deco_left": "🧙", "deco_right": "🧹",
            "winner_hat": "🧙",
            "marquee": [
                "🎃 Trick or Treat", "🦇 Spooky Vibes", "🎃 Boo!",
                "🧙 Happy Halloween", "👻 Halloween Night",
                "🍬 Candy Time", "🕷 Spider Web",
            ],
            "particles": ["#ff8000", "#ffcc00", "#a020f0", "#ff5500"],
            "decorations": [
                {"class": "bat", "emoji": "🦇", "top": "12%", "left": "3%", "size": "42px"},
                {"class": "pumpkin", "emoji": "🎃", "bottom": "8%", "left": "3%", "size": "50px"},
                {"class": "ghost", "emoji": "👻", "top": "25%", "right": "5%", "size": "38px"},
                {"class": "spider", "emoji": "🕷", "top": "55%", "left": "4%", "size": "36px"},
            ],
        },
        "css": {
            "c1": "#ff8000", "c2": "#ffcc00", "c3": "#ff5500",
            "c4": "#a020f0", "c5": "#7c3aed", "c_bg": "#1a0828",
            "grad1": "rgba(30,8,40,0.92)", "grad2": "rgba(55,12,70,0.92)",
            "grad3": "rgba(18,4,28,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 2. CHRISTMAS
    # ═══════════════════════════════════════════════════════
    "christmas": {
        "config": {
            "title": "CHRISTMAS AUCTION",
            "logo": "🎄",
            "deco_text": "MERRY CHRISTMAS",
            "deco_left": "🎅", "deco_right": "🦌",
            "winner_hat": "🎅",
            "marquee": [
                "🎄 Merry Christmas", "🎁 Ho Ho Ho", "❄️ Let it Snow",
                "🔔 Jingle Bells", "⛄ Frosty", "🌟 Star of Wonder",
            ],
            "particles": ["#ff3333", "#ffffff", "#00cc66", "#ffcc00"],
            "decorations": [
                {"class": "snow", "emoji": "❄️", "top": "10%", "left": "20%", "size": "30px"},
                {"class": "tree", "emoji": "🎄", "bottom": "5%", "left": "3%", "size": "60px"},
                {"class": "gift", "emoji": "🎁", "bottom": "5%", "right": "3%", "size": "50px"},
                {"class": "bell", "emoji": "🔔", "top": "30%", "right": "4%", "size": "42px"},
            ],
        },
        "css": {
            "c1": "#ff3333", "c2": "#ffffff", "c3": "#00cc66",
            "c4": "#ffcc00", "c5": "#c41e3a", "c_bg": "#0a1f10",
            "grad1": "rgba(10,30,20,0.92)", "grad2": "rgba(15,60,40,0.92)",
            "grad3": "rgba(5,20,15,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 3. TẾT
    # ═══════════════════════════════════════════════════════
    "tet": {
        "config": {
            "title": "TẾT AUCTION",
            "logo": "🧧",
            "deco_text": "CHÚC MỪNG NĂM MỚI",
            "deco_left": "🏮", "deco_right": "🌸",
            "winner_hat": "🧧",
            "marquee": [
                "🧧 Chúc Mừng Năm Mới", "🌸 Hoa Mai", "🏮 Lì Xì",
                "🐉 Rồng Vàng", "🎊 Tết Sum Vầy", "🍀 An Khang",
            ],
            "particles": ["#ffcc00", "#ff5500", "#ff0033", "#ffaa00"],
            "decorations": [
                {"class": "lantern", "emoji": "🏮", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "flower", "emoji": "🌸", "bottom": "8%", "left": "3%", "size": "40px"},
                {"class": "envelope", "emoji": "🧧", "bottom": "8%", "right": "3%", "size": "50px"},
                {"class": "dragon", "emoji": "🐉", "top": "40%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ffcc00", "c2": "#ff5500", "c3": "#ff0033",
            "c4": "#ffaa00", "c5": "#8b0000", "c_bg": "#3d0a0a",
            "grad1": "rgba(80,10,10,0.92)", "grad2": "rgba(120,20,20,0.92)",
            "grad3": "rgba(60,5,5,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 4. VALENTINE
    # ═══════════════════════════════════════════════════════
    "valentine": {
        "config": {
            "title": "VALENTINE AUCTION",
            "logo": "💝",
            "deco_text": "BE MY VALENTINE",
            "deco_left": "🌹", "deco_right": "💕",
            "winner_hat": "💝",
            "marquee": [
                "💝 Happy Valentine", "🌹 Love is in the air",
                "💕 Kiss me", "💖 Sweet Heart", "💌 Love Letter",
            ],
            "particles": ["#ff6b9d", "#ff0055", "#ffb3cc", "#ff3366"],
            "decorations": [
                {"class": "heart", "emoji": "💖", "top": "10%", "left": "5%", "size": "40px"},
                {"class": "rose", "emoji": "🌹", "bottom": "8%", "left": "3%", "size": "50px"},
                {"class": "kiss", "emoji": "💋", "top": "25%", "right": "5%", "size": "40px"},
                {"class": "ring", "emoji": "💍", "bottom": "10%", "right": "4%", "size": "42px"},
            ],
        },
        "css": {
            "c1": "#ff6b9d", "c2": "#ff0055", "c3": "#ffb3cc",
            "c4": "#ff3366", "c5": "#c70039", "c_bg": "#3d0820",
            "grad1": "rgba(80,10,40,0.92)", "grad2": "rgba(120,20,60,0.92)",
            "grad3": "rgba(60,5,30,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 5. GAMING
    # ═══════════════════════════════════════════════════════
    "gaming": {
        "config": {
            "title": "GAMING AUCTION",
            "logo": "🎮",
            "deco_text": "GAME ON",
            "deco_left": "🎮", "deco_right": "🎯",
            "winner_hat": "🎮",
            "marquee": [
                "🎮 Game On", "🏆 GG WP", "⚡ Ready Player One",
                "🎯 Victory Royale", "🕹 Level Up", "💥 Headshot",
            ],
            "particles": ["#00ccff", "#7c5cff", "#00ff88", "#ff00ff"],
            "decorations": [
                {"class": "pad", "emoji": "🎮", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "target", "emoji": "🎯", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "joystick", "emoji": "🕹", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "trophy", "emoji": "🏆", "bottom": "10%", "right": "5%", "size": "46px"},
            ],
        },
        "css": {
            "c1": "#00ccff", "c2": "#7c5cff", "c3": "#00ff88",
            "c4": "#ff00ff", "c5": "#0055ff", "c_bg": "#0a0f1e",
            "grad1": "rgba(10,15,30,0.92)", "grad2": "rgba(20,30,60,0.92)",
            "grad3": "rgba(5,10,20,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 6. NEON
    # ═══════════════════════════════════════════════════════
    "neon": {
        "config": {
            "title": "NEON AUCTION",
            "logo": "🌃",
            "deco_text": "NEON NIGHTS",
            "deco_left": "⚡", "deco_right": "💜",
            "winner_hat": "🌃",
            "marquee": [
                "🌃 Neon Nights", "⚡ Cyberpunk", "💜 Synth Wave",
                "🎵 Retrowave", "✨ Glow Up", "🌆 Midnight City",
            ],
            "particles": ["#ff00ff", "#00ffff", "#ff0080", "#8800ff"],
            "decorations": [
                {"class": "bolt", "emoji": "⚡", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "heart", "emoji": "💜", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "star", "emoji": "✨", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "city", "emoji": "🌆", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ff00ff", "c2": "#00ffff", "c3": "#ff0080",
            "c4": "#8800ff", "c5": "#0080ff", "c_bg": "#140028",
            "grad1": "rgba(20,0,40,0.92)", "grad2": "rgba(60,0,90,0.92)",
            "grad3": "rgba(10,0,20,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 7. SAKURA
    # ═══════════════════════════════════════════════════════
    "sakura": {
        "config": {
            "title": "SAKURA AUCTION",
            "logo": "🌸",
            "deco_text": "SAKURA SEASON",
            "deco_left": "🌸", "deco_right": "🍃",
            "winner_hat": "🌸",
            "marquee": [
                "🌸 Sakura Season", "🍃 Cherry Blossom", "🌸 Spring Time",
                "✨ Peaceful", "🎋 Japan Vibes",
            ],
            "particles": ["#ffb3cc", "#ff80aa", "#ffd1e0", "#ffe0eb"],
            "decorations": [
                {"class": "blossom", "emoji": "🌸", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "blossom2", "emoji": "🌸", "bottom": "8%", "left": "3%", "size": "40px"},
                {"class": "leaf", "emoji": "🍃", "top": "25%", "right": "5%", "size": "40px"},
                {"class": "temple", "emoji": "⛩", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ffb3cc", "c2": "#ff80aa", "c3": "#ffd1e0",
            "c4": "#ffe0eb", "c5": "#e6a4b4", "c_bg": "#3d1525",
            "grad1": "rgba(50,20,35,0.92)", "grad2": "rgba(80,35,55,0.92)",
            "grad3": "rgba(40,15,25,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 8. DRAGON BALL
    # ═══════════════════════════════════════════════════════
    "dragon": {
        "config": {
            "title": "DRAGON AUCTION",
            "logo": "🐉",
            "deco_text": "DRAGON BALL",
            "deco_left": "🐉", "deco_right": "⚡",
            "winner_hat": "🐉",
            "marquee": [
                "🐉 Dragon Ball", "⚡ Super Saiyan", "🔥 Kamehameha",
                "⭐ 7 Dragon Balls", "💥 Power Level", "🌟 Ultra Instinct",
            ],
            "particles": ["#ffcc00", "#ff5500", "#ffaa00", "#ff8800"],
            "decorations": [
                {"class": "dragon", "emoji": "🐉", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "bolt", "emoji": "⚡", "bottom": "8%", "left": "3%", "size": "46px"},
                {"class": "fire", "emoji": "🔥", "top": "25%", "right": "5%", "size": "46px"},
                {"class": "star", "emoji": "⭐", "bottom": "10%", "right": "5%", "size": "46px"},
            ],
        },
        "css": {
            "c1": "#ffcc00", "c2": "#ff5500", "c3": "#ffaa00",
            "c4": "#ff8800", "c5": "#cc4400", "c_bg": "#3d1e00",
            "grad1": "rgba(60,30,0,0.92)", "grad2": "rgba(100,60,0,0.92)",
            "grad3": "rgba(40,20,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 9. OCEAN
    # ═══════════════════════════════════════════════════════
    "ocean": {
        "config": {
            "title": "OCEAN AUCTION",
            "logo": "🌊",
            "deco_text": "DEEP OCEAN",
            "deco_left": "🌊", "deco_right": "🐠",
            "winner_hat": "🌊",
            "marquee": [
                "🌊 Deep Ocean", "🐠 Under The Sea", "🐚 Ocean Vibes",
                "🦈 Jaws", "💧 Aqua", "🐙 Deep Blue",
            ],
            "particles": ["#00ccff", "#00ffcc", "#0088ff", "#00ddff"],
            "decorations": [
                {"class": "wave", "emoji": "🌊", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "fish", "emoji": "🐠", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "shell", "emoji": "🐚", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "shark", "emoji": "🦈", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#00ccff", "c2": "#00ffcc", "c3": "#0088ff",
            "c4": "#00ddff", "c5": "#0055aa", "c_bg": "#001e3d",
            "grad1": "rgba(0,30,60,0.92)", "grad2": "rgba(0,60,120,0.92)",
            "grad3": "rgba(0,20,40,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 10. FOREST
    # ═══════════════════════════════════════════════════════
    "forest": {
        "config": {
            "title": "FOREST AUCTION",
            "logo": "🌲",
            "deco_text": "WILD FOREST",
            "deco_left": "🌲", "deco_right": "🦌",
            "winner_hat": "🌲",
            "marquee": [
                "🌲 Wild Forest", "🦌 Nature Vibes", "🍃 Green Life",
                "🐺 Wild Pack", "🌿 Jungle", "🐻 Bear Cave",
            ],
            "particles": ["#88ff88", "#44cc44", "#aaffaa", "#66dd66"],
            "decorations": [
                {"class": "tree", "emoji": "🌲", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "leaf", "emoji": "🍃", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "deer", "emoji": "🦌", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "wolf", "emoji": "🐺", "bottom": "10%", "right": "5%", "size": "46px"},
            ],
        },
        "css": {
            "c1": "#88ff88", "c2": "#44cc44", "c3": "#aaffaa",
            "c4": "#66dd66", "c5": "#226622", "c_bg": "#0a2810",
            "grad1": "rgba(10,40,15,0.92)", "grad2": "rgba(20,70,30,0.92)",
            "grad3": "rgba(5,25,10,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 11. SUNSET
    # ═══════════════════════════════════════════════════════
    "sunset": {
        "config": {
            "title": "SUNSET AUCTION",
            "logo": "🌅",
            "deco_text": "GOLDEN SUNSET",
            "deco_left": "🌅", "deco_right": "🌇",
            "winner_hat": "🌅",
            "marquee": [
                "🌅 Golden Sunset", "🌇 Orange Sky", "☀️ Sunset Vibes",
                "🌆 Dusk", "🌉 Twilight", "🎨 Colorful Sky",
            ],
            "particles": ["#ff9933", "#ff3366", "#ffcc66", "#ff6633"],
            "decorations": [
                {"class": "sun", "emoji": "☀️", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "skyline", "emoji": "🌇", "bottom": "8%", "left": "3%", "size": "50px"},
                {"class": "city", "emoji": "🌆", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "bridge", "emoji": "🌉", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ff9933", "c2": "#ff3366", "c3": "#ffcc66",
            "c4": "#ff6633", "c5": "#cc4400", "c_bg": "#3d1400",
            "grad1": "rgba(60,20,0,0.92)", "grad2": "rgba(120,50,0,0.92)",
            "grad3": "rgba(40,10,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 12. NIGHT / MOON
    # ═══════════════════════════════════════════════════════
    "night": {
        "config": {
            "title": "NIGHT AUCTION",
            "logo": "🌙",
            "deco_text": "MOONLIGHT",
            "deco_left": "🌙", "deco_right": "⭐",
            "winner_hat": "🌙",
            "marquee": [
                "🌙 Moonlight", "⭐ Starry Night", "🌌 Milky Way",
                "✨ Twinkle", "🌠 Shooting Star",
            ],
            "particles": ["#aaccff", "#ffee88", "#88aaff", "#ffffff"],
            "decorations": [
                {"class": "moon", "emoji": "🌙", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "star", "emoji": "⭐", "bottom": "8%", "left": "3%", "size": "40px"},
                {"class": "sparkle", "emoji": "✨", "top": "25%", "right": "5%", "size": "40px"},
                {"class": "galaxy", "emoji": "🌌", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#aaccff", "c2": "#ffee88", "c3": "#88aaff",
            "c4": "#ffffff", "c5": "#5566cc", "c_bg": "#050514",
            "grad1": "rgba(5,5,20,0.92)", "grad2": "rgba(15,10,50,0.92)",
            "grad3": "rgba(2,2,10,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 13. GALAXY
    # ═══════════════════════════════════════════════════════
    "galaxy": {
        "config": {
            "title": "GALAXY AUCTION",
            "logo": "🌌",
            "deco_text": "INTERSTELLAR",
            "deco_left": "🌌", "deco_right": "🚀",
            "winner_hat": "🌌",
            "marquee": [
                "🌌 Interstellar", "🚀 To The Moon", "⭐ Cosmic",
                "🪐 Saturn", "💫 Space Time", "👽 Aliens",
            ],
            "particles": ["#cc88ff", "#66ddff", "#ff88cc", "#aa88ff"],
            "decorations": [
                {"class": "galaxy", "emoji": "🌌", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "rocket", "emoji": "🚀", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "planet", "emoji": "🪐", "top": "25%", "right": "5%", "size": "50px"},
                {"class": "comet", "emoji": "☄️", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#cc88ff", "c2": "#66ddff", "c3": "#ff88cc",
            "c4": "#aa88ff", "c5": "#5555cc", "c_bg": "#140032",
            "grad1": "rgba(20,0,50,0.92)", "grad2": "rgba(60,0,120,0.92)",
            "grad3": "rgba(10,0,25,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 14. FIRE
    # ═══════════════════════════════════════════════════════
    "fire": {
        "config": {
            "title": "FIRE AUCTION",
            "logo": "🔥",
            "deco_text": "BURNING UP",
            "deco_left": "🔥", "deco_right": "💥",
            "winner_hat": "🔥",
            "marquee": [
                "🔥 Burning Up", "💥 Explosion", "🌋 Volcano",
                "⚡ Lightning", "🚒 Fire Force", "♨️ Hot Stuff",
            ],
            "particles": ["#ff5500", "#ffcc00", "#ff2200", "#ff8800"],
            "decorations": [
                {"class": "fire", "emoji": "🔥", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "boom", "emoji": "💥", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "bolt", "emoji": "⚡", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "volcano", "emoji": "🌋", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ff5500", "c2": "#ffcc00", "c3": "#ff2200",
            "c4": "#ff8800", "c5": "#aa2200", "c_bg": "#3d0a00",
            "grad1": "rgba(60,5,0,0.92)", "grad2": "rgba(120,20,0,0.92)",
            "grad3": "rgba(40,0,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 15. ICE
    # ═══════════════════════════════════════════════════════
    "ice": {
        "config": {
            "title": "ICE AUCTION",
            "logo": "❄️",
            "deco_text": "FROZEN WORLD",
            "deco_left": "❄️", "deco_right": "🧊",
            "winner_hat": "❄️",
            "marquee": [
                "❄️ Frozen World", "🧊 Ice Cold", "⛄ Snowman",
                "🌨 Blizzard", "💧 Chill", "🐧 Penguin",
            ],
            "particles": ["#aae0ff", "#ffffff", "#88ccff", "#ccf0ff"],
            "decorations": [
                {"class": "snow", "emoji": "❄️", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "cube", "emoji": "🧊", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "snowman", "emoji": "⛄", "top": "25%", "right": "5%", "size": "50px"},
                {"class": "penguin", "emoji": "🐧", "bottom": "10%", "right": "5%", "size": "46px"},
            ],
        },
        "css": {
            "c1": "#aae0ff", "c2": "#ffffff", "c3": "#88ccff",
            "c4": "#ccf0ff", "c5": "#4488cc", "c_bg": "#0a1e3d",
            "grad1": "rgba(10,30,60,0.92)", "grad2": "rgba(30,80,140,0.92)",
            "grad3": "rgba(5,20,40,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 16. GOLD / ROYAL
    # ═══════════════════════════════════════════════════════
    "gold": {
        "config": {
            "title": "GOLD AUCTION",
            "logo": "👑",
            "deco_text": "ROYAL GOLD",
            "deco_left": "👑", "deco_right": "💰",
            "winner_hat": "👑",
            "marquee": [
                "👑 Royal Gold", "💰 Money Rain", "🏆 Champion",
                "💎 Diamond", "⭐ VIP", "🎖 Royal Family",
            ],
            "particles": ["#ffd700", "#ffaa00", "#ff8c00", "#ffe066"],
            "decorations": [
                {"class": "crown", "emoji": "👑", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "money", "emoji": "💰", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "diamond", "emoji": "💎", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "trophy", "emoji": "🏆", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#ffd700", "c2": "#ffaa00", "c3": "#ff8c00",
            "c4": "#ffe066", "c5": "#cc8800", "c_bg": "#3d1e00",
            "grad1": "rgba(40,20,0,0.92)", "grad2": "rgba(80,50,0,0.92)",
            "grad3": "rgba(20,10,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 17. BLOOD
    # ═══════════════════════════════════════════════════════
    "blood": {
        "config": {
            "title": "BLOOD AUCTION",
            "logo": "🩸",
            "deco_text": "BLOOD MOON",
            "deco_left": "🩸", "deco_right": "🗡",
            "winner_hat": "🩸",
            "marquee": [
                "🩸 Blood Moon", "🗡 Death Match", "💀 Last One",
                "⚔️ Duel", "🩸 Blood Bath", "🔪 Killer",
            ],
            "particles": ["#ff0000", "#cc0000", "#ff3366", "#990000"],
            "decorations": [
                {"class": "blood", "emoji": "🩸", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "sword", "emoji": "🗡", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "skull", "emoji": "💀", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "knife", "emoji": "🔪", "bottom": "10%", "right": "5%", "size": "46px"},
            ],
        },
        "css": {
            "c1": "#ff0000", "c2": "#cc0000", "c3": "#ff3366",
            "c4": "#990000", "c5": "#660000", "c_bg": "#1e0000",
            "grad1": "rgba(30,0,0,0.92)", "grad2": "rgba(70,0,0,0.92)",
            "grad3": "rgba(15,0,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 18. MATRIX
    # ═══════════════════════════════════════════════════════
    "matrix": {
        "config": {
            "title": "MATRIX AUCTION",
            "logo": "💚",
            "deco_text": "ENTER THE MATRIX",
            "deco_left": "💚", "deco_right": "🔋",
            "winner_hat": "💚",
            "marquee": [
                "💚 Wake Up Neo", "🐇 Follow White Rabbit",
                "💊 Red or Blue", "🔋 Power", "🌐 The Matrix",
            ],
            "particles": ["#00ff00", "#00cc00", "#88ff88", "#00ff88"],
            "decorations": [
                {"class": "heart", "emoji": "💚", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "battery", "emoji": "🔋", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "rabbit", "emoji": "🐇", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "pill", "emoji": "💊", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#00ff00", "c2": "#00cc00", "c3": "#88ff88",
            "c4": "#00ff88", "c5": "#008800", "c_bg": "#000a00",
            "grad1": "rgba(0,15,0,0.92)", "grad2": "rgba(0,40,0,0.92)",
            "grad3": "rgba(0,8,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 19. RETRO 80s
    # ═══════════════════════════════════════════════════════
    "retro": {
        "config": {
            "title": "RETRO AUCTION",
            "logo": "📼",
            "deco_text": "RETRO 80s",
            "deco_left": "📼", "deco_right": "🕹",
            "winner_hat": "📼",
            "marquee": [
                "📼 Retro 80s", "🕹 Arcade", "🎵 Synthwave",
                "📻 Radio", "🌟 Retro Wave", "💾 Floppy Disk",
            ],
            "particles": ["#ff00ff", "#ffff00", "#00ffff", "#ff8800"],
            "decorations": [
                {"class": "tape", "emoji": "📼", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "joystick", "emoji": "🕹", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "music", "emoji": "🎵", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "radio", "emoji": "📻", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff00ff", "c2": "#ffff00", "c3": "#00ffff",
            "c4": "#ff8800", "c5": "#8800ff", "c_bg": "#320050",
            "grad1": "rgba(50,0,80,0.92)", "grad2": "rgba(120,0,120,0.92)",
            "grad3": "rgba(30,0,50,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 20. RAINBOW
    # ═══════════════════════════════════════════════════════
    "rainbow": {
        "config": {
            "title": "RAINBOW AUCTION",
            "logo": "🌈",
            "deco_text": "TASTE THE RAINBOW",
            "deco_left": "🌈", "deco_right": "☁️",
            "winner_hat": "🌈",
            "marquee": [
                "🌈 Taste The Rainbow", "☁️ Over The Rainbow",
                "🌸 Colorful", "🎨 Rainbow Road", "✨ Color Magic",
            ],
            "particles": ["#ff0000", "#ffff00", "#00ff00", "#00ccff", "#ff00ff"],
            "decorations": [
                {"class": "rainbow", "emoji": "🌈", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "cloud", "emoji": "☁️", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "sparkle", "emoji": "✨", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "flower", "emoji": "🌸", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff0000", "c2": "#ffff00", "c3": "#00ff00",
            "c4": "#00ccff", "c5": "#ff00ff", "c_bg": "#1e1e3c",
            "grad1": "rgba(30,30,60,0.92)", "grad2": "rgba(60,30,80,0.92)",
            "grad3": "rgba(20,20,40,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 21. CYBERPUNK
    # ═══════════════════════════════════════════════════════
    "cyberpunk": {
        "config": {
            "title": "CYBERPUNK AUCTION",
            "logo": "🤖",
            "deco_text": "CYBERPUNK 2077",
            "deco_left": "🤖", "deco_right": "⚙️",
            "winner_hat": "🤖",
            "marquee": [
                "🤖 Cyberpunk", "⚙️ Cyborg", "🔌 Neo Tokyo",
                "🌐 Netrunner", "⚡ High Tech Low Life",
            ],
            "particles": ["#ff00ff", "#00ffff", "#ffea00", "#ff0055"],
            "decorations": [
                {"class": "robot", "emoji": "🤖", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "gear", "emoji": "⚙️", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "plug", "emoji": "🔌", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "globe", "emoji": "🌐", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff00ff", "c2": "#00ffff", "c3": "#ffea00",
            "c4": "#ff0055", "c5": "#8800ff", "c_bg": "#0a001e",
            "grad1": "rgba(10,0,30,0.92)", "grad2": "rgba(40,0,70,0.92)",
            "grad3": "rgba(5,0,15,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 22. PASTEL
    # ═══════════════════════════════════════════════════════
    "pastel": {
        "config": {
            "title": "PASTEL AUCTION",
            "logo": "🎀",
            "deco_text": "PASTEL DREAM",
            "deco_left": "🎀", "deco_right": "🌷",
            "winner_hat": "🎀",
            "marquee": [
                "🎀 Pastel Dream", "🌷 Soft Aesthetic", "🦄 Unicorn",
                "☁️ Dreamy", "🌸 Kawaii",
            ],
            "particles": ["#ffd1dc", "#c8e6ff", "#e0d1ff", "#d1ffe0"],
            "decorations": [
                {"class": "bow", "emoji": "🎀", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "tulip", "emoji": "🌷", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "unicorn", "emoji": "🦄", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "cloud", "emoji": "☁️", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ffd1dc", "c2": "#c8e6ff", "c3": "#e0d1ff",
            "c4": "#d1ffe0", "c5": "#ffb3d9", "c_bg": "#3d2842",
            "grad1": "rgba(60,40,66,0.92)", "grad2": "rgba(90,60,100,0.92)",
            "grad3": "rgba(50,30,55,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 23. VAPORWAVE
    # ═══════════════════════════════════════════════════════
    "vaporwave": {
        "config": {
            "title": "VAPORWAVE AUCTION",
            "logo": "🌴",
            "deco_text": "VAPORWAVE",
            "deco_left": "🌴", "deco_right": "🌊",
            "winner_hat": "🌴",
            "marquee": [
                "🌴 Vaporwave", "🌊 Aesthetic", "💜 ＡＥＳＴＨＥＴＩＣ",
                "🌸 90s Vibes", "🛍 Mall Soft",
            ],
            "particles": ["#ff6b9d", "#a88bff", "#6bb6ff", "#ffb3ff"],
            "decorations": [
                {"class": "palm", "emoji": "🌴", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "wave", "emoji": "🌊", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "statue", "emoji": "🗿", "top": "25%", "right": "5%", "size": "50px"},
                {"class": "disc", "emoji": "💿", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff6b9d", "c2": "#a88bff", "c3": "#6bb6ff",
            "c4": "#ffb3ff", "c5": "#ff80aa", "c_bg": "#1e0a3d",
            "grad1": "rgba(30,10,60,0.92)", "grad2": "rgba(60,20,90,0.92)",
            "grad3": "rgba(20,5,40,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 24. STEAMPUNK
    # ═══════════════════════════════════════════════════════
    "steampunk": {
        "config": {
            "title": "STEAMPUNK AUCTION",
            "logo": "⚙️",
            "deco_text": "STEAMPUNK ERA",
            "deco_left": "⚙️", "deco_right": "🎩",
            "winner_hat": "🎩",
            "marquee": [
                "⚙️ Steampunk Era", "🎩 Victorian", "🚂 Steam Train",
                "🔧 Mechanic", "🕰 Clockwork",
            ],
            "particles": ["#d4a574", "#b87333", "#ffd700", "#8b6f47"],
            "decorations": [
                {"class": "gear", "emoji": "⚙️", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "hat", "emoji": "🎩", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "train", "emoji": "🚂", "top": "25%", "right": "5%", "size": "50px"},
                {"class": "clock", "emoji": "🕰", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#d4a574", "c2": "#b87333", "c3": "#ffd700",
            "c4": "#8b6f47", "c5": "#654321", "c_bg": "#2a1a0a",
            "grad1": "rgba(40,25,10,0.92)", "grad2": "rgba(80,50,20,0.92)",
            "grad3": "rgba(30,18,8,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 25. GOTHIC
    # ═══════════════════════════════════════════════════════
    "gothic": {
        "config": {
            "title": "GOTHIC AUCTION",
            "logo": "🥀",
            "deco_text": "GOTHIC ROMANCE",
            "deco_left": "🥀", "deco_right": "🦇",
            "winner_hat": "🥀",
            "marquee": [
                "🥀 Gothic Romance", "🦇 Dark Wings", "🕯 Candle Light",
                "🌹 Black Rose", "⚰️ Vampire",
            ],
            "particles": ["#8b0000", "#4b0082", "#2f0033", "#000000"],
            "decorations": [
                {"class": "rose", "emoji": "🥀", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "bat", "emoji": "🦇", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "candle", "emoji": "🕯", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "coffin", "emoji": "⚰️", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#8b0000", "c2": "#4b0082", "c3": "#2f0033",
            "c4": "#8b008b", "c5": "#1a001a", "c_bg": "#0a0510",
            "grad1": "rgba(15,5,25,0.92)", "grad2": "rgba(30,10,40,0.92)",
            "grad3": "rgba(10,2,15,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 26. TROPICAL
    # ═══════════════════════════════════════════════════════
    "tropical": {
        "config": {
            "title": "TROPICAL AUCTION",
            "logo": "🌴",
            "deco_text": "TROPICAL PARADISE",
            "deco_left": "🌴", "deco_right": "🍹",
            "winner_hat": "🌴",
            "marquee": [
                "🌴 Tropical Paradise", "🍹 Cocktail Time", "🌺 Aloha",
                "🏖 Beach Vibes", "🦜 Paradise",
            ],
            "particles": ["#ffaa00", "#00ff88", "#ff5500", "#00ccff"],
            "decorations": [
                {"class": "palm", "emoji": "🌴", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "cocktail", "emoji": "🍹", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "flower", "emoji": "🌺", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "parrot", "emoji": "🦜", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ffaa00", "c2": "#00ff88", "c3": "#ff5500",
            "c4": "#00ccff", "c5": "#0088aa", "c_bg": "#003d3d",
            "grad1": "rgba(0,60,60,0.92)", "grad2": "rgba(0,100,80,0.92)",
            "grad3": "rgba(0,40,40,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 27. SAMURAI
    # ═══════════════════════════════════════════════════════
    "samurai": {
        "config": {
            "title": "SAMURAI AUCTION",
            "logo": "⚔️",
            "deco_text": "WAY OF SAMURAI",
            "deco_left": "⚔️", "deco_right": "🏯",
            "winner_hat": "⚔️",
            "marquee": [
                "⚔️ Way of Samurai", "🏯 Feudal Japan", "🌸 Bushido",
                "🗡 Katana", "🎋 Zen",
            ],
            "particles": ["#ff3366", "#ffcc00", "#ffffff", "#cc0033"],
            "decorations": [
                {"class": "sword", "emoji": "⚔️", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "castle", "emoji": "🏯", "bottom": "8%", "left": "3%", "size": "50px"},
                {"class": "flower", "emoji": "🌸", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "katana", "emoji": "🗡", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff3366", "c2": "#ffcc00", "c3": "#ffffff",
            "c4": "#cc0033", "c5": "#880022", "c_bg": "#2a0510",
            "grad1": "rgba(40,5,15,0.92)", "grad2": "rgba(70,10,25,0.92)",
            "grad3": "rgba(30,3,10,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 28. EGYPTIAN
    # ═══════════════════════════════════════════════════════
    "egyptian": {
        "config": {
            "title": "EGYPTIAN AUCTION",
            "logo": "🔺",
            "deco_text": "ANCIENT EGYPT",
            "deco_left": "🔺", "deco_right": "🐫",
            "winner_hat": "🔺",
            "marquee": [
                "🔺 Ancient Egypt", "🐫 Desert Sands", "👁 Eye of Horus",
                "🏺 Pharaoh", "☀️ Ra",
            ],
            "particles": ["#ffd700", "#d4af37", "#ffcc00", "#c9a227"],
            "decorations": [
                {"class": "pyramid", "emoji": "🔺", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "camel", "emoji": "🐫", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "eye", "emoji": "👁", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "jar", "emoji": "🏺", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ffd700", "c2": "#d4af37", "c3": "#ffcc00",
            "c4": "#c9a227", "c5": "#8b6914", "c_bg": "#3d2800",
            "grad1": "rgba(60,40,0,0.92)", "grad2": "rgba(100,70,0,0.92)",
            "grad3": "rgba(40,25,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 29. PIRATE
    # ═══════════════════════════════════════════════════════
    "pirate": {
        "config": {
            "title": "PIRATE AUCTION",
            "logo": "🏴‍☠️",
            "deco_text": "PIRATE ADVENTURE",
            "deco_left": "🏴‍☠️", "deco_right": "⚓",
            "winner_hat": "🏴‍☠️",
            "marquee": [
                "🏴‍☠️ Pirate Adventure", "⚓ Anchor", "🦜 Parrot",
                "💰 Treasure", "🗺 Treasure Map", "⚔️ Ship Battle",
            ],
            "particles": ["#8b4513", "#ffd700", "#cc6600", "#ff8c00"],
            "decorations": [
                {"class": "flag", "emoji": "🏴‍☠️", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "anchor", "emoji": "⚓", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "parrot", "emoji": "🦜", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "money", "emoji": "💰", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#8b4513", "c2": "#ffd700", "c3": "#cc6600",
            "c4": "#ff8c00", "c5": "#654321", "c_bg": "#1e0f00",
            "grad1": "rgba(30,15,0,0.92)", "grad2": "rgba(60,30,0,0.92)",
            "grad3": "rgba(20,10,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 30. SPACE
    # ═══════════════════════════════════════════════════════
    "space": {
        "config": {
            "title": "SPACE AUCTION",
            "logo": "🛸",
            "deco_text": "OUTER SPACE",
            "deco_left": "🛸", "deco_right": "👽",
            "winner_hat": "🛸",
            "marquee": [
                "🛸 Outer Space", "👽 Aliens", "🚀 Rocket Launch",
                "🌍 Earth", "🌞 Solar System",
            ],
            "particles": ["#00ccff", "#cc88ff", "#ffffff", "#66ddff"],
            "decorations": [
                {"class": "ufo", "emoji": "🛸", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "alien", "emoji": "👽", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "rocket", "emoji": "🚀", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "earth", "emoji": "🌍", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#00ccff", "c2": "#cc88ff", "c3": "#ffffff",
            "c4": "#66ddff", "c5": "#3366cc", "c_bg": "#02051e",
            "grad1": "rgba(2,5,30,0.92)", "grad2": "rgba(10,15,60,0.92)",
            "grad3": "rgba(1,3,15,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 31. ANIME
    # ═══════════════════════════════════════════════════════
    "anime": {
        "config": {
            "title": "ANIME AUCTION",
            "logo": "🌸",
            "deco_text": "ANIME WORLD",
            "deco_left": "🌸", "deco_right": "⭐",
            "winner_hat": "🌸",
            "marquee": [
                "🌸 Anime World", "⭐ Kawaii", "🌸 Senpai",
                "💖 Waifu", "🗾 Otaku", "⚡ Sugoi",
            ],
            "particles": ["#ff80aa", "#80b3ff", "#ffb3d9", "#aaccff"],
            "decorations": [
                {"class": "flower", "emoji": "🌸", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "star", "emoji": "⭐", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "heart", "emoji": "💖", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "bolt", "emoji": "⚡", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff80aa", "c2": "#80b3ff", "c3": "#ffb3d9",
            "c4": "#aaccff", "c5": "#ff99bb", "c_bg": "#28194d",
            "grad1": "rgba(40,25,77,0.92)", "grad2": "rgba(60,40,110,0.92)",
            "grad3": "rgba(35,20,65,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 32. MINIMAL BLACK
    # ═══════════════════════════════════════════════════════
    "minimal": {
        "config": {
            "title": "MINIMAL AUCTION",
            "logo": "⚫",
            "deco_text": "MINIMAL",
            "deco_left": "⚫", "deco_right": "⚪",
            "winner_hat": "👑",
            "marquee": [
                "⚫ Minimal", "⚪ Clean", "◾ Simple", "◽ Elegant",
            ],
            "particles": ["#ffffff", "#888888", "#cccccc"],
            "decorations": [],
        },
        "css": {
            "c1": "#ffffff", "c2": "#cccccc", "c3": "#888888",
            "c4": "#555555", "c5": "#333333", "c_bg": "#0a0a0a",
            "grad1": "rgba(15,15,15,0.92)", "grad2": "rgba(25,25,25,0.92)",
            "grad3": "rgba(10,10,10,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 33. SAKURA NIGHT
    # ═══════════════════════════════════════════════════════
    "sakura_night": {
        "config": {
            "title": "SAKURA NIGHT",
            "logo": "🌙",
            "deco_text": "MOONLIT SAKURA",
            "deco_left": "🌙", "deco_right": "🌸",
            "winner_hat": "🌙",
            "marquee": [
                "🌙 Moonlit Sakura", "🌸 Night Blossom", "✨ Starry Petals",
                "🍃 Gentle Breeze",
            ],
            "particles": ["#ffb3cc", "#aaccff", "#cc88ff", "#ffffff"],
            "decorations": [
                {"class": "moon", "emoji": "🌙", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "blossom", "emoji": "🌸", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "sparkle", "emoji": "✨", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "leaf", "emoji": "🍃", "bottom": "10%", "right": "5%", "size": "40px"},
            ],
        },
        "css": {
            "c1": "#ffb3cc", "c2": "#aaccff", "c3": "#cc88ff",
            "c4": "#ffffff", "c5": "#88aacc", "c_bg": "#1a0a28",
            "grad1": "rgba(30,10,45,0.92)", "grad2": "rgba(50,20,70,0.92)",
            "grad3": "rgba(20,5,35,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 34. LAVA
    # ═══════════════════════════════════════════════════════
    "lava": {
        "config": {
            "title": "LAVA AUCTION",
            "logo": "🌋",
            "deco_text": "LAVA FLOW",
            "deco_left": "🌋", "deco_right": "🔥",
            "winner_hat": "🌋",
            "marquee": [
                "🌋 Lava Flow", "🔥 Molten", "♨️ Hot Lava",
                "💥 Eruption", "🌡 Heat Wave",
            ],
            "particles": ["#ff2200", "#ff6600", "#ffcc00", "#ff8800"],
            "decorations": [
                {"class": "volcano", "emoji": "🌋", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "fire", "emoji": "🔥", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "boom", "emoji": "💥", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "thermometer", "emoji": "🌡", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff2200", "c2": "#ff6600", "c3": "#ffcc00",
            "c4": "#ff8800", "c5": "#aa1100", "c_bg": "#2a0500",
            "grad1": "rgba(50,5,0,0.92)", "grad2": "rgba(100,20,0,0.92)",
            "grad3": "rgba(35,0,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 35. AURORA
    # ═══════════════════════════════════════════════════════
    "aurora": {
        "config": {
            "title": "AURORA AUCTION",
            "logo": "🌌",
            "deco_text": "AURORA BOREALIS",
            "deco_left": "🌌", "deco_right": "❄️",
            "winner_hat": "🌌",
            "marquee": [
                "🌌 Aurora Borealis", "❄️ Northern Lights",
                "✨ Polar Sky", "🌟 Star Shower",
            ],
            "particles": ["#00ffcc", "#cc88ff", "#00ccff", "#88ffcc"],
            "decorations": [
                {"class": "galaxy", "emoji": "🌌", "top": "10%", "left": "5%", "size": "50px"},
                {"class": "snow", "emoji": "❄️", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "star", "emoji": "✨", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "shooting", "emoji": "🌠", "bottom": "10%", "right": "5%", "size": "50px"},
            ],
        },
        "css": {
            "c1": "#00ffcc", "c2": "#cc88ff", "c3": "#00ccff",
            "c4": "#88ffcc", "c5": "#0099aa", "c_bg": "#001428",
            "grad1": "rgba(0,20,40,0.92)", "grad2": "rgba(0,40,70,0.92)",
            "grad3": "rgba(0,10,25,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 36. SEPIA / VINTAGE
    # ═══════════════════════════════════════════════════════
    "vintage": {
        "config": {
            "title": "VINTAGE AUCTION",
            "logo": "📻",
            "deco_text": "VINTAGE ERA",
            "deco_left": "📻", "deco_right": "🎞",
            "winner_hat": "📻",
            "marquee": [
                "📻 Vintage Era", "🎞 Old Times", "☕ Retro Cafe",
                "🕰 Classic", "📷 Old Camera",
            ],
            "particles": ["#d4a574", "#8b6f47", "#ffd700", "#b87333"],
            "decorations": [
                {"class": "radio", "emoji": "📻", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "film", "emoji": "🎞", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "coffee", "emoji": "☕", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "clock", "emoji": "🕰", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#d4a574", "c2": "#8b6f47", "c3": "#ffd700",
            "c4": "#b87333", "c5": "#654321", "c_bg": "#281810",
            "grad1": "rgba(35,22,15,0.92)", "grad2": "rgba(65,40,25,0.92)",
            "grad3": "rgba(30,18,12,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 37. GLITCH
    # ═══════════════════════════════════════════════════════
    "glitch": {
        "config": {
            "title": "GLITCH AUCTION",
            "logo": "📺",
            "deco_text": "GLITCH ART",
            "deco_left": "📺", "deco_right": "💥",
            "winner_hat": "📺",
            "marquee": [
                "📺 Glitch Art", "💥 Error 404", "⚡ System Failure",
                "🎮 Game Over", "🔧 Reboot",
            ],
            "particles": ["#ff00ff", "#00ffff", "#00ff00", "#ff0000"],
            "decorations": [
                {"class": "tv", "emoji": "📺", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "boom", "emoji": "💥", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "bolt", "emoji": "⚡", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "wrench", "emoji": "🔧", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ff00ff", "c2": "#00ffff", "c3": "#00ff00",
            "c4": "#ff0000", "c5": "#8800ff", "c_bg": "#0a000a",
            "grad1": "rgba(15,0,15,0.92)", "grad2": "rgba(40,0,40,0.92)",
            "grad3": "rgba(8,0,8,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 38. ZEN
    # ═══════════════════════════════════════════════════════
    "zen": {
        "config": {
            "title": "ZEN AUCTION",
            "logo": "☯",
            "deco_text": "PEACE & ZEN",
            "deco_left": "☯", "deco_right": "🎋",
            "winner_hat": "☯",
            "marquee": [
                "☯ Peace & Zen", "🎋 Bamboo", "🍵 Tea Time",
                "🧘 Meditation", "🌸 Inner Peace",
            ],
            "particles": ["#88aa66", "#aacc88", "#ccddaa", "#88ccaa"],
            "decorations": [
                {"class": "yin", "emoji": "☯", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "bamboo", "emoji": "🎋", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "tea", "emoji": "🍵", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "flower", "emoji": "🌸", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#88aa66", "c2": "#aacc88", "c3": "#ccddaa",
            "c4": "#88ccaa", "c5": "#556633", "c_bg": "#1a2818",
            "grad1": "rgba(25,40,20,0.92)", "grad2": "rgba(45,65,35,0.92)",
            "grad3": "rgba(20,30,15,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 39. HONEY
    # ═══════════════════════════════════════════════════════
    "honey": {
        "config": {
            "title": "HONEY AUCTION",
            "logo": "🍯",
            "deco_text": "SWEET HONEY",
            "deco_left": "🍯", "deco_right": "🐝",
            "winner_hat": "🍯",
            "marquee": [
                "🍯 Sweet Honey", "🐝 Busy Bee", "🌸 Flower Field",
                "☀️ Sunny Day", "🍯 Golden Drop",
            ],
            "particles": ["#ffcc00", "#ffaa00", "#ffdd66", "#ff8800"],
            "decorations": [
                {"class": "honey", "emoji": "🍯", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "bee", "emoji": "🐝", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "flower", "emoji": "🌸", "top": "25%", "right": "5%", "size": "44px"},
                {"class": "sun", "emoji": "☀️", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#ffcc00", "c2": "#ffaa00", "c3": "#ffdd66",
            "c4": "#ff8800", "c5": "#cc8800", "c_bg": "#3d2800",
            "grad1": "rgba(60,40,0,0.92)", "grad2": "rgba(100,70,0,0.92)",
            "grad3": "rgba(40,25,0,0.92)",
        },
    },

    # ═══════════════════════════════════════════════════════
    # 40. COSMIC DREAM
    # ═══════════════════════════════════════════════════════
    "cosmic": {
        "config": {
            "title": "COSMIC AUCTION",
            "logo": "✨",
            "deco_text": "COSMIC DREAM",
            "deco_left": "✨", "deco_right": "💫",
            "winner_hat": "✨",
            "marquee": [
                "✨ Cosmic Dream", "💫 Nebula", "🌌 Andromeda",
                "⭐ Supernova", "🪐 Cosmic Dust",
            ],
            "particles": ["#cc88ff", "#88ccff", "#ff88cc", "#ffffff", "#aaffcc"],
            "decorations": [
                {"class": "sparkle", "emoji": "✨", "top": "10%", "left": "5%", "size": "44px"},
                {"class": "dizzy", "emoji": "💫", "bottom": "8%", "left": "3%", "size": "44px"},
                {"class": "galaxy", "emoji": "🌌", "top": "25%", "right": "5%", "size": "50px"},
                {"class": "star", "emoji": "⭐", "bottom": "10%", "right": "5%", "size": "44px"},
            ],
        },
        "css": {
            "c1": "#cc88ff", "c2": "#88ccff", "c3": "#ff88cc",
            "c4": "#ffffff", "c5": "#aaffcc", "c_bg": "#140528",
            "grad1": "rgba(20,5,40,0.92)", "grad2": "rgba(50,15,80,0.92)",
            "grad3": "rgba(10,2,20,0.92)",
        },
    },
}


# ============================================================
# CSS TEMPLATE — Dùng cho tất cả theme
# ============================================================
THEME_CSS_TEMPLATE = """
/* ═══════════════════════════════════════════════════════════
   {title} — Premium Theme
   ═══════════════════════════════════════════════════════════ */

/* Biến màu */
:root {{
  --c1: {c1};
  --c2: {c2};
  --c3: {c3};
  --c4: {c4};
  --c5: {c5};
  --c-bg: {c_bg};
}}

/* ─── Main wrapper — Glass + multi-glow ─── */
.wrap {{
  background:
    /* Lớp radial glow */
    radial-gradient(circle at 15% 15%,
      {c1_15} 0%, transparent 45%),
    radial-gradient(circle at 85% 85%,
      {c4_15} 0%, transparent 45%),
    /* Nền chính */
    linear-gradient(160deg,
      {grad1} 0%,
      {grad2} 50%,
      {grad3} 100%);

  border: 1px solid {c1_40};

  box-shadow:
    /* Bóng ngoài */
    0 30px 100px rgba(0, 0, 0, 0.7),
    0 8px 24px rgba(0, 0, 0, 0.5),
    /* Glow nhiều màu */
    0 0 80px {c1_35},
    0 0 160px {c4_25},
    0 0 240px {c5_15},
    /* Viền trong sáng */
    inset 0 0 0 1px {c1_20},
    inset 0 1px 0 {c2_30},
    /* Chiều sâu trong */
    inset 0 -40px 80px rgba(0, 0, 0, 0.4);

  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
}}

/* ─── Viền conic gradient xoay ─── */
.wrap::after {{
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 28px;
  padding: 2px;
  background: conic-gradient(from 0deg,
    {c1}, {c2}, {c3}, {c4}, {c5}, {c1});
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: borderRotate 4s linear infinite;
  pointer-events: none;
  z-index: 2;
  opacity: 0.9;
}}

@keyframes borderRotate {{
  0% {{ filter: hue-rotate(0deg); }}
  100% {{ filter: hue-rotate(360deg); }}
}}

/* ─── Top deco ─── */
.top-deco {{
  background: linear-gradient(90deg,
    {c1_15}, {c2_15}, {c4_15});
  border: 1px solid {c1_40};
  box-shadow:
    inset 0 1px 0 {c2_25},
    0 0 20px {c1_25};
}}

.deco-text {{
  background: linear-gradient(135deg, {c1}, {c2}, {c3}, {c1});
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: decoTextShift 2s ease infinite;
  filter: drop-shadow(0 0 10px {c1_80});
}}

@keyframes decoTextShift {{
  0%, 100% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
}}

/* ─── Logo + Title ─── */
.logo {{
  filter:
    drop-shadow(0 0 12px {c1})
    drop-shadow(0 0 30px {c1_60});
}}

.title {{
  background: linear-gradient(135deg, {c1}, {c2}, {c3}, {c1});
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: titleShift 3s ease infinite;
  filter: drop-shadow(0 0 12px {c1_80});
}}

@keyframes titleShift {{
  0%, 100% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
}}

/* ─── Snap badge ─── */
.snap-badge {{
  background: linear-gradient(90deg, {c3}, {c1}, {c3});
  background-size: 200% 100%;
  color: #fff;
  box-shadow:
    0 0 20px {c1},
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  animation: snapShift 1s ease infinite,
             snapPulse 0.6s ease infinite alternate;
}}

@keyframes snapShift {{
  0%, 100% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
}}

@keyframes snapPulse {{
  from {{ transform: scale(1); }}
  to {{ transform: scale(1.08); }}
}}

/* ─── Timer ─── */
.timer {{
  background: linear-gradient(135deg, {c1_30}, {c4_30});
  border: 1px solid {c1_50};
  color: #fff;
  text-shadow: 0 0 12px {c1};
  box-shadow:
    0 0 30px {c1_40},
    inset 0 1px 0 {c2_30};
}}

.timer.warn {{
  background: linear-gradient(135deg, #ff0033, #ff5500);
  border-color: {c2};
  animation: timerWarn 0.6s infinite;
}}

@keyframes timerWarn {{
  0%, 100% {{ transform: scale(1); box-shadow: 0 0 30px #ff0033; }}
  50% {{ transform: scale(1.08); box-shadow: 0 0 60px {c1}; }}
}}

/* ─── Marquee ─── */
.marquee {{
  background: linear-gradient(90deg, {c1_10}, {c4_10});
  border: 1px solid {c1_25};
  box-shadow:
    inset 0 1px 0 {c1_15},
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);
}}

.marquee::before {{
  background: linear-gradient(90deg, {c_bg} 0%, transparent 100%);
}}

.marquee::after {{
  background: linear-gradient(270deg, {c_bg} 0%, transparent 100%);
}}

.marquee-track span {{
  color: {c2};
  filter: drop-shadow(0 0 8px {c1});
}}

/* ─── Row ─── */
.row {{
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.08) 0%,
    rgba(255, 255, 255, 0.02) 100%);
  border: 1px solid {c1_20};
  box-shadow:
    inset 0 1px 0 {c1_15},
    inset 0 -1px 0 rgba(0, 0, 0, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.25);
}}

.row.rank-1 {{
  background: linear-gradient(135deg,
    {c1_40} 0%,
    {c3_15} 100%);
  border: 2px solid {c1_70};
  box-shadow:
    0 0 40px {c1_60},
    0 0 80px {c1_30},
    inset 0 1px 0 {c2_40},
    inset 0 -20px 40px {c3_20};
}}

.row.rank-2 {{
  background: linear-gradient(135deg,
    rgba(220, 220, 240, 0.25) 0%,
    rgba(150, 150, 180, 0.08) 100%);
  border: 1px solid rgba(220, 220, 240, 0.6);
  box-shadow:
    0 0 30px rgba(200, 200, 220, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}}

.row.rank-3 {{
  background: linear-gradient(135deg,
    rgba(205, 127, 50, 0.3) 0%,
    rgba(140, 80, 20, 0.08) 100%);
  border: 1px solid rgba(205, 127, 50, 0.7);
  box-shadow:
    0 0 30px rgba(205, 127, 50, 0.4),
    inset 0 1px 0 rgba(255, 200, 150, 0.3);
}}

.medal {{
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.5));
}}

.row.rank-1 .medal {{
  filter:
    drop-shadow(0 0 12px {c1})
    drop-shadow(0 0 24px {c1_60});
  animation: medalBounce 1.5s ease-in-out infinite;
}}

@keyframes medalBounce {{
  0%, 100% {{ transform: scale(1) rotate(-3deg); }}
  50% {{ transform: scale(1.08) rotate(3deg); }}
}}

.user {{
  color: #fff;
  text-shadow:
    0 2px 6px rgba(0, 0, 0, 0.8),
    0 0 20px {c1_40};
}}

.row.rank-1 .user {{
  color: #fff8d0;
  text-shadow:
    0 2px 6px rgba(0, 0, 0, 0.9),
    0 0 30px {c1_90};
}}

.score {{
  color: #00ff88;
  text-shadow:
    0 0 12px rgba(0, 255, 136, 0.8),
    0 0 24px rgba(0, 255, 136, 0.4);
}}

.row.rank-1 .score {{
  color: {c2};
  text-shadow:
    0 0 16px {c1},
    0 0 32px {c1_70};
}}

.empty {{
  color: {c1_60};
  text-shadow: 0 0 10px {c1_40};
}}

/* ─── Tie overlay ─── */
.tie-overlay::before {{
  background: radial-gradient(circle at center,
    {grad2} 0%,
    rgba(0, 0, 0, 0.98) 100%);
}}

.tie-card {{
  border: 2px solid {c1_60};
  color: {c1};
  box-shadow:
    0 0 60px {c1},
    inset 0 1px 0 {c2_30},
    0 20px 60px rgba(0, 0, 0, 0.6);
}}

.tie-title {{
  background: linear-gradient(135deg, {c1}, {c2}, {c3}, {c1});
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: decoTextShift 2s ease infinite;
  filter: drop-shadow(0 0 20px {c1_90});
}}

.tie-vs {{
  color: {c3};
  text-shadow:
    0 0 20px {c3},
    0 0 40px {c3};
}}

.tie-score {{
  color: {c1};
  text-shadow: 0 0 12px {c1};
}}

.tie-footer {{
  background: linear-gradient(90deg, {c3}, {c5}, {c3});
  background-size: 200% 100%;
  color: #fff;
  animation: snapShift 1.5s ease infinite;
}}

/* ─── Winner ─── */
.winner-overlay::before {{
  background: radial-gradient(circle at center,
    {grad2} 0%,
    rgba(0, 0, 0, 0.98) 100%);
}}

.wo-card {{
  border: 2px solid {c1_70};
  color: {c1};
  box-shadow:
    0 0 80px {c1},
    inset 0 1px 0 {c2_30},
    0 20px 60px rgba(0, 0, 0, 0.7);
}}

.wo-label {{
  color: {c1};
  text-shadow: 0 0 20px {c1};
}}

.wo-name {{
  background: linear-gradient(135deg, #fff, {c1}, {c3}, {c1});
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: decoTextShift 2s ease infinite;
  filter: drop-shadow(0 0 20px {c1_90});
}}

/* ─── Decorations ─── */
@keyframes batFly {{
  0% {{ transform: translateX(0) translateY(0) rotate(0); }}
  25% {{ transform: translateY(-25px) rotate(-15deg); }}
  50% {{ transform: translateX(50vw) translateY(20px) rotate(15deg); }}
  75% {{ transform: translateY(-15px) rotate(-15deg); }}
  100% {{ transform: translateX(110vw) translateY(0) rotate(0); }}
}}

@keyframes pumpkinPulse {{
  0%, 100% {{ transform: scale(1) rotate(-5deg); }}
  50% {{ transform: scale(1.15) rotate(5deg); }}
}}

@keyframes ghostFloat {{
  0%, 100% {{ transform: translateY(0) translateX(0); opacity: 0.5; }}
  50% {{ transform: translateY(-30px) translateX(15px); opacity: 0.9; }}
}}

@keyframes snowFall {{
  0% {{ transform: translateY(0) rotate(0); }}
  100% {{ transform: translateY(100vh) rotate(360deg); }}
}}

@keyframes treeShake {{
  0%, 100% {{ transform: rotate(-3deg); }}
  50% {{ transform: rotate(3deg); }}
}}

@keyframes giftBounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-10px); }}
}}

@keyframes starTwinkle {{
  0%, 100% {{ opacity: 0.5; transform: scale(1); }}
  50% {{ opacity: 1; transform: scale(1.2); }}
}}
"""


# ============================================================
# HELPER để tạo hex alpha
# ============================================================
def hex_to_rgba(hex_color, alpha):
    """Chuyển #RRGGBB → rgba(r,g,b,alpha)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ============================================================
# MAIN
# ============================================================
def main():
    BASE.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("🎨 TẠO 40 THEME PREMIUM")
    print("=" * 65)
    print()

    # Xóa folder cũ nếu có
    if BASE.exists():
        import shutil
        for item in BASE.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
        print(f"🧹 Đã xóa theme cũ trong {BASE}")
        print()

    created = 0

    for name, data in THEMES.items():
        theme_dir = BASE / name
        theme_dir.mkdir(parents=True, exist_ok=True)

        config = data["config"]
        colors = data["css"]

        # Config JSON
        config_file = theme_dir / "config.json"
        config_file.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

                # Tạo CSS từ template
        css_vars = dict(colors)
        css_vars["title"] = config.get("title", name.upper())   # ★ THÊM DÒNG NÀY

        # Thêm biến alpha cho các màu chính
        for key in ["c1", "c2", "c3", "c4", "c5"]:
            color = colors.get(key, "#ffffff")
            for alpha in [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90]:
                css_vars[f"{key}_{alpha}"] = hex_to_rgba(color, alpha / 100)

        css = THEME_CSS_TEMPLATE.format(**css_vars)

        css_file = theme_dir / "theme.css"
        css_file.write_text(css, encoding="utf-8")

        created += 1
        print(f"  ✅ [{created:2d}/40] {name:20s} → {config['title']}")

    print()
    print("=" * 65)
    print(f"🎉 HOÀN THÀNH! Đã tạo {created} theme")
    print(f"📁 Folder: {BASE}")
    print("=" * 65)


if __name__ == "__main__":
    main()