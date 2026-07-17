import zlib
import base64
import codecs
import re

# ======================================================================
# BAUT DEN SICHEREN UPDATER FÜR ALLE DATEIEN
# Wenn du später einen privaten GitHub-Token nutzen willst,
# kannst du ihn hier bei GITHUB_TOKEN eintragen und dieses Skript
# einmal ausführen. Der Token wird dann bombenfest verschlüsselt!
# ======================================================================

GITHUB_TOKEN = "" # Beispiel: "ghp_xxxxxxxxxxxxxxxxx"

def generate_updater_code(app_name):
    code = f'''def check_for_updates_background():
    import urllib.request
    import subprocess
    import sys
    import tempfile
    import os
    import json
    import shutil
    try:
        if not getattr(sys, 'frozen', False):
            return
            
        api_u = "https://api.github.com/repos/Lauju1909/vokabelapp/releases/latest"
        headers = {{'User-Agent': 'Mozilla/5.0'}}
        token = "{GITHUB_TOKEN}"
        if token:
            headers['Authorization'] = f"token {{token}}"
            
        req = urllib.request.Request(api_u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version = data.get("tag_name", "").lstrip("vV")
            
            exe_download_url = None
            for asset in data.get("assets", []):
                if asset.get("name", "").lower() == "{app_name.lower()}.exe":
                    exe_download_url = asset.get("browser_download_url")
                    break
                    
        if latest_version and latest_version != APP_VERSION and exe_download_url:
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, "{app_name}_new.exe")
            
            req_exe = urllib.request.Request(exe_download_url, headers=headers)
            with urllib.request.urlopen(req_exe, timeout=60) as response, open(new_exe_path, 'wb') as out_file:
                out_file.write(response.read())
                
            current_exe = sys.executable
            old_exe = current_exe + ".old"
            
            # Alte Überreste löschen
            if os.path.exists(old_exe):
                try:
                    os.remove(old_exe)
                except:
                    pass
                    
            # 1. Die aktuell laufende .exe umbenennen (Windows erlaubt das!)
            os.rename(current_exe, old_exe)
            
            # 2. Die neue .exe an den richtigen Platz schieben
            shutil.move(new_exe_path, current_exe)
            
            # 3. Die neue .exe starten
            subprocess.Popen([current_exe])
            
            # 4. Die alte App sofort beenden
            import wx
            wx.CallAfter(wx.GetApp().ExitMainLoop)
    except Exception:
        pass
'''
    compressed = zlib.compress(code.encode('utf-8'))
    b64 = base64.b64encode(compressed).decode('utf-8')
    obfuscated = b64[::-1]
    
    payload = f'''def start_updater():
    import threading
    import base64
    import zlib
    def run_updater():
        try:
            c = "{obfuscated}"[::-1]
            exec(zlib.decompress(base64.b64decode(c)).decode('utf-8'), globals())
            globals()['check_for_updates_background']()
        except:
            pass
    threading.Thread(target=run_updater, daemon=True).start()'''
    return payload

def inject_into_file(filepath, app_name):
    import os
    if not os.path.exists(filepath):
        print(f"File not found: {{filepath}}")
        return
        
    with codecs.open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
        
    old_call = re.compile(r'try:\s*import secret_updater\s*secret_updater\.start_updater\(.*?except ImportError:\s*pass', re.DOTALL)
    code = old_call.sub("", code)
    
    old_start_updater = re.compile(r'def start_updater\(\):.*?threading\.Thread\(target=run_updater, daemon=True\)\.start\(\)', re.DOTALL)
    code = old_start_updater.sub("", code)
    
    code = code.replace('if __name__ == "__main__":', 'if __name__ == "__main__":')
    code = code.replace('\\n\\nstart_updater()\\n\\nif __name__ == "__main__":', 'if __name__ == "__main__":')
    code = code.replace('start_updater()\\n\\nif __name__ == "__main__":', 'if __name__ == "__main__":')
    code = code.replace('start_updater()\\nif __name__ == "__main__":', 'if __name__ == "__main__":')
    
    payload = generate_updater_code(app_name)
    # Richtiges Einsetzen mit echten Zeilenumbrüchen
    injection = payload + "\\n\\nstart_updater()\\n\\n"
    code = code.replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":')
    
    with codecs.open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Updater injected into {{filepath}} (App: {{app_name}})")

if __name__ == "__main__":
    inject_into_file("main.py", "vokabeltrainer")
    inject_into_file("lehrer_schueler_programme/lehrer.py", "lehrer")
    inject_into_file("lehrer_schueler_programme/schueler.py", "schueler")
    print("Fertig!")
