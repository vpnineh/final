import requests
import base64
import yaml

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir",
    "https://drive.google.com/uc?export=download&id=1-EopH8hKLwaRJ3kxm3-40x4CZQ3prAzP",
    "https://github.com/mifeng8901/sub/raw/refs/heads/main/2025/3/03-28-17-20.yaml",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub"
]

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except Exception:
        return False

def decode_base64(content):
    try:
        return base64.b64decode(content).decode(errors="ignore")
    except Exception:
        return content

def extract_links_from_yaml(yaml_text):
    links = []
    try:
        config = yaml.safe_load(yaml_text)
        proxies = config.get("proxies", [])
        for proxy in proxies:
            name = proxy.get("name", "")
            type_ = proxy.get("type")
            server = proxy.get("server")
            port = proxy.get("port")
            tls = proxy.get("tls", "")
            network = proxy.get("network", "tcp")
            uuid = proxy.get("uuid", "")
            cipher = proxy.get("cipher", "")
            password = proxy.get("password", "")
            sni = proxy.get("sni", "")

            if type_ == "vmess":
                obj = {
                    "v": "2",
                    "ps": name,
                    "add": server,
                    "port": str(port),
                    "id": uuid,
                    "aid": str(proxy.get("alterId", 0)),
                    "net": network,
                    "type": "none",
                    "host": sni,
                    "path": proxy.get("ws-opts", {}).get("path", "") if network == "ws" else "",
                    "tls": tls
                }
                vmess_json = base64.b64encode(
                    str.encode(str(obj).replace("'", '"'))
                ).decode()
                links.append(f"vmess://{vmess_json}")

            elif type_ == "trojan":
                link = f"trojan://{password}@{server}:{port}"
                params = []
                if sni:
                    params.append(f"sni={sni}")
                full = link + ("?" + "&".join(params) if params else "") + f"#{name}"
                links.append(full)

            elif type_ == "ss":
                userinfo = base64.b64encode(f"{cipher}:{password}".encode()).decode().rstrip("=")
                link = f"ss://{userinfo}@{server}:{port}#{name}"
                links.append(link)

            elif type_ == "vless":
                params = []
                if tls:
                    params.append(f"security={tls}")
                if sni:
                    params.append(f"sni={sni}")
                if network:
                    params.append(f"type={network}")
                    if network == "ws":
                        path = proxy.get("ws-opts", {}).get("path", "")
                        host = proxy.get("ws-opts", {}).get("headers", {}).get("Host", "")
                        if path:
                            params.append(f"path={path}")
                        if host:
                            params.append(f"host={host}")
                    elif network == "http":
                        path = proxy.get("http-opts", {}).get("path", "")
                        host = proxy.get("http-opts", {}).get("headers", {}).get("Host", "")
                        if path:
                            params.append(f"path={path}")
                        if host:
                            params.append(f"host={host}")
                    elif network == "grpc":
                        service_name = proxy.get("grpc-opts", {}).get("serviceName", "")
                        if service_name:
                            params.append(f"serviceName={service_name}")

                param_str = "&".join(params)
                link = f"vless://{uuid}@{server}:{port}?{param_str}#{name}"
                links.append(link)
    except Exception as e:
        print(f"⚠️ خطا در پردازش YAML: {e}")
    return links

def fetch_and_parse(url):
    try:
        print(f"📥 دریافت: {url}")
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        content = res.text.strip()

        if url.endswith((".yaml", ".yml")):
            return extract_links_from_yaml(content)

        if is_base64(content):
            print("🔍 base64 شناسایی شد")
            content = decode_base64(content)

        lines = []
        for line in content.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
        return lines
    except Exception as e:
        print(f"❌ خطا: {e}")
        return []

def main():
    unique_configs = {}

    for url in config_urls:
        lines = fetch_and_parse(url)
        for line in lines:
            key = line.split('#')[0].strip()
            if key not in unique_configs:
                unique_configs[key] = line

    result_lines = list(unique_configs.values())
    with open("sub", "w", encoding="utf-8") as f:
        f.write('\n'.join(result_lines))

    print(f"✅ sub ذخیره شد ({len(result_lines)} کانفیگ یکتا)")

if __name__ == "__main__":
    main()