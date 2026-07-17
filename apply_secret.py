import re
import codecs

# 1. Update main.py
with codecs.open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Pattern to remove the obfuscator block
updater_pattern = re.compile(r'def start_updater\(\):.*?threading\.Thread\(target=run_obfuscated, daemon=True\)\.start\(\)', re.DOTALL)

# Also remove the `start_updater()` call at the bottom if it's there
main_code = main_code.replace("start_updater()\n\nif __name__", "if __name__")

new_updater_call = """try:
    import secret_updater
    secret_updater.start_updater("vokabeltrainer", APP_VERSION)
except ImportError:
    pass
"""

main_code = updater_pattern.sub("", main_code)
# insert the new call before `if __name__ == "__main__":`
main_code = main_code.replace('if __name__ == "__main__":', new_updater_call + '\nif __name__ == "__main__":')

with codecs.open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# 2. Update lehrer.py
def update_sub_app(filename, app_name):
    import os
    filepath = os.path.join("lehrer_schueler_programme", filename)
    if not os.path.exists(filepath):
        return
        
    with codecs.open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
        
    # Inject APP_VERSION and updater call if not there
    if "import secret_updater" not in code:
        version_str = "APP_VERSION = '1.0.0'\n"
        updater_str = f'''
try:
    import secret_updater
    secret_updater.start_updater("{app_name}", APP_VERSION)
except ImportError:
    pass
'''
        # Add right before `if __name__ == "__main__":`
        if 'if __name__ == "__main__":' in code:
            code = code.replace('if __name__ == "__main__":', version_str + updater_str + '\nif __name__ == "__main__":')
        else:
            code += "\n" + version_str + updater_str
            
        with codecs.open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

update_sub_app("lehrer.py", "lehrer")
update_sub_app("schueler.py", "schueler")

print("Secret updater applied to all apps.")
