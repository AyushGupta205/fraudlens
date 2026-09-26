import os
import re
import subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=root, capture_output=True, text=True)
files_to_check = []
for line in res.stdout.splitlines():
    if line.strip():
        path = line[3:].strip().strip('"')
        files_to_check.append(path)

patterns = {
    "AWS_KEY": re.compile(r"AKIA[0-9A-Z]{16}"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    "GENERIC_SECRET": re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    "HARDCODED_USERNAME": re.compile(r"(?i)ayush"),
    "HARDCODED_DRIVE_PATH": re.compile(r"[dD]:[\\/][a-zA-Z0-9_-]+"),
    "DATABASE_PASSWORD": re.compile(r"(?i)(postgres|mysql|mongodb|sqlite)://[^:]+:[^@]+@")
}

findings = []
for path in files_to_check:
    full_path = os.path.join(root, path)
    if not os.path.isfile(full_path):
        continue
    # skip binary or media extensions
    ext = os.path.splitext(full_path)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".pbix", ".joblib", ".parquet", ".db", ".sqlite", ".zip"]:
        continue
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                for p_name, pat in patterns.items():
                    if pat.search(line):
                        findings.append((path, line_no, p_name))
    except (UnicodeDecodeError, PermissionError):
        continue

print(f"Total candidate files checked: {len(files_to_check)}")
print(f"Total findings: {len(findings)}")
for path, line_no, p_name in findings:
    print(f"{path} -> Line {line_no} -> {p_name}")
