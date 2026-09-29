#!/usr/bin/env python3
"""جمع‌آوری کانفیگ‌های رایگان از منابع عمومی، تست اتصال و ساخت فایل اشتراک."""
import base64
import datetime
import ipaddress
import json
import os
import re
import socket
import ssl
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

SOURCES = [
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",
]
PROTOCOLS = ("vless", "vmess", "trojan", "ss", "hysteria2", "hy2")
PER_PROTOCOL = {"vless": 60, "vmess": 20, "trojan": 20, "ss": 20, "hysteria2": 10, "hy2": 10}
CANDIDATES = 400
TIMEOUT = 3
RAW = "https://raw.githubusercontent.com/DrvpnTM/vpn/HEAD/"
CLOUDFLARE_SOURCE = SOURCES[0]  # Epodonios
CLOUDFLARE_COUNT = 50
WARP_ENDPOINTS_URL = "https://raw.githubusercontent.com/ircfspace/endpoint/main/ip.json"
WARP_DEFAULT = ["162.159.192.1:2408", "162.159.193.3:2408", "162.159.195.1:2408", "188.114.97.170:894"]
WARP_NOISE = "ifp=10-20&ifps=10-20&ifpd=1-2&ifpm=m4"
EGYPT_PROXIES_URL = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/EG/data.json"
EGYPT_COUNT = 20
CLOUDFLARE_NETS = [ipaddress.ip_network(n) for n in (
    "173.245.48.0/20 103.21.244.0/22 103.22.200.0/22 103.31.4.0/22 141.101.64.0/18 "
    "108.162.192.0/18 190.93.240.0/20 188.114.96.0/20 197.234.240.0/22 198.41.128.0/17 "
    "162.158.0.0/15 104.16.0.0/13 104.24.0.0/14 172.64.0.0/13 131.0.72.0/22").split()]


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            text = r.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"skip {url}: {e}")
        return []
    if "://" not in text[:2000]:
        try:
            text = base64.b64decode(text.strip() + "===").decode("utf-8", "ignore")
        except Exception:
            return []
    return [l.strip() for l in text.splitlines() if l.strip().startswith(tuple(p + "://" for p in PROTOCOLS))]


def endpoint(link):
    scheme, rest = link.split("://", 1)
    if scheme == "vmess":
        try:
            d = json.loads(base64.b64decode(rest.split("#")[0] + "===").decode())
            return d["add"], int(d["port"])
        except Exception:
            return None
    try:
        u = urllib.parse.urlsplit(link)
        return u.hostname, u.port
    except ValueError:
        return None


def alive(link):
    ep = endpoint(link)
    if not ep or not ep[0] or not ep[1]:
        return False
    if link.startswith(("hysteria2://", "hy2://")):
        return True  # UDP; can't cheaply test
    try:
        with socket.create_connection(ep, timeout=TIMEOUT):
            return True
    except OSError:
        return False


def is_cloudflare(link):
    ep = endpoint(link)
    try:
        ip = ipaddress.ip_address(ep[0])
    except (TypeError, ValueError):
        return False
    return any(ip in n for n in CLOUDFLARE_NETS)


def warp_links():
    try:
        with urllib.request.urlopen(WARP_ENDPOINTS_URL, timeout=30) as r:
            eps = json.load(r).get("ipv4", [])
    except Exception as e:
        print(f"warp endpoints: {e}")
        eps = []
    eps = list(dict.fromkeys(WARP_DEFAULT + eps))
    tag = "drvpn.net"
    header = [
        "//profile-title: base64:" + base64.b64encode(b"drvpn.net WARP").decode(),
        "//profile-update-interval: 1",
        "//profile-web-page-url: https://drvpntm.github.io/vpn/",
    ]
    # Hiddify chain syntax: "A -> B" means A connects through B (warp-in-warp)
    links = [f"warp://auto/?{WARP_NOISE}#{tag} -> warp://auto#{tag}"]
    links += [f"warp://@{ep}?{WARP_NOISE}#{tag}" for ep in eps]
    links += [f"warp://@{ep}?{WARP_NOISE}#{tag} -> warp://@{ep}#{tag}" for ep in eps[:4]]
    return header, links


