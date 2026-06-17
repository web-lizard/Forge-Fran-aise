from pathlib import Path
import json

root = Path(r"D:\PYTHON\Forge Francaise")

# 1. Strip BOM from common frontend/project text files
patterns = [
    "frontend/**/*.json",
    "frontend/**/*.ts",
    "frontend/**/*.vue",
    "frontend/**/*.css",
    "frontend/**/*.html",
    "*.json",
    ".vscode/*.json",
]

changed = []

for pattern in patterns:
    for path in root.glob(pattern):
        if not path.is_file():
            continue

        data = path.read_bytes()

        if data.startswith(b"\xef\xbb\xbf"):
            path.write_bytes(data[3:])
            changed.append(str(path.relative_to(root)))

# 2. Rewrite package.json as clean UTF-8 without BOM
package_path = root / "frontend" / "package.json"

package = {
    "name": "forge-francaise",
    "private": True,
    "version": "0.6.2",
    "type": "module",
    "scripts": {
        "dev": "vite --host 127.0.0.1 --port 5197",
        "build": "vue-tsc --noEmit && vite build",
        "preview": "vite preview --host 127.0.0.1 --port 4197"
    },
    "dependencies": {
        "pinia": "^2.1.7",
        "vue": "^3.4.0",
        "vue-router": "^4.3.0"
    },
    "devDependencies": {
        "@vitejs/plugin-vue": "^5.0.5",
        "typescript": "^5.4.0",
        "vite": "^5.2.0",
        "vue-tsc": "^2.0.0"
    }
}

package_path.write_text(
    json.dumps(package, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

# 3. Make sure vite config is clean and Vue plugin is called
vite_config = """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5197,
  },
  preview: {
    host: '127.0.0.1',
    port: 4197,
  },
})
"""

(root / "frontend" / "vite.config.ts").write_text(vite_config, encoding="utf-8")

print("BOM stripped from:")
for item in changed:
    print("-", item)

print("package.json and vite.config.ts rewritten without BOM")
