import json
from django.conf import settings
from django.templatetags.static import static
from pathlib import Path

def get_vite_asset(asset_name):
    try:
        # ✅ Updated manifest path to match your actual directory structure
        manifest_path = Path(settings.BASE_DIR) / 'static' / 'dist' / '.vite' / 'manifest.json'
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        file_info = manifest.get(asset_name)
        if file_info:
            return {
                'js': static('dist/' + file_info.get('file', '')),
                'css': [static('dist/' + css) for css in file_info.get('css', [])] if 'css' in file_info else []
            }
    except Exception as e:
        print(f"[VITE ERROR] {e}")
    return {'js': '', 'css': []}
