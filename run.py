import requests
import base64

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir",
#    "https://drive.google.com/uc?export=download&id=1-EopH8hKLwaRJ3kxm3-40x4CZQ3prAzP",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub"
]

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def fetch_and_decode(url):
    try:
        print(f"📥 دریافت: {url}")
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        content = res.text.strip()
        if is_base64(content):
            print("🔍 base64 شناسایی شد")
            return base64.b64decode(content).decode(errors="ignore")
        return content
    except Exception as e:
        print(f"❌ خطا: {e}")
        return ""

def main():
    unique_configs = {}
    
    for url in config_urls:
        data = fetch_and_decode(url)
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            key = line.split('#')[0].strip()
            if key not in unique_configs:
                unique_configs[key] = line

    result_lines = list(unique_configs.values())
    
    # ذخیره کانفیگ‌ها
    with open("sub", "w", encoding="utf-8") as f:
        f.write('\n'.join(result_lines))
    
    print(f"✅ sub ذخیره شد ({len(result_lines)} کانفیگ یکتا)")

    # ذخیره لینک Google Drive در فایل esi
    drive_url = "https://drive.google.com/uc?export=download&id=1-EopH8hKLwaRJ3kxm3-40x4CZQ3prAzP"
    with open("esi", "w", encoding="utf-8") as f:
        f.write(drive_url)
    print("📄 لینک drive در فایل esi ذخیره شد.")

if __name__ == "__main__":
    main()
