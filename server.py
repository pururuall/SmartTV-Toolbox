# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import urllib.parse
import subprocess
import os
import sys

# Import functions from tv_manager
import tv_manager

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SmartTVRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/get_apps':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            apps_dir = tv_manager.APPS_DIR
            apps_list = []
            if os.path.exists(apps_dir):
                for f in sorted(os.listdir(apps_dir)):
                    if f.lower().endswith(".apk"):
                        full_p = os.path.join(apps_dir, f)
                        size_mb = round(os.path.getsize(full_p) / (1024 * 1024), 1)
                        apps_list.append({"filename": f, "size_mb": size_mb})
            
            self.wfile.write(json.dumps({"success": True, "apps": apps_list}, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/get_packages':
            query = urllib.parse.parse_qs(parsed.query)
            manual_ip = query.get('ip', [None])[0]
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if not ip:
                self.wfile.write(json.dumps({"success": False, "packages": []}, ensure_ascii=False).encode('utf-8'))
            else:
                pkgs = tv_manager.action_get_installed_packages(ip)
                self.wfile.write(json.dumps({"success": True, "packages": pkgs}, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/get_dns':
            query = urllib.parse.parse_qs(parsed.query)
            manual_ip = query.get('ip', [None])[0]
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if not ip:
                self.wfile.write(json.dumps({"success": False, "message": "Нет связи с ТВ"}, ensure_ascii=False).encode('utf-8'))
            else:
                dns = tv_manager.action_get_dns(ip)
                self.wfile.write(json.dumps({"success": True, "ip": ip, **dns}, ensure_ascii=False).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        req_data = json.loads(body) if body else {}

        if parsed.path == '/api/test_connection':
            manual_ip = req_data.get('ip')
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            data = tv_manager.action_test_connection(clean_ip)
            if not data:
                resp = {
                    "success": False,
                    "message": "Не удалось обнаружить телевизор или порт 5555 закрыт.",
                    "details": "Убедитесь, что телевизор включен, подключен к тому же Wi-Fi и включена отладка ADB."
                }
            else:
                resp = {
                    "success": True,
                    "ip": data.get("ip"),
                    "brand": data.get("brand"),
                    "model": data.get("model"),
                    "android": data.get("android"),
                    "launcher": data.get("launcher"),
                    "dns_mode": data.get("dns_mode"),
                    "dns_specifier": data.get("dns_specifier"),
                    "message": "Связь с телевизором успешно установлена!"
                }
            
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/set_dns':
            manual_ip = req_data.get('ip')
            enable = req_data.get('enable', True)
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if not ip:
                self.wfile.write(json.dumps({"success": False, "message": "Нет связи с ТВ"}, ensure_ascii=False).encode('utf-8'))
            else:
                tv_manager.action_set_dns(ip, enable)
                dns = tv_manager.action_get_dns(ip)
                msg = "AdGuard DNS активирован!" if dns["enabled"] else "Private DNS отключен."
                self.wfile.write(json.dumps({"success": True, "enabled": dns["enabled"], "message": msg}, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/set_dock':
            manual_ip = req_data.get('ip')
            dock_apps = req_data.get('dock_apps')
            columns = int(req_data.get('columns', 6))
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if not ip:
                self.wfile.write(json.dumps({"success": False, "message": "Нет связи с ТВ"}, ensure_ascii=False).encode('utf-8'))
            else:
                tv_manager.action_set_dock(ip, dock_apps, columns)
                self.wfile.write(json.dumps({"success": True, "message": "Конфигурация дока успешно обновлена на телевизоре!"}, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/switch_launcher':
            manual_ip = req_data.get('ip')
            launcher_name = req_data.get('launcher', 'cleanyourtv')
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if not ip:
                self.wfile.write(json.dumps({"success": False, "message": "Нет связи с ТВ"}, ensure_ascii=False).encode('utf-8'))
            else:
                tv_manager.action_switch_launcher(ip, launcher_name)
                self.wfile.write(json.dumps({"success": True, "message": f"Домашний экран переключен на {launcher_name.upper()}!"}, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/run_action':
            action = req_data.get('action')
            manual_ip = req_data.get('ip')
            apks = req_data.get('apks') or req_data.get('apps_list') or req_data.get('preset')
            tv_type = req_data.get('tv_type', 'yaos')
            launcher_choice = req_data.get('launcher_choice', 'cleanyourtv')
            
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            ip = tv_manager.connect_adb(clean_ip)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            if not ip:
                resp = {"success": False, "message": "Нет связи с телевизором по ADB!"}
            else:
                if action == 'install':
                    cnt = tv_manager.action_install_apps(ip, apks or "top6")
                    resp = {"success": True, "message": f"Подгрузка приложений завершена! Установлено: {cnt}."}
                elif action == 'light_debloat':
                    tv_manager.action_light_debloat(ip, tv_type)
                    desc = "Яндекс ТВ" if tv_type == "yaos" else "Android TV / Google TV"
                    resp = {"success": True, "message": f"Легкая очистка рекламы ({desc}) выполнена! Родной лаунчер сохранен."}
                elif action == 'full_debloat':
                    tv_manager.action_full_debloat(ip, tv_type, launcher_choice)
                    desc = "Яндекс ТВ" if tv_type == "yaos" else "Android TV / Google TV"
                    resp = {"success": True, "message": f"Полный деблоат ({desc}) завершен! Активирован лаунчер {launcher_choice.upper()}."}
                elif action == 'restore':
                    tv_manager.action_restore(ip, tv_type)
                    desc = "Яндекс ТВ" if tv_type == "yaos" else "Google TV / Android TV"
                    resp = {"success": True, "message": f"Все заводские службы ({desc}) восстановлены!"}
                else:
                    resp = {"success": False, "message": "Неизвестное действие"}

            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SmartTVRequestHandler) as httpd:
        print(f"[*] Локальный сервер запущен на http://localhost:{PORT}")
        import webbrowser
        webbrowser.open(f"http://localhost:{PORT}/START_HERE.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    run()
