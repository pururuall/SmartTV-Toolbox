import http.server
import json
import os
import socketserver
import urllib.parse
from tv_manager import SmartTVManager

PORT = 8000
HOST = "127.0.0.1"  # Строго локальный бинд для безопасности

manager = SmartTVManager()


class ToolboxHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(manager.base_dir), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.path = "/app_ui.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(post_data)
        except Exception:
            payload = {}

        endpoint = parsed.path.rstrip("/")
        response = {"ok": False, "error": "Unknown endpoint"}

        if endpoint == "/api/connect":
            ip = payload.get("ip", "")
            port = int(payload.get("port", 5555))
            response = manager.connect_tv(ip, port)
        elif endpoint == "/api/pair":
            ip = payload.get("ip", "")
            port = int(payload.get("port", 0))
            code = payload.get("code", "")
            response = manager.wireless_pair(ip, port, code)
        elif endpoint == "/api/catalog":
            response = {
                "ok": True,
                "packages": manager.packages_db,
                "launchers": manager.launchers_db,
                "connected_device": manager.current_device,
            }
        elif endpoint == "/api/diag":
            response = manager.inspect_device()
        elif endpoint == "/api/debloat":
            packages = payload.get("packages", [])
            response = manager.apply_custom_debloat(packages)
        elif endpoint == "/api/restore":
            response = manager.restore_from_backup()
        elif endpoint == "/api/launcher/apply":
            launcher_id = payload.get("launcher_id", "")
            disable_stock = payload.get("disable_stock", True)
            response = manager.install_and_activate_launcher(launcher_id, disable_stock)
        elif endpoint == "/api/launcher/config":
            launcher_id = payload.get("launcher_id", "")
            cfg = payload.get("payload", {})
            response = manager.save_launcher_config(launcher_id, cfg)
        elif endpoint == "/api/launcher/wallpaper":
            launcher_id = payload.get("launcher_id", "")
            filename = payload.get("filename", "")
            local_path = os.path.join(manager.base_dir, "wallpapers", filename)
            if os.path.exists(local_path):
                response = manager.push_launcher_wallpaper(launcher_id, local_path)
            else:
                response = {"ok": False, "error": "Wallpaper file not found"}
        elif endpoint == "/api/youtube":
            response = manager.setup_smarttube_and_bypass(
                install_smarttube=payload.get("install_smarttube", True),
                bypass_mode=payload.get("bypass_mode", "byedpi"),
                byedpi_args=payload.get("byedpi_args", "--split 1+s --disorder 3 --ttl 5"),
                custom_proxy_host=payload.get("proxy_host", "127.0.0.1"),
                custom_proxy_port=int(payload.get("proxy_port", 1080)),
                force_avc_codec=payload.get("force_avc", True),
            )
        elif endpoint == "/api/apps/install":
            apps = payload.get("apps", [])
            response = manager.install_batch_apps(apps)
        elif endpoint == "/api/adb/raw":
            cmd = payload.get("command", "")
            response = manager.run_raw_adb(cmd)
        elif endpoint == "/api/web_remote":
            enable = payload.get("enable", True)
            response = manager.setup_tv_web_remote(enable)
        elif endpoint in ("/api/screenshot", "/api/tv/screenshot", "/api/capture_tv_screenshot"):
            response = manager.capture_tv_screenshot()
        elif endpoint in ("/api/scan", "/api/scan_network"):
            devices = manager.scan_network()
            response = {
                "ok": True,
                "devices": devices,
                "found": [d["ip"] if isinstance(d, dict) else d for d in devices]
            }
        elif endpoint in ("/api/devices/known", "/api/get_known_devices"):
            response = {"ok": True, "devices": manager.get_known_devices()}
        elif endpoint in ("/api/devices/set_nickname", "/api/set_device_nickname"):
            ok = manager.set_device_nickname(payload.get("ip", ""), payload.get("nickname", ""))
            response = {"ok": ok, "devices": manager.get_known_devices()}
        elif endpoint == "/api/apk/install":
            response = manager.install_apk_file(payload.get("file_path", ""))
        elif endpoint in ("/api/processes/scan", "/api/scan_running_processes"):
            response = manager.scan_running_processes()
        elif endpoint in ("/api/processes/stop", "/api/stop_running_processes"):
            response = manager.stop_running_processes(payload.get("packages", []))
        elif endpoint in ("/api/processes/freeze", "/api/freeze_processes"):
            response = manager.freeze_processes(payload.get("packages", []))
        elif endpoint in ("/api/processes/unfreeze", "/api/unfreeze_processes"):
            response = manager.unfreeze_processes(payload.get("packages", []))
        elif endpoint in ("/api/cleanyourtv/config", "/api/get_cleanyourtv_config"):
            response = manager.get_cleanyourtv_config()
        elif endpoint in ("/api/cleanyourtv/save", "/api/save_cleanyourtv_config"):
            cfg = payload.get("config", payload.get("payload", payload))
            restart = payload.get("restart", True)
            response = manager.save_cleanyourtv_config(cfg, restart)
        elif endpoint in ("/api/cleanyourtv/reset", "/api/reset_cleanyourtv_config"):
            response = manager.reset_cleanyourtv_config()
        elif endpoint in ("/api/cleanyourtv/factory_reset", "/api/reset_cleanyourtv_to_factory"):
            response = manager.reset_cleanyourtv_to_factory()
        elif endpoint in ("/api/vpn/install", "/api/install_vpn_client"):
            response = manager.install_vpn_client(payload.get("client", "wireguard"))
        elif endpoint in ("/api/vpn/status", "/api/get_vpn_status"):
            response = manager.get_vpn_status()
        elif endpoint in ("/api/vpn/wireguard_push", "/api/push_wireguard_conf"):
            response = manager.push_wireguard_conf(payload.get("conf_content", ""), payload.get("filename", "wg0.conf"))
        elif endpoint in ("/api/vpn/happ_subscription", "/api/import_happ_subscription"):
            response = manager.import_happ_subscription(payload.get("url", ""))
        elif endpoint in ("/api/cleanyourtv/apps", "/api/get_installed_tv_apps"):
            response = manager.get_installed_tv_apps()
        elif endpoint in ("/api/system/clean_ram", "/api/clean_ram"):
            response = manager.clean_tv_ram()
        elif endpoint in ("/api/system/purge_yandex", "/api/purge_yandex"):
            response = manager.purge_yandex_services()

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), ToolboxHandler) as httpd:
        print(f"[*] Smart TV Toolbox v3.0 Server запущен: http://{HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")


if __name__ == "__main__":
    run_server()
