import json
import os

def load_secrets():
    app_path = os.path.dirname(os.path.abspath(__file__))
    secrets_folder = os.path.join(app_path, '../secrets')
    secrets_file = os.path.join(secrets_folder, 'secrets.json')
    live_secrets_folder = os.path.join(app_path, '../live-secrets')
    live_secrets_file = os.path.join(live_secrets_folder, 'secrets.json')
    
    secrets = {}
    if os.path.exists(live_secrets_file):
        with open(live_secrets_file, 'r') as f:
            secrets = json.load(f)
    elif os.path.exists(secrets_file):
        with open(secrets_file, 'r') as f:
            secrets = json.load(f)
    else:
        raise FileNotFoundError(f"Secrets file not found at {secrets_file}")
    
    # Provide default values if keys are missing
    secrets.setdefault("web-port", 5000)
    secrets.setdefault("web-server", "localhost")
    
    return secrets