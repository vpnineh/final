import requests
import base64
import yaml
import re
import json
import subprocess
import time
import tempfile
import os

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir",
    "https://drive.google.com/uc?export=download&id=1-EopH8hKLwaRJ3kxm3-40x4CZQ3prAzP",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub"
]

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def is_yaml(content):
    return any(x in content.lower() for x in ["proxies:", "- name:", "server:"])

def extract_links(text):
    links = re.findall(r'(?:vmess|vless)://[^\s]+', text)
    return links

def parse_yaml(yaml_content):
    try:
        data = yaml.safe_load(yaml_content)
        proxies = data.get("proxies", [])
        links = []
        for proxy in proxies:
            if proxy["type"] == "vmess":
                vmess_data = {
                    "v": "2",
                    "ps": proxy.get("name", ""),
                    "add": proxy["server"],
                    "port": proxy["port"],
                    "id": proxy["uuid"],
                    "aid": proxy.get("alterId", 0),
                    "net": proxy.get("network", "tcp"),
                    "type": proxy.get("headerType", ""),
                    "host": proxy.get("host", ""),
                    "path": proxy.get("path", ""),
                    "tls": proxy.get("tls", "")
                }
                vmess_b64 = base64.b64encode(json.dumps(vmess_data).encode()).decode()
                links.append("vmess://" + vmess_b64)
            elif proxy["type"] == "vless":
                link = f"vless://{proxy['uuid']}@{proxy['server']}:{proxy['port']}?encryption=none"
                if proxy.get("tls") == "reality":
                    link += f"&security=reality&sni={proxy.get('sni','')}"
                elif proxy.get("tls"):
                    link += f"&security=tls&sni={proxy.get('sni','')}"
                if proxy.get("network") == "grpc":
                    link += "&type=grpc&serviceName=" + proxy.get("grpc-opts", {}).get("grpc-service-name", "")
                links.append(link)
        return links
    except Exception as e:
        print("❌ YAML parse error:", e)
        return []

def fetch_and_decode(url):
    try:
        print(f"📥 دریافت: {url}")
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        content = res.text.strip()
        if is_base64(content):
            print("🔍 base64 شناسایی شد")
            content = base64.b64decode(content).decode(errors="ignore")
        if is_yaml(content):
            print("📦 تبدیل YAML به لینک...")
            return parse_yaml(content)
        return extract_links(content)
    except Exception as e:
        print(f"❌ خطا: {e}")
        return []

def parse_link(link):
    if link.startswith("vmess://"):
        try:
            raw = base64.b64decode(link[8:]).decode()
            return json.loads(raw)
        except: return None
    elif link.startswith("vless://") or link.startswith("http://vless://") or link.startswith("https://vless://"):
        link = link.replace("http://", "").replace("https://", "")
        m = re.match(r'vless://([^@]+)@([^:]+):(\d+)', link)
        if not m: return None
        query = dict(re.findall(r'([\w\-]+)=([^&]+)', link.split('?')[1]) if '?' in link else [])
        return {
            "type": "vless",
            "id": m.group(1),
            "add": m.group(2),
            "port": m.group(3),
            "security": query.get("security", ""),
            "sni": query.get("sni", ""),
            "flow": query.get("flow", ""),
            "typex": query.get("type", "")
        }
    return None

def make_full_conf(link):
    conf = parse_link(link)
    if not conf: return None
    if link.startswith("vmess://"):
        return {
            "log": {"level": "error"},
            "inbounds": [{
                "type": "socks",
                "listen": "127.0.0.1",
                "listen_port": 10808
            }],
            "outbounds": [{
                "type": "vmess",
                "server": conf["add"],
                "server_port": int(conf["port"]),
                "uuid": conf["id"],
                "alterId": int(conf.get("aid", 0)),
                "security": conf.get("type", "auto")
            }]
        }
    elif link.startswith("vless://"):
        return {
            "log": {"level": "error"},
            "inbounds": [{
                "type": "socks",
                "listen": "127.0.0.1",
                "listen_port": 10808
            }],
            "outbounds": [{
                "type": "vless",
                "server": conf["add"],
                "server_port": int(conf["port"]),
                "uuid": conf["id"],
                "flow": conf.get("flow", ""),
                "tls": {
                    "enabled": conf.get("security", "") in ["tls", "reality"],
                    "server_name": conf.get("sni", "")
                },
                "packet_encoding": "xudp" if conf.get("typex") == "grpc" else "none"
            }]
        }
    return None

def test(link):
    cfg = make_full_conf(link)
    if not cfg: return False
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".json", delete=False) as f:
        json.dump(cfg, f)
        f.flush()
        result = 0
        for i in range(3):
            try:
                p = subprocess.Popen(["./bin/sing-box", "run", "-c", f.name],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                time.sleep(1.5)
                r = requests.get("http://127.0.0.1:10808/http://gstatic.com/generate_204", timeout=3)
                if r.status_code == 204:
                    result += 1
                p.terminate()
            except:
                try: p.terminate()
                except: pass
        os.unlink(f.name)
        return result >= 1

def main():
    all_links = []
    for url in config_urls:
        links = fetch_and_decode(url)
        all_links.extend(links)

    print(f"🔗 مجموع لینک‌ها: {len(all_links)}")

    # حذف تکراری‌ها
    seen = {}
    for l in all_links:
        key = l.split('#')[0].strip()
        if key not in seen:
            seen[key] = l
    filtered = list(seen.values())
    print(f"🧹 پس از حذف تکراری: {len(filtered)}")

    ok = []
    for l in filtered:
        print("🔍 تست", l[:50])
        if test(l):
            ok.append(l)

    print(f"✅ نهایی: {len(ok)} کانفیگ سالم")

    with open("sub", "w", encoding="utf-8") as f:
        f.write('\n'.join(ok))

if __name__ == "__main__":
    main()
