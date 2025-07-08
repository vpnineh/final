import requests, base64, yaml, os, subprocess, time, json

config_urls = [
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/b",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/backk%20up%20new",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/family",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/freind",
    "https://github.com/Aa64n/Aa64n-/raw/refs/heads/main/wir"
]

SBOX="./sing-box"  # یا مسیر کامل به فایل sing-box
PORT=1081
TARGET="https://www.gstatic.com/generate_204"

def is_base64(s):
    try: return base64.b64encode(base64.b64decode(s)).decode().strip('=') == s.strip('=')
    except: return False

def extract_links_from_yaml(txt):
    links=[]
    cfg=yaml.safe_load(txt)
    for p in cfg.get("proxies",[]):
        name=p.get("name","")
        sv=p.get("server"); pt=p.get("port")
        ty=p.get("type")
        tls=p.get("tls",""); net=p.get("network","tcp")
        uuid=p.get("uuid",""); cipher=p.get("cipher",""); pwd=p.get("password","")
        sni=p.get("sni","")
        if ty=="vmess":
            obj={"v":"2","ps":name,"add":sv,"port":str(pt),"id":uuid,"aid":str(p.get("alterId",0)),
                 "net":net,"type":"none","host":sni,"path":(p.get("ws-opts",{}).get("path","")if net=="ws" else ""),"tls":tls}
            j=base64.b64encode(json.dumps(obj).encode()).decode()
            links.append(f"vmess://{j}#{name}")
        elif ty=="vless":
            params=[f"security={tls}"] if tls else []
            if net: params.append(f"type={net}")
            if net=="ws":
                wso=p.get("ws-opts",{}); 
                if wso.get("path"): params.append(f"path={wso['path']}")
                if (h:=wso.get("headers",{}).get("Host","")): params.append(f"host={h}")
            if net=="http":
                ho=p.get("http-opts",{}); 
                if ho.get("path"): params.append(f"path={ho['path']}")
                if (h:=ho.get("headers",{}).get("Host","")): params.append(f"host={h}")
            if sni: params.append(f"sni={sni}")
            prm="&".join(params)
            links.append(f"vless://{uuid}@{sv}:{pt}?{prm}#{name}")
        elif ty=="ss":
            ui=base64.b64encode(f"{cipher}:{pwd}".encode()).decode().rstrip("=")
            links.append(f"ss://{ui}@{sv}:{pt}#{name}")
        elif ty=="trojan":
            q=f"?sni={sni}" if sni else ""
            links.append(f"trojan://{pwd}@{sv}:{pt}{q}#{name}")
    return links

def fetch_links(url):
    print("📥",url)
    txt=requests.get(url,timeout=15).text.strip()
    if url.endswith((".yaml",".yml")): return extract_links_from_yaml(txt)
    if is_base64(txt): return base64.b64decode(txt).decode().splitlines()
    return txt.splitlines()

def make_conf(link):
    return {"log":{"disabled":True},"inbounds":[{"type":"socks","listen":"127.0.0.1","port":PORT}],
            "outbounds":[{"protocol":"freedom"},"proxy"]}

def make_full_conf(link):
    # ساخت config واقعی بر اساس نوع پروتکل
    proto, rest = link.split("://",1)
    core={"log":{"disabled":True},"inbounds":[{"type":"socks","listen":"127.0.0.1","port":PORT}],"outbounds":[]}
    tag="AUTO"
    if proto=="vmess":
        conf=json.loads(base64.b64decode(rest.split("#")[0]).decode())
        c={"protocol":"vmess","settings":{"vnext":[{"address":conf["add"],"port":int(conf["port"]),
            "users":[{"id":conf["id"],"alterId":int(conf["aid"]),"security":conf["type"]}]}]},
           "streamSettings":{}}
        if conf["tls"]=="tls": c["streamSettings"]["security"]="tls"
        if conf["net"]=="ws":
            c["streamSettings"].setdefault("wsSettings",{})["path"]=conf["path"]
        core["outbounds"]=[c]
    elif proto=="vless":
        rest2, name = rest.split("#",1)
        addr, query = rest2.split("?",1)
        user,port=addr.split("@")[0],addr.split("@")[1].split(":")[0]
        host,port2 = addr.split("@")[1].split(":")
        qm=dict(q.split("=",1)for q in query.split("&"))
        c={"protocol":"vless","settings":{"clients":[{"id":user}]},"streamSettings":{"network":qm["type"]}}
        if qm.get("security")=="tls": c["streamSettings"]["security"]="tls"
        if qm["type"] in ("ws","http"):
            ss= {"path":qm.get("path",""),"headers":{"Host":qm.get("host","")}}
            c["streamSettings"][f"{qm['type']}Settings"]=ss
        core["outbounds"]=[c]
    elif proto=="ss":
        creds, hostport=rest.split("@")
        methods,passw=base64.b64decode(creds+"=").decode().split(":")
        host,pp=hostport.split("#")[0].split(":")
        c={"protocol":"shadowsocks","settings":{"servers":[{"address":host,"port":int(pp),
            "method":methods,"password":passw}]}}
        core["outbounds"]=[c]
    elif proto=="trojan":
        creds, rest2 = rest.split("@",1)
        hostport, qn=rest2.split("?")[0].split("#")[0],rest2.split("#")[1]
        host,pp=hostport.split(":")
        c={"protocol":"trojan","settings":{"clients":[{"password":creds}]},"streamSettings":{}}
        core["outbounds"]=[c]
    return core

def test(link):
    cfg=make_full_conf(link)
    open("temp.json","w").write(json.dumps(cfg))
    p = subprocess.Popen([SBOX,"run","-c","temp.json"])
    time.sleep(2)
    ok=False
    for i in range(3):
        try:
            r=requests.get(TARGET,timeout=5,proxies={"http":f"socks5h://127.0.0.1:{PORT}","https":f"socks5h://127.0.0.1:{PORT}"})
            if r.status_code==204:
                ok=True; break
        except: pass
    p.terminate()
    time.sleep(1)
    return ok

def main():
    links=[ln for url in config_urls for ln in fetch_links(url)]
    uniq={l.split("#")[0]:l for l in links}.values()
    ok=[]
    for l in uniq:
        print("🔍 تست",l.split("#")[0][:50])
        if test(l): ok.append(l)
    open("sub","w").write("\n".join(ok))
    print("✅ باقی:",len(ok))

if __name__=="__main__": main()
