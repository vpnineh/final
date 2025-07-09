import requests
import base64
import urllib.request 
urllib.request.urlretrieve("https://drive.google.com/uc?export=download&id=1-EopH8hKLwaRJ3kxm3-40x4CZQ3prAzP", "esi.txt")

# Open the source text files
file1 = open('esi.txt', 'r')

# Read the contents of the text files
content1 = file1.read()

# Close the source text files
file1.close()

# Open the destination file
destination_file = open('esi', 'w')

# Write the concatenated content to the destination file
destination_file.write(content1)
# Close the destination file
destination_file.close()


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
             
if __name__ == "__main__":
    main()
