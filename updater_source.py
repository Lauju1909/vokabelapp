# Dies ist der Klartext-Code für den Updater.
# Er wird in main.py verschlüsselt ausgeführt, damit Schüler ihn nicht lesen können.

def check_for_updates_background():
    import urllib.request
    import subprocess
    import sys
    import tempfile
    import os
    import json
    import base64
    try:
        if not getattr(sys, 'frozen', False):
            return
            
        api_u = base64.b64decode("aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9MYXVqdTE5MDkvdm9rYWJlbGFwcC9yZWxlYXNlcy9sYXRlc3Q=".encode('utf-8')).decode('utf-8')
        
        req = urllib.request.Request(api_u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version = data.get("tag_name", "").lstrip("vV")
            
            exe_download_url = None
            for asset in data.get("assets", []):
                if asset.get("name", "").endswith(".exe"):
                    exe_download_url = asset.get("browser_download_url")
                    break
                    
        # APP_VERSION is available from main.py global scope
        if latest_version and latest_version != APP_VERSION and exe_download_url:
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, "vokabeltrainer_new.exe")
            
            req_exe = urllib.request.Request(exe_download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_exe, timeout=60) as response, open(new_exe_path, 'wb') as out_file:
                out_file.write(response.read())
                
            bat_path = os.path.join(temp_dir, "update.bat")
            current_exe = sys.executable
                
            bat_content = f'''@echo off\nping 127.0.0.1 -n 3 > nul\nmove /Y "{new_exe_path}" "{current_exe}"\nstart "" "{current_exe}"\ndel "%~f0"\n'''
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
                
            import wx
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(bat_path, startupinfo=startupinfo)
            wx.CallAfter(wx.GetApp().ExitMainLoop)
    except Exception:
        pass
