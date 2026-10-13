"""Boss system — HP, Robux, gift theo cấp số nhân. Tùy chỉnh từ GUI."""

DEFAULT_HP_BASE = 500
DEFAULT_HP_MULTIPLIER = 2.0
DEFAULT_ROBUX_BASE = 100
DEFAULT_ROBUX_MULTIPLIER = 2.0
DEFAULT_GIFT_BASE = 1
DEFAULT_GIFT_MULTIPLIER = 2.0
DEFAULT_GIFT_MAX = 100_000
MAX_LEVEL = 15

BOSS_NAMES = [
    {"level": 1,  "name": "SLIME",       "emoji": "🟢"},
    {"level": 2,  "name": "GOBLIN",      "emoji": "👺"},
    {"level": 3,  "name": "DEMON KING",  "emoji": "👹"},
    {"level": 4,  "name": "DRAGON",      "emoji": "🐉"},
    {"level": 5,  "name": "SKELETON",    "emoji": "💀"},
    {"level": 6,  "name": "GHOST",       "emoji": "👻"},
    {"level": 7,  "name": "VAMPIRE",     "emoji": "🧛"},
    {"level": 8,  "name": "WEREWOLF",    "emoji": "🐺"},
    {"level": 9,  "name": "WITCH",       "emoji": "🧙"},
    {"level": 10, "name": "TITAN",       "emoji": "🗿"},
    {"level": 11, "name": "PHOENIX",     "emoji": "🔥"},
    {"level": 12, "name": "LEVIATHAN",   "emoji": "🐙"},
    {"level": 13, "name": "GOD OF WAR",  "emoji": "⚔️"},
    {"level": 14, "name": "COSMIC",      "emoji": "🌌"},
    {"level": 15, "name": "OMEGA",       "emoji": "💫"},
]


def max_level():
    return MAX_LEVEL


def get_boss_name(level):
    level = max(1, min(level, MAX_LEVEL))
    return BOSS_NAMES[level - 1].copy()


def get_hp(level, base=DEFAULT_HP_BASE, multiplier=DEFAULT_HP_MULTIPLIER):
    level = max(1, level)
    return int(base * (multiplier ** (level - 1)))


def get_robux_reward(level, base=DEFAULT_ROBUX_BASE, multiplier=DEFAULT_ROBUX_MULTIPLIER):
    level = max(1, level)
    return int(base * (multiplier ** (level - 1)))


def get_gift_count(level, base=DEFAULT_GIFT_BASE, multiplier=DEFAULT_GIFT_MULTIPLIER,
                   max_count=DEFAULT_GIFT_MAX):
    level = max(1, level)
    count = int(base * (multiplier ** (level - 1)))
    return min(count, max_count)


def preview_all(hp_base, hp_mult, robux_base, robux_mult,
                gift_base, gift_mult, gift_max, levels=5):
    rows = []
    for lv in range(1, levels + 1):
        b = get_boss_name(lv)
        rows.append({
            "level": lv,
            "name": b["name"],
            "emoji": b["emoji"],
            "hp": get_hp(lv, hp_base, hp_mult),
            "robux": get_robux_reward(lv, robux_base, robux_mult),
            "gift": get_gift_count(lv, gift_base, gift_mult, gift_max),
        })
    return rows