def exit_country(proxy):
    """Tunnel through an HTTP/SOCKS5 proxy to Cloudflare and return the exit country it reports."""
    host, port, kind = proxy
    try:
        s = socket.create_connection((host, port), timeout=8)
        s.settimeout(10)
        if kind == "http":
            s.sendall(b"CONNECT www.cloudflare.com:443 HTTP/1.1\r\nHost: www.cloudflare.com:443\r\n\r\n")
            if b" 200" not in s.recv(4096).split(b"\r\n")[0]:
                return None
        else:  # socks5, no auth
            s.sendall(b"\x05\x01\x00")
            if s.recv(2) != b"\x05\x00":
                return None
            name = b"www.cloudflare.com"
            s.sendall(b"\x05\x01\x00\x03" + bytes([len(name)]) + name + (443).to_bytes(2, "big"))
            if s.recv(10)[1:2] != b"\x00":
                return None
        t = ssl.create_default_context().wrap_socket(s, server_hostname="www.cloudflare.com")
        t.sendall(b"GET /cdn-cgi/trace HTTP/1.1\r\nHost: www.cloudflare.com\r\nConnection: close\r\n\r\n")
        data = b""
        while chunk := t.recv(4096):
            data += chunk
        t.close()
        trace = dict(l.split("=", 1) for l in data.decode(errors="ignore").splitlines() if "=" in l)
        return trace.get("loc")
    except Exception:
        return None


def egypt_links():
    try:
        with urllib.request.urlopen(EGYPT_PROXIES_URL, timeout=30) as r:
            items = json.load(r)
    except Exception as e:
        print(f"egypt proxies: {e}")
        return []
    proxies = list(dict.fromkeys(
        (i["ip"], int(i["port"]), "http" if i["protocol"] == "http" else "socks5")
        for i in items if i.get("protocol") in ("http", "socks5")))
    with ThreadPoolExecutor(32) as pool:
        ok = [p for p, loc in zip(proxies, pool.map(exit_country, proxies)) if loc == "EG"]
    tag = "drvpn.net"
    warp = f"warp://auto/?{WARP_NOISE}#{tag}"
    # "A -> B": the Egyptian proxy (A) is the exit, reached through WARP (B)
    return [f"{'phttp' if k == 'http' else 'socks'}://{h}:{p}#{tag} -> {warp}" for h, p, k in ok[:EGYPT_COUNT]]


def rename(link):
    tag = "drvpn.net"
    if link.startswith("vmess://"):
        try:
            d = json.loads(base64.b64decode(link[8:].split("#")[0] + "===").decode())
            d["ps"] = tag
            return "vmess://" + base64.b64encode(json.dumps(d, ensure_ascii=False).encode()).decode()
        except Exception:
            return link
    return link.split("#")[0] + "#" + tag


def main():
    seen, by_proto = set(), {p: [] for p in PROTOCOLS}
    for src in SOURCES:
        for link in fetch(src):
            key = link.split("#")[0]
            if key in seen:
                continue
            seen.add(key)
            by_proto[link.split("://")[0]].append(link)

    result = []
    with ThreadPoolExecutor(64) as pool:
        for proto, links in by_proto.items():
            cands = links[:CANDIDATES]
            ok = [l for l, a in zip(cands, pool.map(alive, cands)) if a]
            result += ok[: PER_PROTOCOL[proto]]
            print(f"{proto}: {len(ok[: PER_PROTOCOL[proto]])}/{len(links)}")

    result = [rename(l) for l in result]
    body = "\n".join(result) + "\n"
    with open("sub.txt", "w") as f:
        f.write(body)
    with open("sub_base64.txt", "w") as f:
        f.write(base64.b64encode(body.encode()).decode())
    print(f"total: {len(result)}")

    os.makedirs("subs", exist_ok=True)
    groups = {"vless": ("vless",), "vmess": ("vmess",), "trojan": ("trojan",),
              "ss": ("ss",), "hysteria2": ("hysteria2", "hy2")}
    counts = {}
    for name, schemes in groups.items():
        links = [l for l in result if l.split("://")[0] in schemes]
        counts[name] = len(links)
        with open(f"subs/{name}.txt", "w") as f:
            f.write("\n".join(links) + "\n")

    cands = [l for l in fetch(CLOUDFLARE_SOURCE) if is_cloudflare(l)][:CANDIDATES]
    with ThreadPoolExecutor(64) as pool:
        cf = [rename(l) for l, a in zip(cands, pool.map(alive, cands)) if a][:CLOUDFLARE_COUNT]
    counts["cloudflare"] = len(cf)
    with open("subs/cloudflare.txt", "w") as f:
        f.write("\n".join(cf) + "\n")
    print(f"cloudflare: {len(cf)}")

    header, warp = warp_links()
    counts["warp"] = len(warp)
    with open("subs/warp.txt", "w") as f:
        f.write("\n".join(header + warp) + "\n")
    print(f"warp: {len(warp)}")

    egypt = egypt_links()
    counts["egypt"] = len(egypt)
    with open("subs/egypt.txt", "w") as f:
        f.write("\n".join(egypt) + "\n")
    print(f"egypt: {len(egypt)}")

    manifest = {
        "name": "drvpn.net free VPN subscription",
        "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "update_interval_minutes": 60,
        "total": len(result),
        "subscriptions": {
            "all": RAW + "sub.txt",
            "all_base64": RAW + "sub_base64.txt",
            **{name: RAW + f"subs/{name}.txt" for name in counts},
        },
        "counts": counts,
    }
    with open("subscriptions.json", "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
