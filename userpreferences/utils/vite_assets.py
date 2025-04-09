import json
import os
from django.conf import settings

def get_vite_asset(entry_file):
    manifest_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'manifest.json')
    if not os.path.exists(manifest_path):
        return {'js': '', 'css': ''}

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    entry = manifest.get(entry_file, {})
    js = f"/static/assets/{entry.get('file', '')}"
    css = [f"/static/assets/{css_file}" for css_file in entry.get('css', [])]

    return {'js': js, 'css': css}
