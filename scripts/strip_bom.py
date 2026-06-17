from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    "frontend/**/*.json",
    "frontend/**/*.ts",
    "frontend/**/*.vue",
    "frontend/**/*.css",
    "frontend/**/*.html",
    "backend/**/*.py",
    "content/**/*.json",
    ".vscode/*.json",
    "*.json",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed = []

    for pattern in PATTERNS:
        for path in ROOT.glob(pattern):
            if not path.is_file():
                continue

            data = path.read_bytes()

            if data.startswith(b"\xef\xbb\xbf"):
                changed.append(path.relative_to(ROOT).as_posix())

                if not args.check:
                    path.write_bytes(data[3:])

    if changed:
        print("BOM found:")
        for item in changed:
            print(f"- {item}")

        if args.check:
            raise SystemExit(1)

        print("BOM stripped.")
    else:
        print("BOM check passed.")


if __name__ == "__main__":
    main()
