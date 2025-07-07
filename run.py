import requests
import base64

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir"
]

def is_base64_string(s):
    try:
        # اگر رشته فقط یک خطه و احتمال Base64 بالا بود
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def fetch_and_decode(url):
    try:
        print(f"📥 گرفتن: {url}")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        content = res.text.strip()
        if is_base64_string(content):
            print("🔍 دیکود Base64")
            decoded = base64.b64decode(content).decode(errors="ignore")
            return decoded
        return content
    except Exception as e:
        print(f"❌ خطا در دریافت {url}: {e}")
        return ""

def main():
    all_lines = set()

    for url in config_urls:
        data = fetch_and_decode(url)
        for line in data.strip().splitlines():
            line = line.strip()
            if line:  # حذف خطوط خالی
                all_lines.add(line)

    if all_lines:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(sorted(all_lines)))
        print(f"✅ ذخیره شد: sub.txt ({len(all_lines)} خط)")
    else:
        print("⚠️ هیچ کانفیگی دریافت نشد.")

if __name__ == "__main__":
    main()