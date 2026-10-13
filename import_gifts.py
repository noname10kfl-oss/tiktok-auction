"""
Import gift từ tiktok-gift-icons folder → gifts.py
Extract coins từ tên file + tên đẹp từ JSON.
Chạy: uv run python import_gifts.py
"""
import json
import re
import shutil
from pathlib import Path
from collections import Counter


# ═══════════════════════════════════════════════════════════
# CẤU HÌNH — SỬA ĐƯỜNG DẪN
# ═══════════════════════════════════════════════════════════

# Folder chứa file .webp
SRC_ICONS_DIR = Path("C:/Users/ACER/Downloads/tiktok-gift-icons/tiktok-gift-icons")

# File JSON (để lấy tên đẹp) — có thể bỏ qua nếu không cần
JSON_PATH = Path("C:/Users/ACER/Downloads/tiktok-gift-icons/tiktok-gifts.json")

# Folder đích
DST_ICONS_DIR = Path("C:/Users/ACER/tiktok-auction/assets/gift-icons-2")
FX_DIR = Path("C:/Users/ACER/tiktok-auction/assets/gift-effects")

# Output
OUTPUT = Path("C:/Users/ACER/tiktok-auction/gifts_generated.py")
STATS_OUTPUT = Path("C:/Users/ACER/tiktok-auction/gift_stats.txt")

# Lọc
MIN_COINS = 1
FILTER_REGION = None    # "VN" hoặc None


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def parse_filename(filename):
    """
    Parse tên file → (slug, coins).
    Format: <slug>-<coins>-coins.webp
    Ví dụ: dragon-flame-26999-coins.webp → ("dragon-flame", 26999)
    """
    stem = Path(filename).stem   # dragon-flame-26999-coins
    # Regex: slug-coins-coins
    m = re.match(r"^(.+?)-(\d+)-coins$", stem)
    if m:
        return m.group(1), int(m.group(2))
    return None, None


def slug_to_name(slug):
    """slug → tên đẹp: dragon-flame → Dragon Flame"""
    return " ".join(word.capitalize() for word in slug.split("-"))


def slug_to_folder(slug):
    """slug → folder: dragon-flame → dragon_flame"""
    return slug.replace("-", "_").lower()


def load_fx_files():
    files = {}
    if not FX_DIR.exists():
        return files
    for f in FX_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".webm", ".mp4", ".gif", ".json"}:
            files[f.stem.lower()] = f.name
    return files


def load_json_names():
    """Đọc JSON → dict {slug: name} để lấy tên đẹp."""
    if not JSON_PATH.exists():
        print(f"⚠️ Không có JSON: {JSON_PATH}")
        return {}
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        gifts = data.get("gifts", [])
        names = {}
        for g in gifts:
            slug = (g.get("slug") or "").strip().lower()
            name = (g.get("name") or "").strip()
            if slug and name:
                names[slug] = name
        print(f"✅ JSON có {len(names):,} tên gift")
        return names
    except Exception as e:
        print(f"⚠️ Lỗi JSON: {e}")
        return {}


def extract_gifts(src_dir, json_names):
    """Quét folder, extract gift từ tên file."""
    if not src_dir.exists():
        print(f"❌ Không tìm thấy folder: {src_dir}")
        return []

    result = []
    seen_slugs = set()

    for f in src_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in {".webp", ".png", ".jpg", ".jpeg", ".gif"}:
            continue

        slug, coins = parse_filename(f.name)
        if not slug or coins is None:
            continue
        if coins < MIN_COINS:
            continue

        slug_lower = slug.lower()
        if slug_lower in seen_slugs:
            continue
        seen_slugs.add(slug_lower)

        # Tên đẹp: ưu tiên từ JSON, fallback từ slug
        name = json_names.get(slug_lower, slug_to_name(slug))
        folder = slug_to_folder(slug)

        result.append({
            "name": name,
            "slug": slug,
            "coins": coins,
            "folder": folder,
            "file": f.name,
        })

    # Sắp xếp theo coins tăng dần
    result.sort(key=lambda g: (g["coins"], g["name"].lower()))
    return result


