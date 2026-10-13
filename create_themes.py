"""
Tool tạo 25 theme premium, nền đục hoàn toàn.
Chạy: uv run python create_themes.py
"""
from pathlib import Path
import json
import shutil


BASE = Path(__file__).parent / "themes"


# ============================================================
# 25 THEME CONFIG
# ============================================================
THEMES = {
    "halloween": {
        "config": {
            "title": "HALLOWEEN AUCTION", "logo": "🎃",
            "deco_text": "HAPPY HALLOWEEN",
            "deco_left": "🧙", "deco_right": "🧹", "winner_hat": "🧙",
            "marquee": ["🎃 Trick or Treat", "🦇 Spooky Vibes", "👻 Boo!", "🧙 Happy Halloween"],
            "particles": ["#ff8000", "#ffcc00", "#a020f0", "#ff5500"],
            "decorations": [
                {"class": "bat", "emoji": "🦇", "top": "12%", "left": "3%", "size": "42px"},
                {"class": "pumpkin", "emoji": "🎃", "bottom": "8%", "left": "3%", "size": "50px"},
                {"class": "ghost", "emoji": "👻", "top": "25%", "right": "5%", "size": "38px"},
            ],
        },
        "css": {"c1": "#ff8000", "c2": "#ffcc00", "c3": "#ff5500", "c4": "#a020f0", "c5": "#7c3aed", "c_bg": "#1a0828"},
    },
    "christmas": {
        "config": {"title": "CHRISTMAS AUCTION", "logo": "🎄", "deco_text": "MERRY CHRISTMAS",
                   "deco_left": "🎅", "deco_right": "🦌", "winner_hat": "🎅",
                   "marquee": ["🎄 Merry Christmas", "🎁 Ho Ho Ho", "❄️ Let it Snow", "🔔 Jingle Bells"],
                   "particles": ["#ff3333", "#ffffff", "#00cc66", "#ffcc00"],
                   "decorations": [
                       {"class": "snow", "emoji": "❄️", "top": "10%", "left": "20%", "size": "30px"},
                       {"class": "tree", "emoji": "🎄", "bottom": "5%", "left": "3%", "size": "60px"},
                       {"class": "gift", "emoji": "🎁", "bottom": "5%", "right": "3%", "size": "50px"},
                   ]},
        "css": {"c1": "#ff3333", "c2": "#ffffff", "c3": "#00cc66", "c4": "#ffcc00", "c5": "#c41e3a", "c_bg": "#0a1f10"},
    },
    "tet": {
        "config": {"title": "TẾT AUCTION", "logo": "🧧", "deco_text": "CHÚC MỪNG NĂM MỚI",
                   "deco_left": "🏮", "deco_right": "🌸", "winner_hat": "🧧",
                   "marquee": ["🧧 Chúc Mừng Năm Mới", "🌸 Hoa Mai", "🏮 Lì Xì", "🐉 Rồng Vàng"],
                   "particles": ["#ffcc00", "#ff5500", "#ff0033", "#ffaa00"],
                   "decorations": [
                       {"class": "lantern", "emoji": "🏮", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "flower", "emoji": "🌸", "bottom": "8%", "left": "3%", "size": "40px"},
                       {"class": "envelope", "emoji": "🧧", "bottom": "8%", "right": "3%", "size": "50px"},
                   ]},
        "css": {"c1": "#ffcc00", "c2": "#ff5500", "c3": "#ff0033", "c4": "#ffaa00", "c5": "#8b0000", "c_bg": "#3d0a0a"},
    },
    "valentine": {
        "config": {"title": "VALENTINE AUCTION", "logo": "💝", "deco_text": "BE MY VALENTINE",
                   "deco_left": "🌹", "deco_right": "💕", "winner_hat": "💝",
                   "marquee": ["💝 Happy Valentine", "🌹 Love is in the air", "💕 Kiss me", "💖 Sweet Heart"],
                   "particles": ["#ff6b9d", "#ff0055", "#ffb3cc", "#ff3366"],
                   "decorations": [
                       {"class": "heart", "emoji": "💖", "top": "10%", "left": "5%", "size": "40px"},
                       {"class": "rose", "emoji": "🌹", "bottom": "8%", "left": "3%", "size": "50px"},
                       {"class": "kiss", "emoji": "💋", "top": "25%", "right": "5%", "size": "40px"},
                   ]},
        "css": {"c1": "#ff6b9d", "c2": "#ff0055", "c3": "#ffb3cc", "c4": "#ff3366", "c5": "#c70039", "c_bg": "#3d0820"},
    },
    "gaming": {
        "config": {"title": "GAMING AUCTION", "logo": "🎮", "deco_text": "GAME ON",
                   "deco_left": "🎮", "deco_right": "🎯", "winner_hat": "🎮",
                   "marquee": ["🎮 Game On", "🏆 GG WP", "⚡ Ready Player One", "🎯 Victory Royale"],
                   "particles": ["#00ccff", "#7c5cff", "#00ff88", "#ff00ff"],
                   "decorations": [
                       {"class": "pad", "emoji": "🎮", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "target", "emoji": "🎯", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "trophy", "emoji": "🏆", "bottom": "10%", "right": "5%", "size": "46px"},
                   ]},
        "css": {"c1": "#00ccff", "c2": "#7c5cff", "c3": "#00ff88", "c4": "#ff00ff", "c5": "#0055ff", "c_bg": "#0a0f1e"},
    },
    "neon": {
        "config": {"title": "NEON AUCTION", "logo": "🌃", "deco_text": "NEON NIGHTS",
                   "deco_left": "⚡", "deco_right": "💜", "winner_hat": "🌃",
                   "marquee": ["🌃 Neon Nights", "⚡ Cyberpunk", "💜 Synth Wave", "✨ Glow Up"],
                   "particles": ["#ff00ff", "#00ffff", "#ff0080", "#8800ff"],
                   "decorations": [
                       {"class": "bolt", "emoji": "⚡", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "heart", "emoji": "💜", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "city", "emoji": "🌆", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#ff00ff", "c2": "#00ffff", "c3": "#ff0080", "c4": "#8800ff", "c5": "#0080ff", "c_bg": "#140028"},
    },
    "sakura": {
        "config": {"title": "SAKURA AUCTION", "logo": "🌸", "deco_text": "SAKURA SEASON",
                   "deco_left": "🌸", "deco_right": "🍃", "winner_hat": "🌸",
                   "marquee": ["🌸 Sakura Season", "🍃 Cherry Blossom", "🌸 Spring Time", "✨ Peaceful"],
                   "particles": ["#ffb3cc", "#ff80aa", "#ffd1e0", "#ffe0eb"],
                   "decorations": [
                       {"class": "blossom", "emoji": "🌸", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "leaf", "emoji": "🍃", "top": "25%", "right": "5%", "size": "40px"},
                       {"class": "temple", "emoji": "⛩", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#ffb3cc", "c2": "#ff80aa", "c3": "#ffd1e0", "c4": "#ffe0eb", "c5": "#e6a4b4", "c_bg": "#3d1525"},
    },
    "dragon": {
        "config": {"title": "DRAGON AUCTION", "logo": "🐉", "deco_text": "DRAGON BALL",
                   "deco_left": "🐉", "deco_right": "⚡", "winner_hat": "🐉",
                   "marquee": ["🐉 Dragon Ball", "⚡ Super Saiyan", "🔥 Kamehameha", "⭐ 7 Dragon Balls"],
                   "particles": ["#ffcc00", "#ff5500", "#ffaa00", "#ff8800"],
                   "decorations": [
                       {"class": "dragon", "emoji": "🐉", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "bolt", "emoji": "⚡", "bottom": "8%", "left": "3%", "size": "46px"},
                       {"class": "fire", "emoji": "🔥", "top": "25%", "right": "5%", "size": "46px"},
                   ]},
        "css": {"c1": "#ffcc00", "c2": "#ff5500", "c3": "#ffaa00", "c4": "#ff8800", "c5": "#cc4400", "c_bg": "#3d1e00"},
    },
    "ocean": {
        "config": {"title": "OCEAN AUCTION", "logo": "🌊", "deco_text": "DEEP OCEAN",
                   "deco_left": "🌊", "deco_right": "🐠", "winner_hat": "🌊",
                   "marquee": ["🌊 Deep Ocean", "🐠 Under The Sea", "🐚 Ocean Vibes", "🦈 Jaws"],
                   "particles": ["#00ccff", "#00ffcc", "#0088ff", "#00ddff"],
                   "decorations": [
                       {"class": "wave", "emoji": "🌊", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "fish", "emoji": "🐠", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "shark", "emoji": "🦈", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#00ccff", "c2": "#00ffcc", "c3": "#0088ff", "c4": "#00ddff", "c5": "#0055aa", "c_bg": "#001e3d"},
    },
    "forest": {
        "config": {"title": "FOREST AUCTION", "logo": "🌲", "deco_text": "WILD FOREST",
                   "deco_left": "🌲", "deco_right": "🦌", "winner_hat": "🌲",
                   "marquee": ["🌲 Wild Forest", "🦌 Nature Vibes", "🍃 Green Life", "🐺 Wild Pack"],
                   "particles": ["#88ff88", "#44cc44", "#aaffaa", "#66dd66"],
                   "decorations": [
                       {"class": "tree", "emoji": "🌲", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "deer", "emoji": "🦌", "top": "25%", "right": "5%", "size": "44px"},
                       {"class": "wolf", "emoji": "🐺", "bottom": "10%", "right": "5%", "size": "46px"},
                   ]},
        "css": {"c1": "#88ff88", "c2": "#44cc44", "c3": "#aaffaa", "c4": "#66dd66", "c5": "#226622", "c_bg": "#0a2810"},
    },
    "sunset": {
        "config": {"title": "SUNSET AUCTION", "logo": "🌅", "deco_text": "GOLDEN SUNSET",
                   "deco_left": "🌅", "deco_right": "🌇", "winner_hat": "🌅",
                   "marquee": ["🌅 Golden Sunset", "🌇 Orange Sky", "☀️ Sunset Vibes", "🌆 Dusk"],
                   "particles": ["#ff9933", "#ff3366", "#ffcc66", "#ff6633"],
                   "decorations": [
                       {"class": "sun", "emoji": "☀️", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "skyline", "emoji": "🌇", "bottom": "8%", "left": "3%", "size": "50px"},
                       {"class": "bridge", "emoji": "🌉", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#ff9933", "c2": "#ff3366", "c3": "#ffcc66", "c4": "#ff6633", "c5": "#cc4400", "c_bg": "#3d1400"},
    },
    "night": {
        "config": {"title": "NIGHT AUCTION", "logo": "🌙", "deco_text": "MOONLIGHT",
                   "deco_left": "🌙", "deco_right": "⭐", "winner_hat": "🌙",
                   "marquee": ["🌙 Moonlight", "⭐ Starry Night", "🌌 Milky Way", "✨ Twinkle"],
                   "particles": ["#aaccff", "#ffee88", "#88aaff", "#ffffff"],
                   "decorations": [
                       {"class": "moon", "emoji": "🌙", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "star", "emoji": "⭐", "bottom": "8%", "left": "3%", "size": "40px"},
                       {"class": "galaxy", "emoji": "🌌", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#aaccff", "c2": "#ffee88", "c3": "#88aaff", "c4": "#ffffff", "c5": "#5566cc", "c_bg": "#050514"},
    },
    "galaxy": {
        "config": {"title": "GALAXY AUCTION", "logo": "🌌", "deco_text": "INTERSTELLAR",
                   "deco_left": "🌌", "deco_right": "🚀", "winner_hat": "🌌",
                   "marquee": ["🌌 Interstellar", "🚀 To The Moon", "⭐ Cosmic", "🪐 Saturn"],
                   "particles": ["#cc88ff", "#66ddff", "#ff88cc", "#aa88ff"],
                   "decorations": [
                       {"class": "galaxy", "emoji": "🌌", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "rocket", "emoji": "🚀", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "planet", "emoji": "🪐", "top": "25%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#cc88ff", "c2": "#66ddff", "c3": "#ff88cc", "c4": "#aa88ff", "c5": "#5555cc", "c_bg": "#140032"},
    },
    "fire": {
        "config": {"title": "FIRE AUCTION", "logo": "🔥", "deco_text": "BURNING UP",
                   "deco_left": "🔥", "deco_right": "💥", "winner_hat": "🔥",
                   "marquee": ["🔥 Burning Up", "💥 Explosion", "🌋 Volcano", "⚡ Lightning"],
                   "particles": ["#ff5500", "#ffcc00", "#ff2200", "#ff8800"],
                   "decorations": [
                       {"class": "fire", "emoji": "🔥", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "boom", "emoji": "💥", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "volcano", "emoji": "🌋", "bottom": "10%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#ff5500", "c2": "#ffcc00", "c3": "#ff2200", "c4": "#ff8800", "c5": "#aa2200", "c_bg": "#3d0a00"},
    },
    "ice": {
        "config": {"title": "ICE AUCTION", "logo": "❄️", "deco_text": "FROZEN WORLD",
                   "deco_left": "❄️", "deco_right": "🧊", "winner_hat": "❄️",
                   "marquee": ["❄️ Frozen World", "🧊 Ice Cold", "⛄ Snowman", "🌨 Blizzard"],
                   "particles": ["#aae0ff", "#ffffff", "#88ccff", "#ccf0ff"],
                   "decorations": [
                       {"class": "snow", "emoji": "❄️", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "cube", "emoji": "🧊", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "penguin", "emoji": "🐧", "bottom": "10%", "right": "5%", "size": "46px"},
                   ]},
        "css": {"c1": "#aae0ff", "c2": "#ffffff", "c3": "#88ccff", "c4": "#ccf0ff", "c5": "#4488cc", "c_bg": "#0a1e3d"},
    },
    "gold": {
        "config": {"title": "GOLD AUCTION", "logo": "👑", "deco_text": "ROYAL GOLD",
                   "deco_left": "👑", "deco_right": "💰", "winner_hat": "👑",
                   "marquee": ["👑 Royal Gold", "💰 Money Rain", "🏆 Champion", "💎 Diamond"],
                   "particles": ["#ffd700", "#ffaa00", "#ff8c00", "#ffe066"],
                   "decorations": [
                       {"class": "crown", "emoji": "👑", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "money", "emoji": "💰", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "diamond", "emoji": "💎", "top": "25%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ffd700", "c2": "#ffaa00", "c3": "#ff8c00", "c4": "#ffe066", "c5": "#cc8800", "c_bg": "#3d1e00"},
    },
    "blood": {
        "config": {"title": "BLOOD AUCTION", "logo": "🩸", "deco_text": "BLOOD MOON",
                   "deco_left": "🩸", "deco_right": "🗡", "winner_hat": "🩸",
                   "marquee": ["🩸 Blood Moon", "🗡 Death Match", "💀 Last One", "⚔️ Duel"],
                   "particles": ["#ff0000", "#cc0000", "#ff3366", "#990000"],
                   "decorations": [
                       {"class": "blood", "emoji": "🩸", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "sword", "emoji": "🗡", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "skull", "emoji": "💀", "top": "25%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ff0000", "c2": "#cc0000", "c3": "#ff3366", "c4": "#990000", "c5": "#660000", "c_bg": "#1e0000"},
    },
    "matrix": {
        "config": {"title": "MATRIX AUCTION", "logo": "💚", "deco_text": "ENTER THE MATRIX",
                   "deco_left": "💚", "deco_right": "🔋", "winner_hat": "💚",
                   "marquee": ["💚 Wake Up Neo", "🐇 Follow White Rabbit", "💊 Red or Blue", "🌐 The Matrix"],
                   "particles": ["#00ff00", "#00cc00", "#88ff88", "#00ff88"],
                   "decorations": [
                       {"class": "heart", "emoji": "💚", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "battery", "emoji": "🔋", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "pill", "emoji": "💊", "bottom": "10%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#00ff00", "c2": "#00cc00", "c3": "#88ff88", "c4": "#00ff88", "c5": "#008800", "c_bg": "#000a00"},
    },
    "retro": {
        "config": {"title": "RETRO AUCTION", "logo": "📼", "deco_text": "RETRO 80s",
                   "deco_left": "📼", "deco_right": "🕹", "winner_hat": "📼",
                   "marquee": ["📼 Retro 80s", "🕹 Arcade", "🎵 Synthwave", "📻 Radio"],
                   "particles": ["#ff00ff", "#ffff00", "#00ffff", "#ff8800"],
                   "decorations": [
                       {"class": "tape", "emoji": "📼", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "joystick", "emoji": "🕹", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "music", "emoji": "🎵", "top": "25%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ff00ff", "c2": "#ffff00", "c3": "#00ffff", "c4": "#ff8800", "c5": "#8800ff", "c_bg": "#320050"},
    },
    "rainbow": {
        "config": {"title": "RAINBOW AUCTION", "logo": "🌈", "deco_text": "TASTE THE RAINBOW",
                   "deco_left": "🌈", "deco_right": "☁️", "winner_hat": "🌈",
                   "marquee": ["🌈 Taste The Rainbow", "☁️ Over The Rainbow", "🌸 Colorful", "🎨 Rainbow Road"],
                   "particles": ["#ff0000", "#ffff00", "#00ff00", "#00ccff", "#ff00ff"],
                   "decorations": [
                       {"class": "rainbow", "emoji": "🌈", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "cloud", "emoji": "☁️", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "flower", "emoji": "🌸", "bottom": "10%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ff0000", "c2": "#ffff00", "c3": "#00ff00", "c4": "#00ccff", "c5": "#ff00ff", "c_bg": "#1e1e3c"},
    },
    "cyberpunk": {
        "config": {"title": "CYBERPUNK AUCTION", "logo": "🤖", "deco_text": "CYBERPUNK 2077",
                   "deco_left": "🤖", "deco_right": "⚙️", "winner_hat": "🤖",
                   "marquee": ["🤖 Cyberpunk", "⚙️ Cyborg", "🔌 Neo Tokyo", "🌐 Netrunner"],
                   "particles": ["#ff00ff", "#00ffff", "#ffea00", "#ff0055"],
                   "decorations": [
                       {"class": "robot", "emoji": "🤖", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "gear", "emoji": "⚙️", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "plug", "emoji": "🔌", "top": "25%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ff00ff", "c2": "#00ffff", "c3": "#ffea00", "c4": "#ff0055", "c5": "#8800ff", "c_bg": "#0a001e"},
    },
    "pastel": {
        "config": {"title": "PASTEL AUCTION", "logo": "🎀", "deco_text": "PASTEL DREAM",
                   "deco_left": "🎀", "deco_right": "🌷", "winner_hat": "🎀",
                   "marquee": ["🎀 Pastel Dream", "🌷 Soft Aesthetic", "🦄 Unicorn", "☁️ Dreamy"],
                   "particles": ["#ffd1dc", "#c8e6ff", "#e0d1ff", "#d1ffe0"],
                   "decorations": [
                       {"class": "bow", "emoji": "🎀", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "tulip", "emoji": "🌷", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "unicorn", "emoji": "🦄", "top": "25%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ffd1dc", "c2": "#c8e6ff", "c3": "#e0d1ff", "c4": "#d1ffe0", "c5": "#ffb3d9", "c_bg": "#3d2842"},
    },
    "vaporwave": {
        "config": {"title": "VAPORWAVE AUCTION", "logo": "🌴", "deco_text": "VAPORWAVE",
                   "deco_left": "🌴", "deco_right": "🌊", "winner_hat": "🌴",
                   "marquee": ["🌴 Vaporwave", "🌊 Aesthetic", "💜 ＡＥＳＴＨＥＴＩＣ", "🌸 90s Vibes"],
                   "particles": ["#ff6b9d", "#a88bff", "#6bb6ff", "#ffb3ff"],
                   "decorations": [
                       {"class": "palm", "emoji": "🌴", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "wave", "emoji": "🌊", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "statue", "emoji": "🗿", "top": "25%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#ff6b9d", "c2": "#a88bff", "c3": "#6bb6ff", "c4": "#ffb3ff", "c5": "#ff80aa", "c_bg": "#1e0a3d"},
    },
    "steampunk": {
        "config": {"title": "STEAMPUNK AUCTION", "logo": "⚙️", "deco_text": "STEAMPUNK ERA",
                   "deco_left": "⚙️", "deco_right": "🎩", "winner_hat": "🎩",
                   "marquee": ["⚙️ Steampunk Era", "🎩 Victorian", "🚂 Steam Train", "🔧 Mechanic"],
                   "particles": ["#d4a574", "#b87333", "#ffd700", "#8b6f47"],
                   "decorations": [
                       {"class": "gear", "emoji": "⚙️", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "hat", "emoji": "🎩", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "train", "emoji": "🚂", "top": "25%", "right": "5%", "size": "50px"},
                   ]},
        "css": {"c1": "#d4a574", "c2": "#b87333", "c3": "#ffd700", "c4": "#8b6f47", "c5": "#654321", "c_bg": "#2a1a0a"},
    },
    "gothic": {
        "config": {"title": "GOTHIC AUCTION", "logo": "🥀", "deco_text": "GOTHIC ROMANCE",
                   "deco_left": "🥀", "deco_right": "🦇", "winner_hat": "🥀",
                   "marquee": ["🥀 Gothic Romance", "🦇 Dark Wings", "🕯 Candle Light", "🌹 Black Rose"],
                   "particles": ["#8b0000", "#4b0082", "#2f0033", "#000000"],
                   "decorations": [
                       {"class": "rose", "emoji": "🥀", "top": "10%", "left": "5%", "size": "44px"},
                       {"class": "bat", "emoji": "🦇", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "coffin", "emoji": "⚰️", "bottom": "10%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#8b0000", "c2": "#4b0082", "c3": "#2f0033", "c4": "#8b008b", "c5": "#1a001a", "c_bg": "#0a0510"},
    },
    "tropical": {
        "config": {"title": "TROPICAL AUCTION", "logo": "🌴", "deco_text": "TROPICAL PARADISE",
                   "deco_left": "🌴", "deco_right": "🍹", "winner_hat": "🌴",
                   "marquee": ["🌴 Tropical Paradise", "🍹 Cocktail Time", "🌺 Aloha", "🏖 Beach Vibes"],
                   "particles": ["#ffaa00", "#00ff88", "#ff5500", "#00ccff"],
                   "decorations": [
                       {"class": "palm", "emoji": "🌴", "top": "10%", "left": "5%", "size": "50px"},
                       {"class": "cocktail", "emoji": "🍹", "bottom": "8%", "left": "3%", "size": "44px"},
                       {"class": "parrot", "emoji": "🦜", "bottom": "10%", "right": "5%", "size": "44px"},
                   ]},
        "css": {"c1": "#ffaa00", "c2": "#00ff88", "c3": "#ff5500", "c4": "#00ccff", "c5": "#0088aa", "c_bg": "#003d3d"},
    },
    "minimal": {
        "config": {"title": "MINIMAL AUCTION", "logo": "⚫", "deco_text": "MINIMAL",
                   "deco_left": "⚫", "deco_right": "⚪", "winner_hat": "👑",
                   "marquee": ["⚫ Minimal", "⚪ Clean", "◾ Simple", "◽ Elegant"],
                   "particles": ["#ffffff", "#888888", "#cccccc"],
                   "decorations": []},
        "css": {"c1": "#ffffff", "c2": "#cccccc", "c3": "#888888", "c4": "#555555", "c5": "#333333", "c_bg": "#0a0a0a"},
    },
}


# ============================================================
# CSS TEMPLATE — nền đục hoàn toàn
# ============================================================
THEME_CSS_TEMPLATE = """
/* ═══════════════════════════════════════════════════════════
   {title} — Premium Theme (opaque)
   ═══════════════════════════════════════════════════════════ */

:root {{
  --c1: {c1};
  --c2: {c2};
  --c3: {c3};
  --c4: {c4};
  --c5: {c5};
  --c-bg: {c_bg};

  /* Info row (VOUCHES + MIN) */
  --info-bg: {info_bg};
  --info-border: {c1};
  --info-glow: {c1_50};
  --info-inner: {c1_15};
  --info-text: #ffffff;
  --info-text-glow: {c2_70};

  /* Min badge */
  --badge-c1: {c1};
  --badge-c2: {c5};
  --badge-border: {c2};
  --badge-glow: {c1_80};
  --badge-text: #ffffff;
}}

/* ─── MAIN WRAPPER — nền đục 100% ─── */
.wrap {{
  position: absolute;
  top: 40px; right: 40px;
  width: 560px;
  border-radius: 26px;
  padding: 20px 24px 24px;
  z-index: 10;
  /* ★ NỀN ĐỤC HOÀN TOÀN — không dùng transparent, không backdrop-filter */
  background:
    radial-gradient(circle at 15% 15%,
      {c1_15} 0%,
      {c_bg_rgba0} 45%,
      {c_bg_rgba0} 100%),
    radial-gradient(circle at 85% 85%,
      {c4_15} 0%,
      {c_bg_rgba0} 45%,
      {c_bg_rgba0} 100%),
    linear-gradient(160deg,
      {c_bg_light} 0%,
      {c_bg_mid} 50%,
      {c_bg_dark} 100%);
  background-color: {c_bg};
  border: 1px solid {c1_40};
  box-shadow:
    0 30px 100px rgba(0, 0, 0, 0.9),
    0 8px 24px rgba(0, 0, 0, 0.7),
    0 0 80px {c1_35},
    0 0 160px {c4_25},
    0 0 240px {c5_15},
    inset 0 0 0 1px {c1_20},
    inset 0 1px 0 {c2_30},
    inset 0 -40px 80px rgba(0, 0, 0, 0.4);
  /* ★ BỎ backdrop-filter — vì background đã đục */
}}

.wrap::after {{
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 28px;
  padding: 2px;
  background: conic-gradient(from 0deg, {c1}, {c2}, {c3}, {c4}, {c5}, {c1});
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
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

/* ─── TOP DECO ─── */
.top-deco {{
  background: linear-gradient(90deg, {c1_15}, {c2_15}, {c4_15});
  border: 1px solid {c1_40};
  box-shadow: inset 0 1px 0 {c2_25}, 0 0 20px {c1_25};
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

/* ─── LOGO + TITLE ─── */
.logo {{
  filter: drop-shadow(0 0 12px {c1}) drop-shadow(0 0 30px {c1_60});
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

/* ─── SNAP BADGE ─── */
.snap-badge {{
  background: linear-gradient(90deg, {c3}, {c1}, {c3});
  background-size: 200% 100%;
  color: #fff;
  box-shadow: 0 0 20px {c1}, inset 0 1px 0 rgba(255, 255, 255, 0.4);
  animation: snapShift 1s ease infinite, snapPulse 0.6s ease infinite alternate;
}}

@keyframes snapShift {{
  0%, 100% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
}}

@keyframes snapPulse {{
  from {{ transform: scale(1); }}
  to {{ transform: scale(1.08); }}
}}

/* ─── TIMER ─── */
.timer {{
  background: linear-gradient(135deg, {c1_30}, {c4_30});
  border: 1px solid {c1_50};
  color: #fff;
  text-shadow: 0 0 12px {c1};
  box-shadow: 0 0 30px {c1_40}, inset 0 1px 0 {c2_30};
}}

.timer.warn {{
  background: linear-gradient(135deg, #ff0033, {c3});
  border-color: {c2};
  animation: timerWarn 0.6s infinite;
}}

@keyframes timerWarn {{
  0%, 100% {{ transform: scale(1); box-shadow: 0 0 30px #ff0033; }}
  50% {{ transform: scale(1.08); box-shadow: 0 0 60px {c1}; }}
}}

/* ─── MARQUEE ─── */
.marquee {{
  background: linear-gradient(90deg, {c1_10}, {c4_10});
  border: 1px solid {c1_25};
  box-shadow: inset 0 1px 0 {c1_15}, inset 0 -1px 0 rgba(0, 0, 0, 0.2);
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

/* ═══ INFO ROW (VOUCHES + MIN) ═══ */
.info-row {{
  display: flex;
  align-items: stretch;
  gap: 10px;
  margin-bottom: 14px;
}}

.info-row .vouch-row,
.info-row .min-row {{
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--info-bg);
  border: 2px solid var(--info-border);
  box-shadow: 0 0 12px var(--info-glow), inset 0 0 8px var(--info-inner);
}}

.info-row .vouch-icon {{
  font-size: 20px;
  color: var(--info-border);
  filter: drop-shadow(0 0 8px var(--info-border));
  line-height: 1;
}}

.info-row .vouch-text {{
  font-size: 18px;
  font-weight: 900;
  color: var(--info-text);
  letter-spacing: 1.5px;
  text-shadow: 0 0 4px var(--info-text-glow), 0 2px 4px rgba(0, 0, 0, 0.8);
  text-transform: uppercase;
  white-space: nowrap;
}}

.info-row .min-row {{
  justify-content: space-between;
}}

.info-row .min-label {{
  font-size: 16px;
  font-weight: 900;
  color: var(--info-text);
  letter-spacing: 1.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  white-space: nowrap;
}}

.info-row .min-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--badge-c1), var(--badge-c2));
  border: 2px solid var(--badge-border);
  box-shadow: 0 0 12px var(--badge-glow), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}}

.info-row .min-value {{
  font-size: 18px;
  font-weight: 900;
  color: var(--badge-text);
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
  font-variant-numeric: tabular-nums;
}}

.info-row .min-coin {{
  font-size: 16px;
  filter: drop-shadow(0 0 6px var(--badge-border));
}}

/* ─── ROW ─── */
.row {{
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
  border: 1px solid {c1_20};
  box-shadow: inset 0 1px 0 {c1_15}, inset 0 -1px 0 rgba(0, 0, 0, 0.15), 0 4px 16px rgba(0, 0, 0, 0.25);
}}

.row.rank-1 {{
  background: linear-gradient(135deg, {c1_40} 0%, {c3_15} 100%);
  border: 2px solid {c1_70};
  box-shadow: 0 0 40px {c1_60}, 0 0 80px {c1_30}, inset 0 1px 0 {c2_40};
}}

.row.rank-2 {{
  background: linear-gradient(135deg, rgba(220, 220, 240, 0.25) 0%, rgba(150, 150, 180, 0.08) 100%);
  border: 1px solid rgba(220, 220, 240, 0.6);
  box-shadow: 0 0 30px rgba(200, 200, 220, 0.4);
}}

.row.rank-3 {{
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.3) 0%, rgba(140, 80, 20, 0.08) 100%);
  border: 1px solid rgba(205, 127, 50, 0.7);
  box-shadow: 0 0 30px rgba(205, 127, 50, 0.4);
}}

.medal {{ filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.5)); }}

.row.rank-1 .medal {{
  filter: drop-shadow(0 0 12px {c1}) drop-shadow(0 0 24px {c1_60});
  animation: medalBounce 1.5s ease-in-out infinite;
}}

@keyframes medalBounce {{
  0%, 100% {{ transform: scale(1) rotate(-3deg); }}
  50% {{ transform: scale(1.08) rotate(3deg); }}
}}

.user {{
  color: #fff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.8), 0 0 20px {c1_40};
}}

.row.rank-1 .user {{
  color: #fff8d0;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9), 0 0 30px {c1_90};
}}

.score {{
  color: #00ff88;
  text-shadow: 0 0 12px rgba(0, 255, 136, 0.8), 0 0 24px rgba(0, 255, 136, 0.4);
}}

.row.rank-1 .score {{
  color: {c2};
  text-shadow: 0 0 16px {c1}, 0 0 32px {c1_70};
}}

.empty {{
  color: {c1_60};
  text-shadow: 0 0 10px {c1_40};
}}

/* ─── TIE + WINNER ─── */
.tie-overlay::before,
.winner-overlay::before {{
  background: radial-gradient(circle at center, {c_bg} 0%, #000 100%);
}}

.tie-card, .wo-card {{
  border: 2px solid {c1_60};
  color: {c1};
  background: {c_bg};
  box-shadow: 0 0 60px {c1}, inset 0 1px 0 {c2_30}, 0 20px 60px rgba(0, 0, 0, 0.6);
}}

.tie-title, .wo-name {{
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
  text-shadow: 0 0 20px {c3}, 0 0 40px {c3};
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

.wo-label {{
  color: {c1};
  text-shadow: 0 0 20px {c1};
}}

/* ─── DECORATION ANIMATIONS ─── */
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
# HELPERS
# ============================================================
def hex_to_rgba(hex_color, alpha):
    """Chuyển #RRGGBB → rgba(r,g,b,alpha)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def hex_lighten(hex_color, factor=1.2):
    """Làm sáng màu."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r = min(255, int(int(h[0:2], 16) * factor))
    g = min(255, int(int(h[2:4], 16) * factor))
    b = min(255, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_darken(hex_color, factor=0.75):
    """Làm tối màu."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r = max(0, int(int(h[0:2], 16) * factor))
    g = max(0, int(int(h[2:4], 16) * factor))
    b = max(0, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================
# MAIN
# ============================================================
def main():
    BASE.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("🎨 TẠO 25 THEME PREMIUM — NỀN ĐỤC")
    print("=" * 65)
    print()

    if BASE.exists():
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

        # CSS vars
        css_vars = dict(colors)
        css_vars["title"] = config.get("title", name.upper())

        # Alpha colors
        for key in ["c1", "c2", "c3", "c4", "c5"]:
            color = colors.get(key, "#ffffff")
            for alpha in [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90]:
                css_vars[f"{key}_{alpha}"] = hex_to_rgba(color, alpha / 100)

                # Background shades — ★ ĐỤC HOÀN TOÀN
        c_bg = colors.get("c_bg", "#0a0a0a")
        css_vars["c_bg"] = c_bg
        css_vars["c_bg_light"] = hex_lighten(c_bg, 1.15)
        css_vars["c_bg_mid"] = c_bg
        css_vars["c_bg_dark"] = hex_darken(c_bg, 0.75)

        # ★ c_bg_rgba0 — màu nền với alpha=0 (thay cho `transparent`)
        h = c_bg.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        css_vars["c_bg_rgba0"] = f"rgba({r},{g},{b},0)"

        # info_bg — nền info row đục 60%
        css_vars["info_bg"] = hex_to_rgba(c_bg, 0.6)

        # Generate CSS
        css = THEME_CSS_TEMPLATE.format(**css_vars)

        css_file = theme_dir / "theme.css"
        css_file.write_text(css, encoding="utf-8")

        created += 1
        print(f"  ✅ [{created:2d}/25] {name:20s} → {config['title']}")

    print()
    print("=" * 65)
    print(f"🎉 HOÀN THÀNH! Đã tạo {created} theme — nền đục 100%")
    print(f"📁 Folder: {BASE.absolute()}")
    print("=" * 65)


if __name__ == "__main__":
    main()