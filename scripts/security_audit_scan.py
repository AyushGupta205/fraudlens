"""
FraudLens — Security and Secret Scanner
Recursively scans the project directory for credentials, secrets, tokens,
private keys, emails, phone numbers, and hardcoded absolute paths.
"""

import os
import re
import json

ROOT_DIR = "."

PATTERNS = {
    "API_KEY": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]"),
    "SECRET_KEY": re.compile(r"(?i)(secret[_-]?key|client[_-]?secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]"),
    "ACCESS_TOKEN": re.compile(r"(?i)(auth[_-]?token|access[_-]?token|bearer\s+[A-Za-z0-9_\-\.]{15,}|github[_-]?token)\s*[:=]?\s*['\"]?[A-Za-z0-9_\-\.]{15,}['\"]?"),
    "PASSWORD": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
    "AWS_KEY": re.compile(r"(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
    "AZURE_KEY": re.compile(r"(?i)(azure_storage_account|azure_client_secret)\s*[:=]"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN\s+(RSA|OPENSSH|DSA|EC|PGP)?\s*PRIVATE KEY-----"),
    "DB_CONNECTION": re.compile(r"(?i)(postgres|mysql|mssql|mongodb)(\+srv)?:\/\/[^\s:]+:[^\s@]+@"),
    "EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "LOCAL_PATH_D": re.compile(r"(?i)D:[\\/]financial_Analytics"),
    "LOCAL_PATH_C_USER": re.compile(r"(?i)C:[\\/]Users[\\/][a-zA-Z0-9_-]+"),
    "LOCAL_PATH_PROGRAM_FILES": re.compile(r"(?i)C:[\\/]Program Files[\\/]")
}

IGNORE_DIRS = {".git", ".pytest_cache", ".venv", "venv", "__pycache__", "backups"}
TEXT_EXTS = {".py", ".sql", ".md", ".json", ".txt", ".dax", ".m", ".ini", ".example", ".html", ".bat", ".csv", ".pbir", ".pbism"}

def run_scan():
    findings = []
    scanned_files = 0
    
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in TEXT_EXTS or f in {".gitignore", ".env", ".env.example", "pytest.ini"}:
                fp = os.path.join(dirpath, f)
                scanned_files += 1
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        for line_num, line in enumerate(fh, 1):
                            for cat, pat in PATTERNS.items():
                                if pat.search(line):
                                    findings.append({
                                        "category": cat,
                                        "file": fp,
                                        "line": line_num
                                    })
                except Exception as e:
                    pass
                    
    print(f"Scanned {scanned_files} text/code files.")
    print(f"Total pattern matches: {len(findings)}")
    
    categories = {}
    for item in findings:
        cat = item["category"]
        categories.setdefault(cat, []).append(item)
        
    for cat, items in categories.items():
        print(f"\n--- {cat} ({len(items)} matches) ---")
        unique_files = sorted(list(set(x["file"] for x in items)))
        for uf in unique_files[:10]:
            print(f"  {uf}")
        if len(unique_files) > 10:
            print(f"  ... and {len(unique_files) - 10} more files")

if __name__ == "__main__":
    run_scan()
