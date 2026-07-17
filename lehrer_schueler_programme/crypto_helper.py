import json
from cryptography.fernet import Fernet

KEY = b'vM7D-jS6qE1HjV_3lFwz-4sJqI_3qB_9uYv7tX8yGqU='
cipher = Fernet(KEY)

def encrypt_results(results_dict, output_path):
    """Verschlüsselt ein Dictionary und speichert es als Datei."""
    json_data = json.dumps(results_dict, ensure_ascii=False).encode('utf-8')
    encrypted = cipher.encrypt(json_data)
    with open(output_path, 'wb') as f:
        f.write(encrypted)

def decrypt_results(input_path):
    """Liest eine verschlüsselte Datei und gibt das Dictionary zurück."""
    with open(input_path, 'rb') as f:
        encrypted = f.read()
    try:
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8'))
    except Exception as e:
        print("Entschlüsselungsfehler:", e)
        return None