def copy_icons(gifts, src_dir):
    """Copy file ảnh sang folder đích."""
    DST_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for g in gifts:
        src = src_dir / g["file"]
        # Đổi tên theo folder (bỏ -coins.webp)
        dst = DST_ICONS_DIR / f"{g['folder']}.webp"
        if src.exists():
            shutil.copy2(src, dst)
            copied += 1
    return copied


def detect_effect(folder, fx_files):
    for key in [folder, folder.replace("_", ""), folder.replace("_", "-")]:
        if key.lower() in fx_files:
            return "fx"
    return "text"


def generate_gifts_py(gifts, fx_files):
    lines = [
        '"""',
        'TikTok gift list — TỰ ĐỘNG SINH từ tiktok-gift-icons.',
        f'Tổng: {len(gifts):,} gift',
        'Format: (name, icon, points, effect_type, folder)',
        'effect_type:',
        '  "fx"   = quà lớn, phát file animation (webm/gif/lottie)',
        '  "text" = quà nhỏ, chỉ hiện chữ',
        '"""',
        'import re',
        '',
        '',
        'GIFTS = [',
    ]

    for g in gifts:
        name = g["name"].replace('"', '\\"')
        coins = g["coins"]
        folder = g["folder"]
        effect = detect_effect(folder, fx_files)
        icon = "🎁"

        lines.append(
            f'    ("{name}", "{icon}", {coins}, "{effect}", "{folder}"),'
        )

    lines.extend([
        "]",
        "",
        "",
        "# ═══════════════════════════════════════════════════════════",
        "# HELPERS",
        "# ═══════════════════════════════════════════════════════════",
        "",
        "def _norm(s):",
        '    return re.sub(r"[^a-z0-9]", "", str(s).lower())',
        "",
        "",
        "def find_gift(name):",
        "    if not name:",
        "        return None",
        "    target = _norm(name)",
        "    for g in GIFTS:",
        "        if _norm(g[0]) == target:",
        "            return g",
        "    return None",
        "",
        "",
        "def gift_from_points(points):",
        "    if not GIFTS:",
        "        return None",
        "    chosen = GIFTS[0]",
        "    for g in GIFTS:",
        "        if points >= g[2]:",
        "            chosen = g",
        "    return chosen",
        "",
        "",
        "def get_points(name):",
        "    g = find_gift(name)",
        "    return g[2] if g else 0",
        "",
        "",
        "def get_icon(name):",
        "    g = find_gift(name)",
        "    return g[1] if g else '🎁'",
        "",
        "",
        "def get_effect(name):",
        "    g = find_gift(name)",
        "    return g[3] if g else 'text'",
        "",
        "",
        "def get_folder(name):",
        "    g = find_gift(name)",
        "    return g[4] if g else ''",
        "",
        "",
        "def list_fx_gifts():",
        "    return [(g[0], g[1], g[2], g[4]) for g in GIFTS if g[3] == 'fx']",
        "",
        "",
        "def list_text_gifts():",
        "    return [(g[0], g[1], g[2], g[4]) for g in GIFTS if g[3] == 'text']",
    ])

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Đã sinh: {OUTPUT}")
    print(f"   Tổng: {len(gifts):,} gift")


