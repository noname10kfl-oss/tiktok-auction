"""
Tải 60 avatar 200x200 cho bot.
Folder đích: assets/bots/avatars (đã có sẵn).
"""
import io
import sys
import time
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Chưa cài Pillow")
    print("   Chạy: uv add Pillow")
    sys.exit(1)


# ============================================================
# CẤU HÌNH
# ============================================================
COUNT = 60
SIZE = (200, 200)
DELAY = 0.5

# ★ Folder có sẵn
OUTPUT_DIR = Path(r"C:\Users\ACER\tiktok-auction\assets\bots\avatars")

FILE_PATTERN = "avatar_{:02d}.png"

# Nguồn ảnh
IMAGE_URL_TEMPLATE = "https://picsum.photos/seed/avatar{num}/400/400"


# ============================================================
# FUNCTIONS
# ============================================================
def download_image(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "image/*,*/*;q=0.8",
        }
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def process_and_save(data: bytes, filepath: Path, size=(200, 200)) -> bool:
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize(size, Image.LANCZOS)

        img.save(filepath, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"❌ Lỗi xử lý ảnh: {e}")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    if not OUTPUT_DIR.exists():
        print(f"❌ Không tìm thấy folder: {OUTPUT_DIR}")
        sys.exit(1)

    print("=" * 60)
    print("📥 TẢI AVATAR CHO BOT")
    print("=" * 60)
    print(f"📁 Folder:     {OUTPUT_DIR}")
    print(f"📐 Kích thước: {SIZE[0]}×{SIZE[1]} px")
    print(f"🔢 Số lượng:   {COUNT}")
    print(f"🌐 Nguồn:      {IMAGE_URL_TEMPLATE}")
    print("=" * 60)
    print()

    success = 0
    skipped = 0
    failed = 0

    for i in range(1, COUNT + 1):
        filename = FILE_PATTERN.format(i)
        filepath = OUTPUT_DIR / filename

        if filepath.exists():
            size_kb = filepath.stat().st_size // 1024
            print(f"[{i:2d}/{COUNT}] ⏭  Đã có {filename} ({size_kb} KB)")
            skipped += 1
            continue

        url = IMAGE_URL_TEMPLATE.format(num=i)

        for attempt in range(3):
            try:
                print(f"[{i:2d}/{COUNT}] ⬇️  Đang tải {filename}...",
                      end=" ", flush=True)

                data = download_image(url)

                if process_and_save(data, filepath, SIZE):
                    size_kb = filepath.stat().st_size // 1024
                    print(f"✅ {size_kb} KB")
                    success += 1
                    time.sleep(DELAY)
                    break
                else:
                    print("❌ Lỗi xử lý")
                    failed += 1
                    break

            except Exception as e:
                if attempt < 2:
                    print(f"⚠️  Thử lại ({attempt + 1}/3)...")
                    time.sleep(1.5)
                else:
                    print(f"❌ Thất bại: {e}")
                    failed += 1

    print()
    print("=" * 60)
    print("📊 KẾT QUẢ")
    print("=" * 60)
    print(f"✅ Thành công:   {success}")
    print(f"⏭️  Bỏ qua:       {skipped}")
    print(f"❌ Lỗi:          {failed}")

    total = len([
        f for f in OUTPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in
        {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    ])
    print(f"🖼️  Tổng avatar:  {total} ảnh")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Đã dừng")
        sys.exit(0)