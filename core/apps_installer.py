# -*- coding: utf-8 -*-
"""
core.apps_installer
Логика установки APK, лаунчеров, VPN клиентов и проверки версий.
"""
import os
import sys
import re
import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.debloat import KNOWN_TV_PACKAGES


class AppsInstallerMixin:
    def is_valid_apk(self, path: Optional[Path]) -> bool:

        """Проверяет существование файла, минимальный размер (>1000 байт) и сигнатуру zip/apk."""

        try:

            if not path:

                return False

            p = Path(path)

            if not p.is_file():

                return False

            if p.stat().st_size < 1000:

                return False

            with open(p, "rb") as f:

                return f.read(4) == b"PK\x03\x04"

        except Exception:

            return False


    def resolve_apk(self, rel_path: str, status_cb=None) -> Optional[Path]:

        """

        Ищет APK в exe_dir, _MEIPASS, base_dir, плоских папках apps,

        проверяет сигнатуру файла (отсекает 131-байтные Git LFS указатели)

        и при необходимости автоматически скачивает файл из GitHub-репозитория.

        """

        if not rel_path:

            return None



        clean_rel = rel_path.replace("\\", "/").strip("/")

        filename = Path(clean_rel).name



        candidates = [

            self.exe_dir / clean_rel,

            self.meipass_dir / clean_rel,

            self.base_dir / clean_rel,

            self.exe_dir / "apps" / filename,

            self.base_dir / "apps" / filename,

            self.meipass_dir / "apps" / filename,

            Path.cwd() / clean_rel,

            Path.cwd() / "apps" / filename,

            Path.cwd() / filename,

            self.exe_dir / "apps" / filename.lower(),

            self.base_dir / "apps" / filename.lower(),

        ]



        for cand in candidates:

            if self.is_valid_apk(cand):

                return cand



        # Дополнительный рекурсивный поиск в папках apps (на случай вложенности или регистра)

        for root in [self.exe_dir, self.meipass_dir, self.base_dir, Path.cwd()]:

            if not root or not root.exists():

                continue

            apps_dir = root / "apps"

            if apps_dir.exists():

                for found_file in apps_dir.rglob("*.apk"):

                    if found_file.name.lower() == filename.lower() and self.is_valid_apk(found_file):

                        return found_file



        # Если локально нет или файл поврежден (например LFS указатель ~131 байт) — скачиваем из GitHub

        self._notify(f"[Облако] Скачивание {filename} из репозитория...", status_cb)



        target_dir = self.exe_dir / Path(clean_rel).parent

        try:

            target_dir.mkdir(parents=True, exist_ok=True)

            target_path = self.exe_dir / clean_rel

        except Exception:

            appdata = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "SmartTV_Toolbox"

            target_dir = appdata / Path(clean_rel).parent

            target_dir.mkdir(parents=True, exist_ok=True)

            target_path = appdata / clean_rel



        urls = [

            f"https://media.githubusercontent.com/media/pururuall/SmartTV-Toolbox/main/{clean_rel}",

            f"https://raw.githubusercontent.com/pururuall/SmartTV-Toolbox/main/{clean_rel}",

            f"https://github.com/pururuall/SmartTV-Toolbox/raw/main/{clean_rel}",

        ]

        if not clean_rel.startswith("apps/"):

            urls.insert(0, f"https://media.githubusercontent.com/media/pururuall/SmartTV-Toolbox/main/apps/{clean_rel}")



        import urllib.request

        import shutil



        temp_target = target_path.with_suffix(target_path.suffix + ".downloading")

        for url in urls:

            try:

                req = urllib.request.Request(

                    url,

                    headers={

                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SmartTV-Toolbox/3.0",

                        "Accept": "*/*",

                    },

                )

                with urllib.request.urlopen(req, timeout=45) as resp:

                    if resp.status == 200:

                        with open(temp_target, "wb") as f_out:

                            shutil.copyfileobj(resp, f_out)



                        if self.is_valid_apk(temp_target):

                            if target_path.exists():

                                target_path.unlink()

                            temp_target.replace(target_path)

                            size_kb = target_path.stat().st_size // 1024

                            self._notify(f"[Облако] ✓ {filename} успешно загружен ({size_kb} КБ)", status_cb)

                            return target_path

                        else:

                            if temp_target.exists():

                                temp_target.unlink()

            except Exception:

                if temp_target.exists():

                    try:

                        temp_target.unlink()

                    except Exception:

                        pass

                continue



        self._notify(f"[Ошибка] Не удалось скачать {filename} из GitHub.", status_cb)

        return None


    def install_and_activate_launcher(

        self, launcher_id: str, disable_stock: bool = True

    ) -> Dict[str, Any]:

        """Устанавливает выбранный лаунчер и безопасно делает его главным экраном."""

        launchers = self.launchers_db.get("launchers", {})

        if launcher_id not in launchers:

            return {"ok": False, "error": f"Неизвестный лаунчер: {launcher_id}"}



        meta = launchers[launcher_id]

        self._notify(f"Поиск APK для лаунчера {meta.get('name', launcher_id)}...")

        apk_full_path = self.resolve_apk(meta["apk_path"])

        if not apk_full_path:

            return {"ok": False, "error": f"Файл APK не найден и не удалось скачать: {meta['apk_path']}"}



        self._notify(f"Установка APK на ТВ: {apk_full_path.name}...")

        inst_res = self.run_adb(["install", "-r", str(apk_full_path)], timeout=90)

        if not inst_res["ok"]:

            return {"ok": False, "error": f"Ошибка установки APK: {inst_res['stderr'] or inst_res['stdout']}"}



        component = f"{meta['package']}/{meta['main_activity']}"

        self.run_adb(["shell", "cmd", "package", "set-home-activity", component])



        if disable_stock:

            stock_launchers = [

                "com.yandex.tv.launcher",

                "com.google.android.apps.tv.launcherx",

                "com.google.android.tvlauncher",

                "ru.sberdevices.starlauncher",

                "com.haier.launcher.haiermatrix",

                "com.mitv.tvhome",

            ]

            for stock_pkg in stock_launchers:

                self.run_adb(["shell", "pm", "disable-user", "--user", "0", stock_pkg])



        self.run_adb(["shell", "am", "start", "-n", component])



        web_remote_url = None

        if meta.get("supports_web_remote") and self.current_device:

            ip_only = self.current_device.split(":")[0]

            web_remote_url = f"http://{ip_only}:{meta['web_remote_port']}"



        return {

            "ok": True,

            "launcher": meta["name"],

            "web_remote_url": web_remote_url,

        }


    def push_launcher_wallpaper(self, launcher_id: str, local_image_path: str) -> Dict[str, Any]:

        """Загружает кастомный фон с компьютера напрямую в выбранный лаунчер на ТВ."""

        launchers = self.launchers_db.get("launchers", {})

        meta = launchers.get(launcher_id)

        if not meta or not meta.get("supports_custom_wallpaper"):

            return {"ok": False, "error": "Выбранный лаунчер не поддерживает прямую загрузку обоев."}



        remote_path = meta["wallpaper_remote_path"]

        remote_dir = os.path.dirname(remote_path).replace("\\", "/")

        self.run_adb(["shell", "mkdir", "-p", remote_dir])



        push_res = self.run_adb(["push", local_image_path, remote_path], timeout=30)

        if not push_res["ok"]:

            return {"ok": False, "error": push_res["stderr"]}



        self.run_adb([

            "shell", "am", "broadcast",

            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",

            "-d", f"file://{remote_path}"

        ])

        self.run_adb(["shell", "am", "force-stop", meta["package"]])

        self.run_adb(["shell", "am", "start", "-n", f"{meta['package']}/{meta['main_activity']}"])



        return {"ok": True, "remote_path": remote_path}


    def setup_tv_web_remote(self, enable: bool = True) -> Dict[str, Any]:

        """Устанавливает или отключает автономный веб-пульт прямо на ТВ и добавляет круглую кнопку в CleanYourTV."""

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен к ADB."}



        ip_only = self.current_device.split(":")[0]

        remote_pkg = "com.zhouwj.tvinstaller"



        def update_cleanyourtv_topbar(add_pkg: bool):

            try:

                cfg_remote = "/sdcard/Android/data/com.gathin.tvhome/files/config.json"

                tmp_cfg = self.backups_dir / "clean_config_tmp.json"

                res = self.run_adb(["pull", cfg_remote, str(tmp_cfg)])

                if res.get("ok", False) and tmp_cfg.exists():

                    with open(tmp_cfg, "r", encoding="utf-8") as f:

                        cfg = json.load(f)

                    top_apps = cfg.get("top_bar_apps", [])

                    changed = False

                    if add_pkg and remote_pkg not in top_apps:

                        top_apps.append(remote_pkg)

                        cfg["top_bar_apps"] = top_apps

                        changed = True

                    elif not add_pkg and remote_pkg in top_apps:

                        top_apps = [p for p in top_apps if p != remote_pkg]

                        cfg["top_bar_apps"] = top_apps

                        changed = True



                    if changed:

                        with open(tmp_cfg, "w", encoding="utf-8") as f:

                            json.dump(cfg, f, indent=4)

                        self.run_adb(["push", str(tmp_cfg), cfg_remote])

                        self.run_adb(["shell", "am", "force-stop", "com.gathin.tvhome"])

                        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])

            except Exception as e:

                print(f"[TVWebRemote] top bar update error: {e}")



        if not enable:

            self.run_adb(["shell", "pkill", "-f", "busybox.*httpd"])

            self.run_adb(["shell", "rm", "-rf", "/data/local/tmp/web_remote"])

            update_cleanyourtv_topbar(add_pkg=False)

            return {"ok": True, "enabled": False, "msg": "Веб-пульт остановлен, круглая кнопка удалена из панели ТВ."}



        local_remote_dir = self.base_dir / "web_remote"

        if not local_remote_dir.exists():

            for d in [self.exe_dir / "web_remote", self.meipass_dir / "web_remote"]:

                if d.exists():

                    local_remote_dir = d

                    break

        if not local_remote_dir.exists():

            return {"ok": False, "error": "Папка web_remote не найдена."}



        self.run_adb(["shell", "mkdir", "-p", "/data/local/tmp/web_remote/cgi-bin"])

        self.run_adb(["push", str(local_remote_dir / "index.html"), "/data/local/tmp/web_remote/index.html"])



        cgi_dir = local_remote_dir / "cgi-bin"

        if cgi_dir.exists():

            for cgi_file in cgi_dir.iterdir():

                if cgi_file.is_file():

                    self.run_adb(["push", str(cgi_file), f"/data/local/tmp/web_remote/cgi-bin/{cgi_file.name}"])



        self.run_adb(["shell", "chmod", "-R", "755", "/data/local/tmp/web_remote"])

        self.run_adb(["shell", "pkill", "-f", "busybox.*httpd"])

        self.run_adb(["shell", "busybox", "httpd", "-p", "8080", "-h", "/data/local/tmp/web_remote"])



        apk_path = self.resolve_apk("apps/TVWebRemote.apk")

        if not apk_path:

            apk_path = self.resolve_apk("apps/media/TVWebRemote.apk")



        pm_check = self.run_adb(["shell", "pm", "path", remote_pkg])

        if "package:" not in pm_check.get("stdout", "") and apk_path:

            self._notify("Установка TVWebRemote на ТВ...")

            self.run_adb(["install", "-r", str(apk_path)], timeout=60)



        update_cleanyourtv_topbar(add_pkg=True)



        url = f"http://{ip_only}:8080"

        qr_b64 = ""

        try:

            import qrcode, io, base64

            qr = qrcode.QRCode(box_size=6, border=2)

            qr.add_data(url)

            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()

            img.save(buf, format="PNG")

            qr_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        except Exception:

            pass



        return {

            "ok": True,

            "enabled": True,

            "port": 8080,

            "url": url,

            "qr_base64": qr_b64,

            "msg": f"Веб-пульт активен! Круглая кнопка вызова QR-кода добавлена на ТВ: {url}"

        }


    def setup_smarttube_and_bypass(

        self,

        install_smarttube: bool = True,

        bypass_mode: str = "byedpi",

        byedpi_args: str = "--split 1+s --disorder 3 --ttl 5",

        custom_proxy_host: str = "127.0.0.1",

        custom_proxy_port: int = 1080,

        force_avc_codec: bool = True,

    ) -> Dict[str, Any]:

        """Установка и тонкая настройка SmartTube + обхода замедлений YouTube."""

        steps_log = []

        smarttube_pkg = "com.liskovsoft.smarttubetv.beta"



        if install_smarttube:

            self._notify("[YouTube] Подготовка SmartTube...")

            st_apk = self.resolve_apk("apps/youtube/SmartTube_stable.apk")

            if st_apk and self.is_valid_apk(st_apk):

                self._notify(f"[YouTube] Установка {st_apk.name} на ТВ...")

                res = self.run_adb(["install", "-r", str(st_apk)], timeout=90)

                steps_log.append({"step": "install_smarttube", "ok": res["ok"]})

            else:

                steps_log.append({"step": "install_smarttube", "ok": False, "error": "SmartTube APK не найден"})



        if bypass_mode == "byedpi":

            self._notify("[ByeDPI] Подготовка ByeDPI...")

            byedpi_apk = self.resolve_apk("apps/youtube/ByeDPI_tv.apk")

            if byedpi_apk and self.is_valid_apk(byedpi_apk):

                self._notify(f"[ByeDPI] Установка {byedpi_apk.name} на ТВ...")

                self.run_adb(["install", "-r", str(byedpi_apk)], timeout=60)



            cfg_dir = "/sdcard/Android/data/io.github.dovecoteescapee.byedpi/files"

            self.run_adb(["shell", "mkdir", "-p", cfg_dir])

            self.run_adb(["shell", f"echo '{byedpi_args}' > {cfg_dir}/byedpi_cmd.txt"])

            custom_proxy_host = "127.0.0.1"

            custom_proxy_port = 1080

            steps_log.append({"step": "configure_byedpi", "args": byedpi_args, "ok": True})

        elif bypass_mode == "dns_only":

            self.run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"])

            self.run_adb(["shell", "settings", "put", "global", "private_dns_specifier", "dns.adguard-dns.com"])

            steps_log.append({"step": "configure_private_dns", "dns": "dns.adguard-dns.com", "ok": True})



        if bypass_mode in ("byedpi", "custom_proxy") or force_avc_codec:

            st_prefs_dir = f"/sdcard/Android/data/{smarttube_pkg}/files/smarttube_preset"

            self.run_adb(["shell", "mkdir", "-p", st_prefs_dir])



            preset_data = {

                "proxy_enabled": bypass_mode in ("byedpi", "custom_proxy"),

                "proxy_type": "SOCKS5",

                "proxy_host": custom_proxy_host,

                "proxy_port": custom_proxy_port,

                "preferred_codec": "avc" if force_avc_codec else "vp9",

                "video_buffer_size": "high",

                "sponsor_block_enabled": True,

            }

            local_preset = self.backups_dir / "smarttube_preset.json"

            with open(local_preset, "w", encoding="utf-8") as f:

                json.dump(preset_data, f, indent=2)



            self.run_adb(["push", str(local_preset), f"{st_prefs_dir}/config.json"])

            steps_log.append({"step": "inject_smarttube_prefs", "preset": preset_data, "ok": True})



        return {"ok": True, "steps": steps_log}


    def install_batch_apps(self, app_keys: List[str]) -> Dict[str, Any]:

        """Пакетная установка медиа-приложений из каталога."""

        installed, errors = [], []

        apps_map = {

            "lampa": "apps/media/Lampa.apk",

            "zona": "apps/media/Zona.apk",

            "hdrezka": "apps/media/HDRezka.apk",

            "filemanager": "apps/media/FileManagerPlus.apk",

            "happ": "apps/media/Happ.apk",

            "spotify": "apps/media/SpotifyTV.apk",

            "smarttube": "apps/youtube/SmartTube_stable.apk",

            "byedpi": "apps/youtube/ByeDPI_tv.apk",

            "wireguard": "apps/media/wireguard.apk",

            "amnezia": "apps/media/amnezia.apk",

            "msx": "apps/media/Media+Station+X+v.0.1.160.apk",

            "num": "apps/media/NUM_1.0.150-release.apk",

            "webremote": "apps/media/TVWebRemote.apk",

            "cleanyourtv": "apps/launchers/CleanYourTV.apk",

            "moytv": "apps/launchers/MoyTV.apk",

            "flauncher": "apps/launchers/FLauncher.apk",

        }



        total = len(app_keys)

        for idx, key in enumerate(app_keys, 1):

            rel_path = apps_map.get(key.lower())

            if not rel_path:

                errors.append({"app": key, "error": "Приложение не найдено в каталоге"})

                continue



            self._notify(f"[{idx}/{total}] Поиск APK: {key} ({Path(rel_path).name})...")

            apk = self.resolve_apk(rel_path)

            if apk and self.is_valid_apk(apk):

                self._notify(f"[{idx}/{total}] Установка {key} на ТВ...")

                res = self.run_adb(["install", "-r", str(apk)], timeout=120)

                out = (res.get("stdout", "") + " " + res.get("stderr", "")).strip()

                if res.get("ok") or "Success" in out:

                    installed.append(key)

                    self._notify(f"[{idx}/{total}] ✓ {key} успешно установлено!")

                else:

                    err_msg = res.get("stderr") or res.get("stdout") or "Ошибка установки"

                    errors.append({"app": key, "error": err_msg})

                    self._notify(f"[{idx}/{total}] ⚠ Ошибка установки {key}: {err_msg}")

            else:

                errors.append({"app": key, "error": "APK файл не найден и не удалось скачать"})

                self._notify(f"[{idx}/{total}] ⚠ Не удалось получить APK для {key}")



        return {"ok": True, "installed": installed, "errors": errors}


    def install_apk_file(self, apk_path: str) -> Dict[str, Any]:

        """Установка пользовательского APK файла на подключенный ТВ."""

        p = Path(apk_path)

        if not p.exists():

            return {"ok": False, "error": f"Файл не найден: {apk_path}"}

        res = self.run_adb(["install", "-r", str(p)], timeout=120)

        stdout = res.get("stdout", "")

        stderr = res.get("stderr", "")

        if "Success" in stdout or "Success" in stderr or res.get("ok", False):

            return {"ok": True, "msg": f"Приложение {p.name} успешно установлено на ТВ!"}

        return {"ok": False, "error": stderr or stdout or "Ошибка установки"}


    def list_installed_third_party(self) -> List[Dict[str, str]]:

        """Возвращает список установленных пользовательских пакетов."""

        res = self.run_adb(["shell", "pm", "list", "packages", "-3"])

        if not res["ok"]:

            return []

        packages = []

        for line in res["stdout"].splitlines():

            pkg = line.replace("package:", "").strip()

            if pkg:

                packages.append({"package": pkg, "name": pkg.split(".")[-1].capitalize()})

        return packages


    def get_vpn_status(self) -> Dict[str, Any]:

        """Проверяет статус установки поддерживаемых VPN клиентов на телевизоре."""

        status = {

            "wireguard": False,

            "amnezia": False,

            "happ": False,

            "byedpi": False

        }

        if not self.current_device:

            return {"ok": False, "status": status, "error": "ТВ не подключен"}

        res = self.run_adb(["shell", "pm", "list", "packages", "-3"], timeout=8)

        if res.get("ok"):

            stdout = res.get("stdout", "")

            status["wireguard"] = ("com.wireguard.android" in stdout)

            status["amnezia"] = ("org.amnezia.vpn" in stdout)

            status["happ"] = ("su.happ.proxyutility" in stdout)

            status["byedpi"] = ("io.github.dovecoteescapee.byedpi" in stdout or "org.lumic.byedpi" in stdout)

        return {"ok": True, "status": status}


    def install_vpn_client(self, client_name: str) -> Dict[str, Any]:

        """Устанавливает выбранный VPN клиент на ТВ из встроенной папки apps."""

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "Телевизор не подключен по ADB"}



        client = (client_name or "").lower().strip()

        apk_candidates = {

            "wireguard": ["apps/media/wireguard.apk", "apps/wireguard.apk"],

            "amnezia": ["apps/media/amnezia.apk", "apps/amnezia.apk"],

            "happ": ["apps/media/Happ.apk", "apps/Happ.apk"],

            "byedpi": ["apps/youtube/ByeDPI_tv.apk", "apps/byedpi.apk"]

        }

        candidates = apk_candidates.get(client, [])

        target_path = None

        for cand in candidates:

            p = self._resolve_file(cand)

            if p.exists() and p.stat().st_size > 100000:

                target_path = p

                break

        

        if not target_path:

            return {"ok": False, "error": f"Файл APK для {client_name} не найден в apps/"}



        self._notify(f"[{client_name.upper()}] Установка {target_path.name} на ТВ...")

        res = self.install_apk_file(str(target_path))

        if res.get("ok"):

            self._notify(f"[{client_name.upper()}] ✓ Приложение успешно установлено на телевизор!")

        return res


    def push_wireguard_conf(self, conf_content: str, filename: str = "wg0.conf") -> Dict[str, Any]:

        """Загружает файл конфигурации WireGuard (.conf) в папку Download на ТВ и открывает приложение."""

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "Телевизор не подключен по ADB"}



        if not conf_content or not conf_content.strip():

            return {"ok": False, "error": "Конфигурация WireGuard пуста"}



        if not filename.endswith(".conf"):

            filename = f"{filename}.conf"



        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")

        if not clean_filename:

            clean_filename = "wg0.conf"



        local_tmp = self.backups_dir / clean_filename

        try:

            with open(local_tmp, "w", encoding="utf-8") as f:

                f.write(conf_content.strip() + "\n")

        except Exception as e:

            return {"ok": False, "error": f"Ошибка сохранения локального файла: {e}"}



        # 1. Create Download dir on TV

        self.run_adb(["shell", "mkdir", "-p", "/sdcard/Download"])

        

        # 2. Push file

        remote_target = f"/sdcard/Download/{clean_filename}"

        push_res = self.run_adb(["push", str(local_tmp), remote_target], timeout=15)

        if not push_res.get("ok"):

            return {"ok": False, "error": f"Ошибка передачи файла на ТВ: {push_res.get('stderr')}"}



        self.run_adb(["shell", "chmod", "666", remote_target])



        # 3. Try to launch WireGuard on TV

        self._notify(f"[WireGuard] Файл {clean_filename} успешно загружен в /sdcard/Download/ на ТВ!")

        self.run_adb(["shell", "am", "start", "-n", "com.wireguard.android/.activity.MainActivity"], timeout=8)



        return {

            "ok": True,

            "msg": f"Конфиг {clean_filename} успешно сохранён в папку «Download» на ТВ! Приложение WireGuard запущено на экране.",

            "path": remote_target

        }


    def import_happ_subscription(self, url: str) -> Dict[str, Any]:

        """Отправляет ссылку подписки в приложение Happ на телевизоре через Android Intent."""

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "Телевизор не подключен по ADB"}



        url = (url or "").strip()

        if not url:

            return {"ok": False, "error": "Ссылка подписки Happ пуста"}



        self._notify(f"[Happ] Отправка ссылки подписки на ТВ: {url[:30]}...")

        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url], timeout=10)

        

        check_pkg = self.run_adb(["shell", "pm", "path", "su.happ.proxyutility"])

        if not check_pkg.get("ok") or not check_pkg.get("stdout"):

            return {

                "ok": True,

                "msg": "Ссылка отправлена! Примечание: Приложение Happ ещё не установлено на ТВ — установите его кнопкой «Установить Happ».",

                "happ_installed": False

            }



        return {"ok": True, "msg": "Ссылка подписки успешно передана в Happ на телевизоре!", "happ_installed": True}


    def get_installed_tv_apps(self) -> Dict[str, Any]:

        """Возвращает список всех установленных на ТВ приложений с понятными именами для выбора в док/скрытие."""

        apps_list = []

        installed_set = set()



        if self.current_device:

            res3 = self.run_adb(["shell", "pm", "list", "packages", "-3"], timeout=10)

            if res3["ok"]:

                for line in res3["stdout"].splitlines():

                    pkg = line.replace("package:", "").strip()

                    if pkg:

                        installed_set.add(pkg)



            res_all = self.run_adb(["shell", "pm", "list", "packages"], timeout=10)

            if res_all["ok"]:

                for line in res_all["stdout"].splitlines():

                    pkg = line.replace("package:", "").strip()

                    if pkg in KNOWN_TV_PACKAGES and KNOWN_TV_PACKAGES[pkg].get("category") in ("user_app", "media_app"):

                        installed_set.add(pkg)



        if installed_set:

            for pkg in sorted(installed_set):

                meta = KNOWN_TV_PACKAGES.get(pkg)

                name = meta["name"] if meta else pkg.split(".")[-1].replace("_", " ").title()

                apps_list.append({

                    "pkg": pkg,

                    "name": name,

                    "desc": meta["desc"] if meta else pkg

                })

        else:

            fallback_pkgs = [

                "mobi.zona", "com.lampa.tv", "ru.rezka.app", "com.google.android.youtube.tv",

                "ru.kinopoisk.tv", "com.vk.vkvideo", "ru.ivi.client", "ru.rt.video.app.tv",

                "com.spb.tv.android", "tv.smarttube.beta", "com.google.android.apps.tv.launcherx"

            ]

            for pkg in fallback_pkgs:

                meta = KNOWN_TV_PACKAGES.get(pkg)

                name = meta["name"] if meta else pkg

                apps_list.append({

                    "pkg": pkg,

                    "name": name,

                    "desc": meta["desc"] if meta else pkg

                })



        return {"ok": True, "apps": apps_list}
