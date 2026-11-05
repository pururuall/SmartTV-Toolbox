import os
import sys
import webview
from tv_manager import SmartTVManager


class WebViewBridge:
    def __init__(self):
        self.manager = SmartTVManager()

    def connect(self, ip: str, port: int = 5555):
        return self.manager.connect_tv(ip, int(port))

    def pair_wireless(self, ip: str, pair_port: int, code: str):
        return self.manager.wireless_pair(ip, int(pair_port), code)

    def get_catalog_data(self):
        return {
            "packages": self.manager.packages_db,
            "launchers": self.manager.launchers_db,
            "connected_device": self.manager.current_device,
        }

    def get_device_diag(self):
        return self.manager.inspect_device()

    def run_custom_debloat(self, selected_packages: list):
        return self.manager.apply_custom_debloat(selected_packages)

    def restore_tv(self):
        return self.manager.restore_from_backup()

    def apply_launcher(self, launcher_id: str, disable_stock: bool = True):
        return self.manager.install_and_activate_launcher(launcher_id, disable_stock)

    def choose_and_push_wallpaper(self, launcher_id: str):
        window = webview.windows[0]
        file_types = ("Image Files (*.jpg;*.jpeg;*.png)", "All files (*.*)")
        result = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and len(result) > 0:
            return self.manager.push_launcher_wallpaper(launcher_id, result[0])
        return {"ok": False, "error": "Выбор файла отменен"}

    def push_preset_wallpaper(self, launcher_id: str, filename: str):
        local_path = os.path.join(self.manager.base_dir, "wallpapers", filename)
        if os.path.exists(local_path):
            return self.manager.push_launcher_wallpaper(launcher_id, local_path)
        return {"ok": False, "error": f"Обои не найдены: {filename}"}

    def update_launcher_settings(self, launcher_id: str, payload: dict):
        return self.manager.save_launcher_config(launcher_id, payload)

    def configure_youtube(self, options: dict):
        return self.manager.setup_smarttube_and_bypass(
            install_smarttube=options.get("install_smarttube", True),
            bypass_mode=options.get("bypass_mode", "byedpi"),
            byedpi_args=options.get("byedpi_args", "--split 1+s --disorder 3 --ttl 5"),
            custom_proxy_host=options.get("proxy_host", "127.0.0.1"),
            custom_proxy_port=int(options.get("proxy_port", 1080)),
            force_avc_codec=options.get("force_avc", True),
        )

    def install_apps(self, app_keys: list):
        return self.manager.install_batch_apps(app_keys)

    def execute_raw_adb(self, command: str):
        return self.manager.run_raw_adb(command)

    def setup_web_remote(self, enable: bool = True):
        return self.manager.setup_tv_web_remote(enable)

    def scan_network(self):
        return self.manager.scan_network()

    def list_third_party(self):
        return self.manager.list_installed_third_party()


if __name__ == "__main__":
    bridge = WebViewBridge()
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        meipass_dir = getattr(sys, '_MEIPASS', exe_dir)
        if os.path.exists(os.path.join(exe_dir, "app_ui.html")):
            ui_path = os.path.join(exe_dir, "app_ui.html")
        else:
            ui_path = os.path.join(meipass_dir, "app_ui.html")
    else:
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_ui.html")

    window = webview.create_window(
        title="Smart TV Toolbox v3.0 — Custom TV Optimizer",
        url=ui_path,
        js_api=bridge,
        width=1240,
        height=840,
        min_size=(980, 680),
    )
    webview.start(debug=False)
