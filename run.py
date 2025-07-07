import requests
import base64

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir"
]

def is_base64(s):
    try:
        # Base64 باید فقط یک خط باشه
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def fetch_and_decode(url):
    try:
        print(f"📥 در حال دریافت: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text.strip()

        # اگر بیس۶۴ بود، دیکود کنیم
        if is_base64(content):
            print("🔍 محتوای base64 شناسایی شد")
            decoded = base64.b64decode(content).decode(errors="ignore")
            return decoded
        else:
            return content
    except Exception as e:
        print(f"❌ خطا در دریافت {url}: {e}")
        return ""

def main():
    all_lines = set()

    for url in config_urls:
        data = fetch_and_decode(url)
        lines = data.splitlines()
        for line in lines:
            line = line.strip()
            if line:  # حذف خطوط خالی
                all_lines.add(line)

    if all_lines:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(sorted(all_lines)))
        print(f"✅ فایل ساخته شد: sub.txt ({len(all_lines)} کانفیگ)")
    else:
        print("⚠️ هیچ داده‌ای برای نوشتن وجود ندارد")

if __name__ == "__main__":
    main()