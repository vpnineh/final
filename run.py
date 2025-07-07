import requests
import base64

# لینک‌های مستقیم به فایل کانفیگ (متنی یا base64)
config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir"
]

def download_config(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.strip()

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def decode_if_base64(s):
    if is_base64(s):
        print("🔍 محتوای base64 شناسایی شد، در حال دیکود...")
        return base64.b64decode(s).decode(errors='ignore')
    return s

def merge_and_clean(config_texts):
    all_lines = []
    for text in config_texts:
        lines = text.strip().splitlines()
        all_lines.extend(lines)

    # حذف خطوط خالی و تکراری
    unique_lines = sorted(set(line.strip() for line in all_lines if line.strip()))
    return '\n'.join(unique_lines)

def encode_to_base64(content):
    encoded = base64.b64encode(content.encode()).decode()
    return encoded

def save_to_file(content, filename="sub"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    configs = []
    for url in config_urls:
        try:
            print(f"📥 در حال دریافت: {url}")
            text = download_config(url)
            decoded = decode_if_base64(text)
            configs.append(decoded)
        except Exception as e:
            print(f"❌ خطا در دریافت {url}: {e}")

    if configs:
        print("🔧 در حال ادغام و حذف تکراری‌ها...")
        merged = merge_and_clean(configs)
        print("🔐 در حال انکد خروجی به base64...")
        encoded = encode_to_base64(merged)
        save_to_file(encoded)
        print("✅ فایل نهایی base64 ذخیره شد: sub")
    else:
        print("⚠️ هیچ کانفیگی دریافت نشد.")

if __name__ == "__main__":
    main()