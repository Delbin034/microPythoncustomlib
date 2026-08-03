import network
import time
import socket

# ============================================================
#  ESP32 WIFI LIBRARY
#  Supports: STA Mode, AP Mode, HTTP GET/POST, UDP, Scan,
#            Auto-reconnect, mDNS hostname, RSSI
# ============================================================

_sta  = network.WLAN(network.STA_IF)
_ap   = network.WLAN(network.AP_IF)

_config = {
    "ssid"     : "",
    "password" : "",
    "hostname" : "esp32",
    "timeout"  : 15,       # seconds
    "retry"    : 3,
}

# ---------- GLOBAL CONFIG ----------

def setWiFi(ssid, password, hostname="esp32", timeout=15):
    """Set WiFi credentials and optional hostname / connect timeout."""
    _config["ssid"]     = ssid
    _config["password"] = password
    _config["hostname"] = hostname
    _config["timeout"]  = timeout

# ---------- CONNECT ----------

def _radio_reset():
    """
    Hard-reset the WiFi radio to clear 'Wifi Internal State Error'.
    This deactivates and reactivates the STA interface with a delay,
    which clears any stuck internal state from a previous connect attempt
    or soft reboot without a full power cycle.
    """
    try:
        _sta.disconnect()
    except:
        pass
    _sta.active(False)
    time.sleep_ms(300)
    _sta.active(True)
    time.sleep_ms(200)

def connect(ssid=None, password=None):
    """
    Connect to WiFi. Retries up to _config['retry'] times.
    Returns True on success, False on failure.

    Automatically performs a radio reset before each attempt to avoid
    'OSError: Wifi Internal State Error' after soft reboots.
    """
    ssid     = ssid     or _config["ssid"]
    password = password or _config["password"]

    if not ssid:
        print("WiFi: No SSID set. Call setWiFi() first.")
        return False

    # If already connected, just report and return
    _sta.active(True)
    if _sta.isconnected():
        print("WiFi: Already connected. IP:", _sta.ifconfig()[0])
        return True

    for attempt in range(1, _config["retry"] + 1):
        print(f"WiFi: Connecting to '{ssid}' (attempt {attempt}/{_config['retry']})...")

        # Reset radio state before every attempt — fixes Internal State Error
        # that occurs after soft reboot (Ctrl+D / machine.reset()) because
        # MicroPython does not power-cycle the WiFi peripheral on soft reset.
        _radio_reset()

        # Set hostname (requires MicroPython 1.19+)
        try:
            _sta.config(dhcp_hostname=_config["hostname"])
        except:
            pass

        try:
            _sta.connect(ssid, password)
        except OSError as e:
            print(f"WiFi: connect() raised {e} — retrying after radio reset")
            _radio_reset()
            try:
                _sta.connect(ssid, password)
            except OSError as e2:
                print(f"WiFi: still failing ({e2}), skipping attempt")
                continue

        deadline = time.ticks_add(time.ticks_ms(), _config["timeout"] * 1000)
        while not _sta.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                print("WiFi: Connection timeout.")
                break
            time.sleep_ms(500)
            print(".", end="")
        print()

        if _sta.isconnected():
            print("WiFi Connected!")
            cfg = _sta.ifconfig()
            print(f"  IP      : {cfg[0]}")
            print(f"  Subnet  : {cfg[1]}")
            print(f"  Gateway : {cfg[2]}")
            print(f"  DNS     : {cfg[3]}")
            return True
        else:
            _sta.disconnect()
            time.sleep(1)

    print("WiFi: Failed to connect after all retries.")
    return False

# ---------- DISCONNECT ----------

def disconnect():
    """Disconnect from the current WiFi network."""
    _sta.disconnect()
    print("WiFi: Disconnected.")

# ---------- IS CONNECTED ----------

def isConnected():
    """Return True if currently connected to WiFi."""
    return _sta.isconnected()

# ---------- IP ----------

def ip():
    """Return the current IP address string, or None if not connected."""
    if _sta.isconnected():
        return _sta.ifconfig()[0]
    return None

# ---------- RSSI ----------

def rssi():
    """Return the signal strength (RSSI in dBm) of the current connection."""
    try:
        return _sta.status("rssi")
    except:
        return None

# ---------- SCAN ----------

