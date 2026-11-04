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
            
            apps_dir = os.path.join(DIRECTORY, "apps")
            apps_list = []
            if os.path.exists(apps_dir):
                for f in sorted(os.listdir(apps_dir)):
                    if f.lower().endswith(".apk"):
                        full_p = os.path.join(apps_dir, f)
                        size_mb = round(os.path.getsize(full_p) / (1024 * 1024), 1)
                        apps_list.append({"filename": f, "size_mb": size_mb})
            
            self.wfile.write(json.dumps({"success": True, "apps": apps_list}, ensure_ascii=False).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/test_connection':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
            req_data = json.loads(body) if body else {}
            manual_ip = req_data.get('ip')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            # Run test logic
            ip = tv_manager.connect_adb(manual_ip)
            if not ip:
                resp = {
                    "success": False,
                    "message": "Не удалось обнаружить телевизор или порт 5555 закрыт.",
                    "details": "Убедитесь, что телевизор включен, подключен к тому же Wi-Fi, и в Factory Menu включен пункт ADB -> ON."
                }
            else:
                try:
                    model = tv_manager.adb_shell(ip, "getprop ro.product.model")
                    brand = tv_manager.adb_shell(ip, "getprop ro.product.brand")
                    android_v = tv_manager.adb_shell(ip, "getprop ro.build.version.release")
                    launcher = tv_manager.adb_shell(ip, "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME")
                    cur_launcher = launcher.splitlines()[-1] if launcher else "Стандартный"
                    resp = {
                        "success": True,
                        "ip": ip,
                        "brand": brand,
                        "model": model,
                        "android": android_v,
                        "launcher": cur_launcher,
                        "message": "Связь с телевизором успешно установлена!"
                    }
                except Exception as e:
                    resp = {"success": False, "message": f"Ошибка связи: {e}"}
            
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        elif parsed.path == '/api/run_action':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            action = data.get('action')
            manual_ip = data.get('ip')
            apks = data.get('apks') or data.get('apps_list') or data.get('preset')
            
            ip = tv_manager.connect_adb(manual_ip)
            if not ip:
                resp = {"success": False, "message": "Нет связи с телевизором по ADB!"}
            else:
                if action == 'install':
                    tv_manager.action_install_apps(ip, apks or "top6")
                    resp = {"success": True, "message": "Подгрузка приложений успешно завершена!"}
                elif action == 'light_debloat':
                    tv_manager.action_light_debloat(ip)
                    resp = {"success": True, "message": "Легкая очистка рекламы выполнена! Родной лаунчер сохранен."}
                elif action == 'full_debloat':
                    tv_manager.action_full_debloat(ip)
                    resp = {"success": True, "message": "Полный деблоат завершен! Активирован FLauncher."}
                elif action == 'restore':
                    tv_manager.action_restore(ip)
                    resp = {"success": True, "message": "Все заводские службы Яндекса восстановлены!"}
                else:
                    resp = {"success": False, "message": "Неизвестное действие"}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
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
