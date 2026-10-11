"""TikTok gift list with diamond values + effect category + folder name.

Format: (name, icon, points, effect_type, folder)
effect_type:
  "fx"   = quà lớn, phát file animation (webm/gif/lottie)
  "text" = quà nhỏ, chỉ hiện toast chữ
"""

GIFTS = [
    # ==================== TEXT GIFTS ====================
    ("Rose",              "🌹",  1,     "text", "rose"),
    ("TikTok",            "🎵",  1,     "text", "tiktok"),
    ("GG",                "🎮",  1,     "text", "gg"),
    ("Finger Heart",      "🫰",  5,     "text", "finger_heart"),
    ("Ice Cream Cone",    "🍦",  5,     "text", "ice_cream_cone"),
    ("Thumbs Up",         "👍",  5,     "text", "thumbs_up"),
    ("Hand Wave",         "👋",  9,     "text", "hand_wave"),
    ("Heart Me",          "❤️", 10,     "text", "heart_me"),
    ("Rosa",              "🌷", 10,     "text", "rosa"),
    ("White Rose",        "🤍", 10,     "text", "white_rose"),
    ("Birthday Cake",     "🎂", 10,     "text", "birthday_cake"),
    ("Music Album",       "🎶", 10,     "text", "music_album"),
    ("Perfume",           "🧴", 20,     "text", "perfume"),
    ("Doughnut",          "🍩", 30,     "text", "doughnut"),
    ("Pumpkin",           "🎃", 30,     "text", "pumpkin"),
    ("Rainbow",           "🌈", 50,     "text", "rainbow"),
    ("Slay",              "💅", 50,     "text", "slay"),
    ("Hat and Mustache",  "🎩", 99,     "text", "hat_and_mustache"),
    ("Go Popular",        "📈", 99,     "text", "go_popular"),
    ("Sunglasses",        "🕶️", 199,    "text", "sunglasses"),
    ("Lightning Bolt",    "⚡", 199,    "text", "lightning_bolt"),
    ("Fireworks",         "🎆", 108,    "text", "fireworks"),
    ("Traveler",          "🧳", 399,    "text", "traveler"),

    # ==================== FX GIFTS — RẺ (100-1200 coin) ====================
    ("Super GG",          "🎮",  100,    "fx", "super_gg"),
    ("Game Controller",   "🎮",  100,    "fx", "game_controller"),
    ("Corgi",             "🐕",  299,    "fx", "corgi"),
    ("Money Gun",         "💸",  500,    "fx", "money_gun"),
    ("Swan",              "🦢",  699,    "fx", "swan"),
    ("Fire Phoenix",      "🔥",  888,    "fx", "fire_phoenix"),
    ("Interstellar",      "🌠",  999,    "fx", "interstellar"),
    ("Galaxy",            "🌌",  1000,   "fx", "galaxy"),
    ("Fairy Wings",       "🧚",  1088,   "fx", "fairy_wings"),
    ("Gaming Console",    "🕹️", 1200,   "fx", "gaming_console"),

    # ==================== FX GIFTS — TRUNG (1500-5000 coin) ====================
    ("Private Jet",       "✈️", 1500,   "fx", "private_jet"),
    ("Castle",            "🏰", 1999,   "fx", "castle"),
    ("Sports Car",        "🏎️", 3000,   "fx", "sports_car"),
    ("Drama Queen",       "🎭", 5000,   "fx", "drama_queen"),
    ("Yacht",             "🛥️", 5000,   "fx", "yacht"),

    # ==================== FX GIFTS — CAO CẤP (10000+ coin) ====================
    ("Rocket",            "🚀", 10000,  "fx", "rocket"),
    ("Diamond Ring",      "💍", 15000,  "fx", "diamond_ring"),
    ("Gaming Console Pro","🎮", 15000,  "fx", "gaming_console_pro"),
    ("Crown",             "👑", 29999,  "fx", "crown"),
    ("Lion",              "🦁", 29999,  "fx", "lion"),
    ("Golden Lion",       "👑", 39999,  "fx", "golden_lion"),
    ("TikTok Universe",   "💫", 44999,  "fx", "tiktok_universe"),
]


# ============================================================
# HELPERS
# ============================================================
def get_gift_names():
    return [g[0] for g in GIFTS]


def find_gift(name):
    for g in GIFTS:
        if g[0] == name:
            return g
    return None


def get_points(name):
    g = find_gift(name)
    return g[2] if g else 0


def get_icon(name):
    g = find_gift(name)
    return g[1] if g else "🎁"


def get_effect(name):
    g = find_gift(name)
    return g[3] if g else "text"


def get_folder(name):
    g = find_gift(name)
    return g[4] if g else ""


def gift_from_points(points: int):
    """Find the closest gift <= points."""
    chosen = GIFTS[0]
    for g in GIFTS:
        if points >= g[2]:
            chosen = g
    return chosen


def list_fx_gifts():
    """Return list of FX gifts (need animation folder)."""
    return [(g[0], g[1], g[2], g[4]) for g in GIFTS if g[3] == "fx"]


def list_text_gifts():
    """Return list of text-only gifts."""
    return [(g[0], g[1], g[2], g[4]) for g in GIFTS if g[3] == "text"]