def scan():
    """
    Scan for nearby WiFi networks.
    Returns a list of tuples: (ssid, bssid, channel, rssi, authmode, hidden)
    """
    _sta.active(True)
    networks = _sta.scan()
    print(f"Found {len(networks)} network(s):")
    for n in networks:
        ssid    = n[0].decode("utf-8") if isinstance(n[0], bytes) else n[0]
        channel = n[2]
        rssi_   = n[3]
        auth    = n[4]
        auth_names = {0:"Open", 1:"WEP", 2:"WPA-PSK", 3:"WPA2-PSK", 4:"WPA/WPA2-PSK"}
        print(f"  {ssid:<30} Ch:{channel}  RSSI:{rssi_} dBm  Auth:{auth_names.get(auth,'?')}")
    return networks

# ---------- ACCESS POINT ----------

def startAP(ssid, password="", channel=6, authmode=3):
    """
    Start ESP32 as a WiFi Access Point.
    authmode: 0=Open, 3=WPA2-PSK
    """
    _ap.active(True)
    _ap.config(essid=ssid, password=password, channel=channel, authmode=authmode)
    time.sleep_ms(500)
    print(f"AP started: SSID='{ssid}', IP={_ap.ifconfig()[0]}")
    return _ap.ifconfig()[0]

# ---------- STOP AP ----------

def stopAP():
    """Stop the Access Point."""
    _ap.active(False)
    print("AP stopped.")

# ---------- AP IP ----------

def apIP():
    """Return the AP IP address."""
    return _ap.ifconfig()[0] if _ap.active() else None

# ---------- HTTP GET ----------

def httpGet(url, headers=None, timeout=10):
    """
    Perform a simple HTTP GET request.
    Returns (status_code, body_string) or (None, error_message).
    """
    try:
        proto, _, host, path = url.split("/", 3)
    except ValueError:
        proto, _, host = url.split("/", 2)
        path = ""

    port = 443 if proto == "https:" else 80

    if ":" in host:
        host, port = host.split(":")
        port = int(port)

    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s    = socket.socket()
        s.settimeout(timeout)
        s.connect(addr)

        request  = f"GET /{path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n"
        if headers:
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
        request += "\r\n"

        s.send(request.encode())

        response = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            response += chunk
        s.close()

        header, _, body = response.partition(b"\r\n\r\n")
        status_line = header.split(b"\r\n")[0]
        status_code = int(status_line.split(b" ")[1])
        return status_code, body.decode("utf-8", "replace")

    except Exception as e:
        return None, str(e)

# ---------- HTTP POST ----------

def httpPost(url, body="", content_type="application/json", headers=None, timeout=10):
    """
    Perform a simple HTTP POST request.
    Returns (status_code, body_string) or (None, error_message).
    """
    try:
        proto, _, host, path = url.split("/", 3)
    except ValueError:
        proto, _, host = url.split("/", 2)
        path = ""

    port = 443 if proto == "https:" else 80
    if ":" in host:
        host, port = host.split(":")
        port = int(port)

    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s    = socket.socket()
        s.settimeout(timeout)
        s.connect(addr)

        body_bytes = body.encode() if isinstance(body, str) else body
        request    = (
            f"POST /{path} HTTP/1.0\r\n"
            f"Host: {host}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Connection: close\r\n"
        )
        if headers:
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
        request += "\r\n"

        s.send(request.encode() + body_bytes)

        response = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            response += chunk
        s.close()

        header, _, body_resp = response.partition(b"\r\n\r\n")
        status_line = header.split(b"\r\n")[0]
        status_code = int(status_line.split(b" ")[1])
        return status_code, body_resp.decode("utf-8", "replace")

    except Exception as e:
        return None, str(e)

# ---------- UDP SEND ----------

def udpSend(host, port, message):
    """Send a UDP datagram."""
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s    = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message.encode() if isinstance(message, str) else message, addr)
        s.close()
        return True
    except Exception as e:
        print(f"UDP send error: {e}")
        return False

# ---------- UDP RECEIVE (blocking with timeout) ----------

def udpReceive(port, timeout=5, buffer=1024):
    """
    Listen for a single UDP datagram on the given port.
    Returns (data_string, sender_addr) or (None, None) on timeout.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", port))
        s.settimeout(timeout)
        data, addr = s.recvfrom(buffer)
        s.close()
        return data.decode("utf-8", "replace"), addr
    except:
        return None, None

# ---------- AUTO-RECONNECT TICK ----------

def keepAlive():
    """
    Call this in your main loop to auto-reconnect if WiFi drops.
    Example: add  wifi.keepAlive()  at the top of your while True loop.
    """
    if not _sta.isconnected():
        print("WiFi: Connection lost. Reconnecting...")
        connect()
