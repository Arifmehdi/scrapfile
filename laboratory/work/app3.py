import base64
import time
import socket
import threading
import requests
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options as ChromeOptions
import random
import os
import json
from urllib.parse import urlparse
import sys

# Authenticated proxy details
username = "tqnpkuc4bi"
password = "prozzjlnfy"
ip = "45.201.18.83"
port = 7777

auth_str = f"{username}:{password}"
auth_b64 = base64.b64encode(auth_str.encode()).decode()
auth_header_value = f"Basic {auth_b64}"

LOCAL_PROXY_HOST = '127.0.0.1'
LOCAL_PROXY_PORT = 8080

# FlareSolverr endpoint
FLARESOLVERR_URL = "http://localhost:8191/v1"

# Path to FlareSolverr’s Chrome binary
CHROME_BINARY_PATH = r"C:\Users\0p\Downloads\flaresolverr_windows_x64\flaresolverr\chrome\chrome.exe"


class LocalProxyServer(threading.Thread):
    def __init__(self, host='127.0.0.1', port=8080):
        super().__init__()
        self.host = host
        self.port = port
        self.daemon = True
        self.stop_flag = threading.Event()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"Local proxy listening on http://{self.host}:{self.port}")
            while not self.stop_flag.is_set():
                client_conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(client_conn,), daemon=True).start()

    def stop(self):
        self.stop_flag.set()
        # Unblock the accept call by connecting
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_sock:
                temp_sock.connect((self.host, self.port))
        except:
            pass

    def handle_connect_method(self, client_conn, host_port):
        host, port_str = host_port.split(':')
        port_num = int(port_str)
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_sock.settimeout(10)
        try:
            upstream_sock.connect((ip, port))
            connect_request = (
                f"CONNECT {host}:{port_num} HTTP/1.1\r\n"
                f"Host: {host}:{port_num}\r\n"
                f"Proxy-Authorization: {auth_header_value}\r\n"
                f"Proxy-Connection: keep-alive\r\n\r\n"
            )
            upstream_sock.sendall(connect_request.encode('utf-8'))
            response = self.recv_until_double_crlf(upstream_sock)
            if b"200 Connection" not in response:
                client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                upstream_sock.close()
                return

            client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            self.tunnel_data(client_conn, upstream_sock)
        except Exception as e:
            print("Tunnel error:", e)
            client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            client_conn.close()

    def recv_until_double_crlf(self, sock):
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return data

    def tunnel_data(self, conn1, conn2):
        def forward(src, dst):
            try:
                while True:
                    chunk = src.recv(4096)
                    if not chunk:
                        break
                    dst.sendall(chunk)
            except:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_RDWR)
                    dst.close()
                except:
                    pass

        t1 = threading.Thread(target=forward, args=(conn1, conn2))
        t2 = threading.Thread(target=forward, args=(conn2, conn1))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def handle_client(self, client_conn):
        with client_conn:
            request_data = b""
            while True:
                chunk = client_conn.recv(4096)
                if not chunk:
                    return
                request_data += chunk
                if b"\r\n\r\n" in request_data:
                    break

            if not request_data:
                return

            headers_part, _, body = request_data.partition(b"\r\n\r\n")
            headers_lines = headers_part.decode(errors="ignore").split("\r\n")
            if len(headers_lines) < 1:
                return

            method_line = headers_lines[0]
            parts = method_line.split()
            if len(parts) < 3:
                return

            method = parts[0]
            path = parts[1]

            if method.upper() == "CONNECT":
                self.handle_connect_method(client_conn, path)
                return

            out_headers = {}
            for line in headers_lines[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    out_headers[k.lower()] = v

            if path.startswith("http://") or path.startswith("https://"):
                url = path
            else:
                host_header = out_headers.get('host')
                if not host_header:
                    client_conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                    return
                url = f"http://{host_header}{path}"

            session = requests.Session()
            session.trust_env = False
            session.verify = False
            session.proxies = {
                "http": f"http://{ip}:{port}",
                "https": f"http://{ip}:{port}"
            }

            req_headers = {k: v for k, v in out_headers.items() if k.lower() not in ['proxy-connection', 'connection', 'keep-alive']}
            req_headers['Proxy-Authorization'] = auth_header_value

            try:
                resp = session.request(method, url, headers=req_headers, data=body, timeout=10)
            except Exception:
                client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Type: text/plain\r\n\r\nBad Gateway")
                return

            status_line = f"HTTP/1.1 {resp.status_code} {resp.reason}\r\n"
            response_headers = ""
            for k, v in resp.headers.items():
                if k.lower() not in ['transfer-encoding', 'connection', 'proxy-authenticate', 'proxy-authorization']:
                    response_headers += f"{k}: {v}\r\n"

            content = resp.content
            response_data = (status_line + response_headers + "\r\n").encode() + content
            client_conn.sendall(response_data)


def get_flaresolverr_cookies(target_url):
    """Use FlareSolverr to bypass Cloudflare and get cookies."""
    payload = {
        "cmd": "request.get",
        "url": target_url,
        "maxTimeout": 60000
    }
    try:
        resp = requests.post(FLARESOLVERR_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()
        return result.get('cookies', [])
    except Exception as e:
        print(f"FlareSolverr error: {e}")
        return []


def main():
    local_proxy = LocalProxyServer(host=LOCAL_PROXY_HOST, port=LOCAL_PROXY_PORT)
    local_proxy.start()
    time.sleep(1)
    options = ChromeOptions()
    options.add_argument(f'--proxy-server=http://{LOCAL_PROXY_HOST}:{LOCAL_PROXY_PORT}')

    # Launch Chrome before fetching cookies
    driver = uc.Chrome(
        options=options,
        # browser_executable_path=CHROME_BINARY_PATH,
        # version_main=123
        browser_executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
        version_main=131 # Replace 123 with your Chrome version's major version (e.g., 117)
    )

    target_url = "https://estcolathai.com/daretobeawesome"
    base_domain = "https://estcolathai.com/daretobeawesome"

    try:
        # Navigate to the base domain first to set cookie context
        driver.get(base_domain)
        # Wait for a moment
        time.sleep(2)

        # Get cookies from FlareSolverr after Chrome is running
        solver_cookies = get_flaresolverr_cookies(target_url)

        domain = urlparse(target_url).netloc
        for ck in solver_cookies:
            cookie_dict = {
                "name": ck.get("name"),
                "value": ck.get("value"),
                "domain": ck.get("domain", domain),
                "path": ck.get("path", "/"),
                "secure": ck.get("secure", False),
                "httpOnly": ck.get("httpOnly", False),
                "expiry": ck.get("expires") if ck.get("expires") else None
            }
            cookie_dict = {k: v for k, v in cookie_dict.items() if v is not None}
            driver.add_cookie(cookie_dict)

        # Now navigate to the target page with cookies
        driver.get(target_url)

        # Example of waiting or scrolling after load
        time.sleep(5 + random.random() * 5)
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(5 + random.random() * 5)
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(5 + random.random() * 5)

        # Insert your loop or waiting condition here if needed
        # For example, waiting for a certain element:
        # from selenium.webdriver.common.by import By
        # from selenium.webdriver.support.ui import WebDriverWait
        # from selenium.webdriver.support import expected_conditions as EC
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".some-element")))

    finally:
        input('Enter input')
        driver.quit()
        local_proxy.stop()


if __name__ == "__main__":
    main()
