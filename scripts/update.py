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
COUNTRY_NETS_URL = "https://raw.githubusercontent.com/ipverse/rir-ip/master/country/{}/ipv4-aggregated.txt"
EGYPT_NETS_URL = "https://raw.githubusercontent.com/ipverse/rir-ip/master/country/eg/ipv4-aggregated.txt"
_P = "https://raw.githubusercontent.com/"
EGYPT_PROXY_SOURCES = [  # (protocol, url) — public proxy lists; only Egyptian IPs are kept
    ("http", _P + "proxifly/free-proxy-list/main/proxies/countries/EG/data.txt"),
    ("http", _P + "proxifly/free-proxy-list/main/proxies/protocols/http/data.txt"),
    ("http", _P + "TheSpeedX/PROXY-List/master/http.txt"),
    ("socks4", _P + "TheSpeedX/PROXY-List/master/socks4.txt"),
    ("socks5", _P + "TheSpeedX/PROXY-List/master/socks5.txt"),
    ("http", _P + "ErcinDedeoglu/proxies/main/proxies/http.txt"),
    ("socks4", _P + "ErcinDedeoglu/proxies/main/proxies/socks4.txt"),
    ("socks5", _P + "ErcinDedeoglu/proxies/main/proxies/socks5.txt"),
    ("http", _P + "zloi-user/hideip.me/main/http.txt"),
    ("http", _P + "mmpx12/proxy-list/master/http.txt"),
    ("http", _P + "sunny9577/proxy-scraper/master/generated/http_proxies.txt"),
    ("http", _P + "monosans/proxy-list/main/proxies/http.txt"),
    ("socks5", _P + "monosans/proxy-list/main/proxies/socks5.txt"),
    ("http", _P + "vakhov/fresh-proxy-list/master/http.txt"),
    ("socks5", _P + "vakhov/fresh-proxy-list/master/socks5.txt"),
]
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
        elif kind == "socks4":  # SOCKS4a: let the proxy resolve the name
            s.sendall(b"\x04\x01" + (443).to_bytes(2, "big") + b"\x00\x00\x00\x01\x00www.cloudflare.com\x00")
            if s.recv(8)[1:2] != b"\x5a":
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


def socks5_udp_ok(proxy):
    """True if the SOCKS5 proxy relays UDP (checked with a real DNS query to 1.1.1.1)."""
    host, port = proxy
    try:
        c = socket.create_connection((host, port), timeout=8)
        c.settimeout(8)
        c.sendall(b"\x05\x01\x00")
        if c.recv(2) != b"\x05\x00":
            return False
        c.sendall(b"\x05\x03\x00\x01\x00\x00\x00\x00\x00\x00")  # UDP ASSOCIATE
        r = c.recv(64)
        if len(r) < 10 or r[1] != 0 or r[3] != 1:
            return False
        relay_ip = socket.inet_ntoa(r[4:8])
        if relay_ip in ("0.0.0.0", "127.0.0.1") or relay_ip.startswith(("10.", "192.168.", "172.")):
            relay_ip = host
        relay = (relay_ip, int.from_bytes(r[8:10], "big"))
        query = (b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
                 b"\x0acloudflare\x03com\x00\x00\x01\x00\x01")
        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        u.settimeout(6)
        for _ in range(2):
            u.sendto(b"\x00\x00\x00\x01" + socket.inet_aton("1.1.1.1") + (53).to_bytes(2, "big") + query, relay)
            try:
                data, _ = u.recvfrom(2048)
            except socket.timeout:
                continue
            if len(data) > 12 and data[10:12] == b"\x12\x34":
                return True
        return False
    except Exception:
        return False
    finally:
        try:
            c.close()
            u.close()
        except Exception:
            pass


def warp_egypt_links(pairs):
    """WARP tunnelled through Egyptian SOCKS5 proxies that relay UDP.

    WARP then connects to Cloudflare from an Egyptian IP, so the exit is a
    Cloudflare WARP IP located in Egypt.
    """
    pairs = list(pairs)
    with ThreadPoolExecutor(128) as pool:
        eg = [p for p, loc in zip(pairs, pool.map(lambda x: exit_country((*x, "socks5")), pairs)) if loc == "EG"]
        ok = [p for p, udp in zip(eg, pool.map(socks5_udp_ok, eg)) if udp]
    print(f"warp-egypt: socks5 with EG exit {len(eg)}, with UDP {len(ok)}")
    tag = "drvpn.net"
    hidden = urllib.parse.quote(tag + " §hide§")
    # "A -> B": WARP (A) connects through the Egyptian SOCKS5 proxy (B); only WARP is listed
    return [f"warp://p2@{WARP_DEFAULT[0]}?{WARP_NOISE}#{tag} -> socks://{h}:{p}#{hidden}" for h, p in ok]