def write_stats(gifts, fx_files, copied):
    lines = []
    lines.append("=" * 70)
    lines.append("📊 THỐNG KÊ GIFT IMPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"📦 Tổng gift:       {len(gifts):,}")
    lines.append(f"📁 Ảnh copy được:   {copied:,}")
    lines.append(f"📁 FX có sẵn:       {len(fx_files):,}")
    lines.append("")

    # FX vs Text
    fx_count = 0
    text_count = 0
    fx_gifts = []
    for g in gifts:
        if detect_effect(g["folder"], fx_files) == "fx":
            fx_count += 1
            fx_gifts.append(g)
        else:
            text_count += 1

    lines.append(f"🎆 FX gift:         {fx_count:,}")
    lines.append(f"📝 Text gift:       {text_count:,}")
    lines.append("")

    # Phân bố coins
    lines.append("─" * 70)
    lines.append("💰 PHÂN BỐ THEO COINS")
    lines.append("─" * 70)
    counter = Counter(g["coins"] for g in gifts)
    for coins in sorted(counter.keys()):
        lines.append(f"   {coins:>10,} coins: {counter[coins]:>5,} gift")
    lines.append("")

    # FX gift đã có
    lines.append("─" * 70)
    lines.append(f"✅ FX GIFT ĐÃ CÓ FILE WEBM ({len(fx_gifts)} gift)")
    lines.append("─" * 70)
    lines.append("")
    for g in fx_gifts:
        lines.append(f"   ✅ {g['name']:<40} {g['coins']:>8,} coins")
    lines.append("")

    # Gift giá cao CẦN thêm FX
    lines.append("─" * 70)
    lines.append("🎯 TOP 100 GIFT GIÁ CAO — NÊN THÊM FX")
    lines.append("─" * 70)
    lines.append("")

    high_value = [g for g in gifts if g["coins"] >= 1000]
    high_value.sort(key=lambda g: -g["coins"])

    lines.append(f"★ Gift ≥ 1000 coins: {len(high_value):,}")
    lines.append("")
    for g in high_value[:100]:
        has_fx = "✅" if detect_effect(g["folder"], fx_files) == "fx" else "❌"
        lines.append(
            f"   {has_fx} {g['name']:<40} {g['coins']:>10,} coins  "
            f"→ {g['folder']}.webm"
        )

    lines.append("")
    lines.append("─" * 70)
    lines.append("📁 DANH SÁCH FILE WEBM CẦN THÊM VÀO assets/gift-effects/")
    lines.append("─" * 70)
    lines.append("")

    fx_needed = [g for g in high_value[:100]
                 if detect_effect(g["folder"], fx_files) != "fx"]

    for g in fx_needed:
        lines.append(f"   {g['folder']}.webm")

    lines.append("")
    lines.append("=" * 70)

    STATS_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Đã ghi stats: {STATS_OUTPUT}")


def main():
    print("=" * 70)
    print("🎁 IMPORT GIFT TỪ tiktok-gift-icons")
    print("=" * 70)
    print()

    # Load
    json_names = load_json_names()
    fx_files = load_fx_files()
    print(f"📁 FX files: {len(fx_files):,}")

    # Extract
    gifts = extract_gifts(SRC_ICONS_DIR, json_names)
    if not gifts:
        print("❌ Không tìm thấy gift nào")
        return

    print()
    print(f"📋 Preview 15 gift đầu:")
    print(f"   {'Tên':<40} {'Coins':>10}")
    print("   " + "─" * 52)
    for g in gifts[:15]:
        print(f"   {g['name']:<40} {g['coins']:>10,}")
    if len(gifts) > 15:
        print(f"   ... và {len(gifts) - 15:,} gift khác")

    print()
    print("📊 Phân bố coins (top 20 mức):")
    counter = Counter(g["coins"] for g in gifts)
    for coins in sorted(counter.keys())[:20]:
        print(f"   {coins:>10,} coins: {counter[coins]:>5,} gift")
    if len(counter) > 20:
        print(f"   ... và {len(counter) - 20} mức khác")

    print()
    ans = input("❓ Tiếp tục? Copy ảnh + sinh file? (y/n): ").strip().lower()
    if ans != "y":
        print("⏹ Đã hủy")
        return

    # Copy icons
    print()
    print("📁 Đang copy ảnh...")
    copied = copy_icons(gifts, SRC_ICONS_DIR)
    print(f"   ✅ Copy được: {copied:,}")

    # Sinh gifts.py
    generate_gifts_py(gifts, fx_files)

    # Stats
    write_stats(gifts, fx_files, copied)

    print()
    print("=" * 70)
    print("📝 BƯỚC TIẾP THEO")
    print("=" * 70)
    print()
    print("1. Backup + thay gifts.py:")
    print("   copy gifts.py gifts.py.bak")
    print("   copy gifts_generated.py gifts.py")
    print()
    print("2. Xem stats:")
    print(f"   notepad {STATS_OUTPUT}")
    print()
    print("3. Restart app:")
    print("   uv run python app.py")
    print()


if __name__ == "__main__":
    main()