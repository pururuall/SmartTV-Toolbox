# -*- coding: utf-8 -*-

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



    def run_custom_debloat(self, selected_packages: list = None, packages: list = None):
        pkgs = selected_packages if selected_packages is not None else (packages or [])
        return self.manager.apply_custom_debloat(pkgs)



    def scan_running_processes(self):

        return self.manager.scan_running_processes()



    def stop_running_processes(self, packages: list):

        return self.manager.stop_running_processes(packages)



    def freeze_processes(self, packages: list):

        return self.manager.freeze_processes(packages)



    def unfreeze_processes(self, packages: list):

        return self.manager.unfreeze_processes(packages)



    def clean_tv_ram(self):

        return self.manager.clean_tv_ram()



    def clean_ram(self):

        return self.manager.clean_tv_ram()



    def purge_yandex_services(self):

        return self.manager.purge_yandex_services()



    def purge_yandex(self):

        return self.manager.purge_yandex_services()



    def get_cleanyourtv_config(self):

        return self.manager.get_cleanyourtv_config()



    def save_cleanyourtv_config(self, payload: dict, restart: bool = True):

        return self.manager.save_cleanyourtv_config(payload, restart)



    def reset_cleanyourtv_to_factory(self):

        return self.manager.reset_cleanyourtv_to_factory()



    def reset_cleanyourtv_config(self):

        return self.manager.reset_cleanyourtv_to_factory()



    def get_installed_tv_apps(self):

        return self.manager.get_installed_tv_apps()



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

        candidates = [

            self.manager.exe_dir / "wallpapers" / filename,

            self.manager.meipass_dir / "wallpapers" / filename,

            self.manager.base_dir / "wallpapers" / filename,

        ]

        for c in candidates:

            if c.exists():

                return self.manager.push_launcher_wallpaper(launcher_id, str(c))

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



    def choose_custom_apk(self):

        window = webview.windows[0]

        file_types = ("Android Package (*.apk)", "All files (*.*)")

        result = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)

        if result and len(result) > 0:

            return {"ok": True, "path": result[0]}

        return {"ok": False, "error": "Выбор файла отменен"}



    def install_custom_apk(self, file_path: str):

        return self.manager.install_apk_file(file_path)



    def execute_raw_adb(self, command: str):

        return self.manager.run_raw_adb(command)



    def setup_web_remote(self, enable: bool = True):

        return self.manager.setup_tv_web_remote(enable)



    

    def capture_tv_screenshot(self):

        return self.manager.capture_tv_screenshot()



    def scan_network(self):

        devices = self.manager.scan_network()

        return {

            "ok": True,

            "devices": devices,

            "found": [d["ip"] if isinstance(d, dict) else d for d in devices]

        }



    def get_known_devices(self):

        return {"ok": True, "devices": self.manager.get_known_devices()}



    def set_device_nickname(self, ip: str, nickname: str):

        ok = self.manager.set_device_nickname(ip, nickname)

        return {"ok": ok, "devices": self.manager.get_known_devices()}



    def list_third_party(self):

        return self.manager.list_installed_third_party()



    def push_wireguard_conf(self, conf_content="", filename="wg0.conf"):

        return self.manager.push_wireguard_conf(conf_content, filename)



    def import_happ_subscription(self, url=""):

        return self.manager.import_happ_subscription(url)



    def window_minimize(self):

        if webview.windows:

            webview.windows[0].minimize()

        return {"ok": True}



    def window_toggle_maximize(self):

        if webview.windows:

            w = webview.windows[0]

            try:

                from webview.platforms import winforms

                form = winforms.BrowserView.instances.get(w.uid)

                if form and str(form.WindowState) == "Maximized":

                    w.restore()

                    return {"ok": True, "maximized": False}

                else:

                    w.maximize()

                    return {"ok": True, "maximized": True}

            except Exception:

                w.toggle_fullscreen()

                return {"ok": True}

        return {"ok": False}



    def window_close(self):

        if webview.windows:

            webview.windows[0].destroy()

        return {"ok": True}





def _apply_dwm_caption_theming(window):

    """

    Natively colors the Windows titlebar to #141415 (matching the unslop graphite background),

    sets text to #ededed, enables dark mode caption controls, and sets the window border.

    This maintains 100% native window resizing, snapping, and controls without any frame glitches.

    """

    try:

        import ctypes

        from webview.platforms import winforms

        form = winforms.BrowserView.instances.get(window.uid)

        if not form:

            return

        hwnd = form.Handle.ToInt32()

        dwmapi = ctypes.windll.dwmapi



        # 1. Enable immersive dark mode

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        dark = ctypes.c_int(1)

        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark), ctypes.sizeof(dark))



        # 2. Native Titlebar background: #141415 (COLORREF 0x00BBGGRR = 0x00151414)

        DWMWA_CAPTION_COLOR = 35

        caption_color = ctypes.c_int(0x00141111)

        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(caption_color), ctypes.sizeof(caption_color))



        # 3. Native Titlebar text: #ededed (0x00ededed)

        DWMWA_TEXT_COLOR = 36

        text_color = ctypes.c_int(0x00ededed)

        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_TEXT_COLOR, ctypes.byref(text_color), ctypes.sizeof(text_color))



        # 4. Native Border color: #141415 (0x00151414)

        DWMWA_BORDER_COLOR = 34

        border_color = ctypes.c_int(0x00141111)

        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR, ctypes.byref(border_color), ctypes.sizeof(border_color))

    except Exception:

        pass





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

        title="Smart TV Toolbox v4.4.2 — Custom TV Optimizer, Live Process Manager & CleanYourTV Studio",

        url=ui_path,

        js_api=bridge,

        width=1240,

        height=840,

        min_size=(980, 680),

        resizable=True,

        background_color="#111114",

    )

    window.events.before_show += lambda: _apply_dwm_caption_theming(window)

    window.events.shown += lambda: _apply_dwm_caption_theming(window)

    webview.start(_apply_dwm_caption_theming, window, debug=False)