def fetch_text(url):
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"skip {url}: {e}")
        return ""


def egypt_links():
    nets = [ipaddress.ip_network(l.strip()) for l in fetch_text(EGYPT_NETS_URL).splitlines()
            if l.strip() and not l.startswith("#")]
    if not nets:
        return [], [], []
    proxies = {}
    for kind, url in EGYPT_PROXY_SOURCES:
        for ip, port in re.findall(r"(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})", fetch_text(url)):
            try:
                if any(ipaddress.ip_address(ip) in n for n in nets):
                    proxies[(ip, int(port), kind)] = None
            except ValueError:
                pass
    proxies = list(proxies)
    print(f"egypt candidates: {len(proxies)}")
    with ThreadPoolExecutor(128) as pool:
        ok = [p for p, loc in zip(proxies, pool.map(exit_country, proxies)) if loc == "EG"]
    # one entry per ip:port, preferring http > socks5 > socks4
    best = {}
    for h, p, k in sorted(ok, key=lambda x: ("http", "socks5", "socks4").index(x[2])):
        best.setdefault((h, p), k)
    tag = "drvpn.net"
    # "§hide§" keeps the WARP hop out of Hiddify's server list, so auto/lowest-ping
    # can only pick the Egyptian proxies; one shared WARP identity (p2) for all lines.
    warp = f"warp://p2@auto/?{WARP_NOISE}#{urllib.parse.quote(tag + ' §hide§')}"
    scheme = {"http": "phttp://{}:{}", "socks5": "socks://{}:{}", "socks4": "socks://{}:{}?v=4a"}
    direct = [scheme[k].format(h, p) + f"#{tag}" for (h, p), k in best.items()]
    # "A -> B": the Egyptian proxy (A) is the exit, reached through WARP (B)
    warp_egypt = warp_egypt_links(dict.fromkeys((h, p) for h, p, _ in proxies))
    return [f"{d} -> {warp}" for d in direct], direct, warp_egypt


def country_configs(links, cc):
    """V2Ray configs whose server (IP or resolved domain) is in country `cc` and is reachable."""
    nets = [ipaddress.ip_network(l.strip()) for l in fetch_text(COUNTRY_NETS_URL.format(cc.lower())).splitlines()
            if l.strip() and not l.startswith("#")]
    if not nets:
        return []
    hosts = {}
    for link in links:
        ep = endpoint(link)
        if ep and ep[0]:
            hosts.setdefault(ep[0], []).append(link)

    def in_country(host):
        try:
            ips = [ipaddress.ip_address(host)]
        except ValueError:
            try:
                ips = {ipaddress.ip_address(a[4][0]) for a in socket.getaddrinfo(host, None, socket.AF_INET)}
            except (OSError, UnicodeError):
                return False
        return any(ip in n for ip in ips for n in nets)

    with ThreadPoolExecutor(128) as pool:
        found = [l for h, hit in zip(hosts, pool.map(in_country, hosts)) if hit for l in hosts[h]]
        return [rename(l) for l, a in zip(found, pool.map(alive, found)) if a]


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

    all_links = [l for links in by_proto.values() for l in links]
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

    egypt, egypt_direct, warp_egypt = egypt_links()
    counts["warp_egypt"] = len(warp_egypt)
    with open("subs/warp_egypt.txt", "w") as f:
        f.write("\n".join(warp_egypt) + "\n")
    counts["egypt"] = len(egypt)
    counts["egypt_direct"] = len(egypt_direct)
    with open("subs/egypt.txt", "w") as f:
        f.write("\n".join(egypt) + "\n")
    # plain proxies without WARP, for unfiltered networks (e.g. Starlink) and any app
    with open("subs/egypt_direct.txt", "w") as f:
        f.write("\n".join(egypt_direct) + "\n")
    print(f"egypt: {len(egypt)}")

    iraq = country_configs(all_links, "IQ")
    counts["iraq"] = len(iraq)
    with open("subs/iraq.txt", "w") as f:
        f.write("\n".join(iraq) + "\n")
    print(f"iraq: {len(iraq)}")

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
